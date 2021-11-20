# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Calculate Geometry
                                 A QGIS plugin
 Calculate area, length
                             -------------------
        begin                : 2018-02-06
        copyright            : (C) 2018 by Tarot Osuji
        email                : tarot@sdf.org
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.gui import QgsProjectionSelectionWidget
from .CalculateGeometryUI import (
        CalculateGeometryDialog, distance_units, area_units)


class CalculateGeometry(QObject):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.translator = QTranslator()
        if self.translator.load(QLocale(QgsApplication.locale()),
                '', '', os.path.join(os.path.dirname(__file__), 'i18n')):
            qApp.installTranslator(self.translator)

    def initGui(self):
        self.plugin_name = self.tr('Calculate Geometry')
        self.plugin_act = QAction(self.plugin_name + '…')
        self.plugin_act.triggered.connect(self.run)
        self.iface.addCustomActionForLayerType(self.plugin_act, None,
                QgsMapLayer.VectorLayer, True)
        self.dialog = None

    def unload(self):
        self.iface.removeCustomActionForLayerType(self.plugin_act)

    def run(self):
        if self.dialog is None:
            self.dialog = CalculateGeometryDialog()
            self.dialog.checks.buttonToggled.connect(self.checks_toggled)
            self.dialog.radios.buttonClicked.connect(self.system_changed)
            self.dialog.selectorCrs.crsChanged.connect(self.system_changed)

        layer = self.iface.layerTreeView().currentLayer()
        if layer.geometryType() == QgsWkbTypes.PointGeometry:
            self.dialog.prepare_for_point(QgsWkbTypes.hasZ(layer.wkbType()),
                                          QgsWkbTypes.hasM(layer.wkbType()))
        elif layer.geometryType() == QgsWkbTypes.LineGeometry:
            self.dialog.prepare_for_line()
        elif layer.geometryType() == QgsWkbTypes.PolygonGeometry:
            self.dialog.prepare_for_polygon()
        else:
            self.iface.messageBar().pushCritical(self.plugin_name,
                    self.tr('Unsupported geometry type'))
            return
        if not layer.crs().isValid():
            self.iface.messageBar().pushCritical(self.plugin_name,
                    self.tr('Invalid CRS'))
            return
        self.dialog.selectorCrs.setLayerCrs(layer.crs())
        self.system_changed()

        fields = [x.name() for x in layer.fields()]
        for combo in (cols[1] for cols in self.dialog.rows):
            text = combo.currentText()
            combo.clear()
            combo.addItems(fields)
            combo.setCompleter(QCompleter(fields))
            combo.setEditText(text)

        ellips_defs = {d.acronym: d for d in QgsEllipsoidUtils.definitions()}
        ellips_acro = QgsProject.instance().ellipsoid()
        try:
            ellips_desc = ellips_defs[ellips_acro].description
        except KeyError:
            if ellips_acro.startswith('PARAMETER:'):
                ellips_desc = self.tr('Custom ({})').format(ellips_acro)
            else:
                ellips_desc = self.tr('None / Planimetric')
        self.dialog.labelEllips.setText(ellips_desc)
        enabled = (layer.geometryType() != QgsWkbTypes.PointGeometry)
        self.dialog.labelEllips.setEnabled(enabled)
        self.dialog.radio2.setEnabled(enabled)
        if not self.dialog.radio2.isEnabled():
            self.dialog.radio1.setChecked(True)

        self.is_selected = bool(layer.selectedFeatureCount())
        self.dialog.checkVirtual.setEnabled(True)
        self.dialog.checkSelected.setEnabled(self.is_selected)
        self.dialog.checkSelected.setChecked(self.is_selected)

        dp = layer.dataProvider()
        if not dp.capabilities() & dp.ChangeAttributeValues \
                or layer.readOnly():
            self.dialog.checkVirtual.setEnabled(False)
            self.dialog.checkVirtual.setChecked(True)

        self.dialog.reset_standard_buttons()
        self.dialog.setMinimumHeight(0)

        result = self.dialog.exec()
        if result == QDialog.Rejected:
            return

        # transform  0: layer  -1: project  1: crs
        data = self.dialog.comboCrs.currentData()
        if data == QgsProjectionSelectionWidget.LayerCrs:
            transform = 0
        elif data == QgsProjectionSelectionWidget.ProjectCrs:
            transform = -1
        else:
            transform = 1

        virtual = self.dialog.checkVirtual.isChecked()

        ########################################
        def process_exp(expstr, field_name, prec, conv_factor=1):
            if self.dialog.radio2.isChecked():
                expstr = '$' + expstr
            else:
                if transform == 0:
                    expstr += '($geometry)'
                else:
                    expstr += "(transform($geometry, " \
                                         "layer_property(@layer ,'crs'), " \
                                         "%s))" % (
                              "@project_crs" if transform == -1 else
                              "'%s'" % self.dialog.selectorCrs.crs().authid() )
                if conv_factor != 1:
                    expstr += ' * %s' % str(conv_factor)
            if prec is not None:
                expstr = 'round(%s, %d)' % (expstr, prec)

            idx = layer.fields().indexOf(field_name)
            if idx == -1:
                if virtual:
                    layer.addExpressionField(expstr,
                            QgsField(field_name, QVariant.Double))
                    return
                else:
                    layer.startEditing()
                    layer.addAttribute(QgsField(field_name, QVariant.Double))
                    idx = layer.fields().indexOf(field_name)

            if layer.fields().fieldOrigin(idx) == QgsFields.OriginExpression:
                layer.updateExpressionField(idx, expstr)
                return

            if layer.fields().fieldOrigin(idx) in (
                    QgsFields.OriginProvider, QgsFields.OriginEdit):
                layer.startEditing()
                context = QgsExpressionContext(
                        QgsExpressionContextUtils.globalProjectLayerScopes(layer))
                features = (layer.selectedFeatures()
                            if self.dialog.checkSelected.isChecked() else
                            layer.getFeatures())
                for f in features:
                    context.setFeature(f)
                    res = layer.changeAttributeValue(f.id(), idx,
                            QgsExpression(expstr).evaluate(context))
                if res:
                    return

            self.iface.messageBar().pushWarning(self.plugin_name,
                    self.tr('Actual field "{}" could not be processed')
                            .format(field_name))
        ########################################

        def get_prec(lineedit):
            text = lineedit.text()
            try:
                prec = int(text)
                lineedit.setText(str(prec))
            except ValueError:
                lineedit.clear()
                prec = None
            return prec

        if layer.geometryType() == QgsWkbTypes.PointGeometry:
            row = self.dialog.rowXcoord
            if row[0].isChecked() and row[1].currentText():
                process_exp('x', row[1].currentText(), get_prec(row[3]))
            row = self.dialog.rowYcoord
            if row[0].isChecked() and row[1].currentText():
                process_exp('y', row[1].currentText(), get_prec(row[3]))
            if QgsWkbTypes.hasZ(layer.wkbType()):
                row = self.dialog.rowZcoord
                if row[0].isChecked() and row[1].currentText():
                    process_exp('z', row[1].currentText(), get_prec(row[3]))
            if QgsWkbTypes.hasM(layer.wkbType()):
                row = self.dialog.rowMvalue
                if row[0].isChecked() and row[1].currentText():
                    process_exp('m', row[1].currentText(), get_prec(row[3]))
        else:
            du = layer.sourceCrs().mapUnits()
            if layer.geometryType() == QgsWkbTypes.LineGeometry:
                row = self.dialog.rowLength
                if row[0].isChecked() and row[1].currentText():
                    conv_factor = QgsUnitTypes.fromUnitToUnitFactor(
                            du, row[2].currentData())
                    process_exp('length', row[1].currentText(),
                            get_prec(row[3]), conv_factor)
            elif layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                row = self.dialog.rowArea
                if row[0].isChecked() and row[1].currentText():
                    au = QgsUnitTypes.distanceToAreaUnit(du)
                    conv_factor = QgsUnitTypes.fromUnitToUnitFactor(
                            au, row[2].currentData())
                    process_exp('area', row[1].currentText(),
                            get_prec(row[3]), conv_factor)
                row = self.dialog.rowPerimeter
                if row[0].isChecked() and row[1].currentText():
                    conv_factor = QgsUnitTypes.fromUnitToUnitFactor(
                            du, row[2].currentData())
                    process_exp('perimeter', row[1].currentText(),
                            get_prec(row[3]), conv_factor)

        self.iface.actionDraw().trigger()

    def checks_toggled(self, button, checked):
        for b in self.dialog.checks.buttons():
            if not b is button:
                if checked:
                    b.setEnabled(False)
                    b.setChecked(False)
                elif self.is_selected:
                    b.setEnabled(True)

    def system_changed(self):
        if self.dialog.rowXcoord[2].isVisibleTo(self.dialog):
            unit = self.dialog.selectorCrs.crs().mapUnits()
            self.dialog.rowXcoord[2].setText(
                    QgsUnitTypes.toString(unit).title())
            self.dialog.rowYcoord[2].setText(
                    QgsUnitTypes.toString(unit).title())
        else:
            if self.dialog.radio2.isChecked():
                project = QgsProject.instance()
                du = distance_units.index(project.distanceUnits())
                au = area_units.index(project.areaUnits())
                self.dialog.rowLength[2].setCurrentIndex(du)
                self.dialog.rowArea[2].setCurrentIndex(au)
                self.dialog.rowPerimeter[2].setCurrentIndex(du)
            for w in (self.dialog.rowLength,
                      self.dialog.rowArea,
                      self.dialog.rowPerimeter,):
                w[2].setEnabled(not self.dialog.radio2.isChecked())
