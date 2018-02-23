# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Calculate Geometry
                                 A QGIS plugin
 Calculate area, length
                             -------------------
        begin                : 2018-02-06
        copyright            : (C) 2018 by Tarot Osuji
        email                : tarot@sdf.lonestar.org
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
try:
    from PyQt5.QtCore import QSettings, QTranslator, QCoreApplication
    from PyQt5.QtWidgets import QAction
except:
    from PyQt4.QtCore import QSettings, QTranslator, QCoreApplication
    from PyQt4.QtGui import QAction
from qgis.core import *
from .CalculateGeometryDialog import CalculateGeometryDialog


class CalculateGeometry:
    def __init__(self, iface):
        self.iface = iface
        try:
            self.qgis_version = Qgis.QGIS_VERSION_INT
        except NameError:
            self.qgis_version = QGis.QGIS_VERSION_INT
        self.Point, self.Line, self.Polygon = ((
                QgsWkbTypes.PointGeometry,
                QgsWkbTypes.LineGeometry,
                QgsWkbTypes.PolygonGeometry) if self.qgis_version >= 29900
                else (QGis.Point, QGis.Line, QGis.Polygon))

        locale = QSettings().value('locale/userLocale')
        locale_path = os.path.join(
                os.path.dirname(__file__),
                'i18n', locale)
        self.translator = QTranslator()
        if self.translator.load(locale_path):
            QCoreApplication.installTranslator(self.translator)

    def tr(self, message):
        return QCoreApplication.translate(self.__class__.__name__, message)

    def initGui(self):
        self.dialog = CalculateGeometryDialog()
        self.dialog.comboBox_property.currentIndexChanged.connect(self.property_changed)

        self.action = QAction(self.tr('&Calculate Geometry...'),
                self.iface.mainWindow() if self.qgis_version >= 29900
                else self.iface.legendInterface())
        self.action.triggered.connect(self.run)

        if self.qgis_version >= 29900:
            self.iface.addCustomActionForLayerType(self.action,
                    None,
                    QgsMapLayer.VectorLayer, True)
        else:
            self.iface.legendInterface().addLegendLayerAction(self.action,
                    None, self.__class__.__name__,
                    QgsMapLayer.VectorLayer, True)

        self.AreaUnits = [self.tr('Square Meters'),
                          self.tr('Square Kilometers'),
                          self.tr('Square Feet'),
                          self.tr('Square Yards'),
                          self.tr('Square Miles'),
                          self.tr('Hectares'),
                          self.tr('Acres'),
                          self.tr('Square Nautical Miles'),
                          self.tr('Square Degrees')]
        if self.qgis_version >= 29900:
            self.AreaUnits += [self.tr('Square Centimeters'),
                               self.tr('Square Millimeters')]
            self.DistanceUnits = [self.tr('Meters'),
                                  self.tr('Kilometers'),
                                  self.tr('Feet'),
                                  self.tr('Nautical Miles'),
                                  self.tr('Yards'),
                                  self.tr('Miles'),
                                  self.tr('Degrees'),
                                  self.tr('Centimeters'),
                                  self.tr('Millimeters'),
                                  None]
        else:
            self.DistanceUnits = [self.tr('Meters'),
                                  self.tr('Feet'),
                                  self.tr('Degrees'), None, None, None, None,
                                  self.tr('Nautical Miles')]
            if self.qgis_version >= 21600:
                self.DistanceUnits += [self.tr('Kilometers'),
                                       self.tr('Yards'),
                                       self.tr('Miles')]
        self.AreaUnits += [None]

    def unload(self):
        if self.qgis_version >= 29900:
            self.iface.removeCustomActionForLayerType(self.action)
        else:
            self.iface.legendInterface().removeLegendLayerAction(self.action)

    def run(self):
        self.dialog.comboBox_property.clear()
        self.dialog.comboBox_field.clear()
        self.dialog.comboBox_units.clear()

        layer = (self.iface.activeLayer() if self.qgis_version >= 29900
                else self.iface.legendInterface().currentLayer())
        if layer.geometryType() == self.Point:
            self.iface.messageBar().pushWarning(
                    self.tr('Warning'), self.tr('Point is not supported'))
            return
        elif layer.geometryType() == self.Line:
            self.dialog.comboBox_property.addItems([self.tr('Length')])
        elif layer.geometryType() == self.Polygon:
            self.dialog.comboBox_property.addItems([self.tr('Area'), self.tr('Perimeter')])
        else:
            self.iface.messageBar().pushWarning(
                    self.tr('Warning'), self.tr('Unknown geometry type'))
            return
        if layer.fields().count() == 0:
            self.iface.messageBar().pushWarning(
                    self.tr('Warning'), self.tr('No fields in the layer'))
            return
        self.dialog.comboBox_field.addItems(
                [x.name() for x in layer.fields()])
        self.dialog.show()

        result = self.dialog.exec_()
        if result:
            property = self.dialog.comboBox_property.currentText()
            field = self.dialog.comboBox_field.currentText()
            units = self.dialog.comboBox_units.currentText()
            da = QgsDistanceArea()
            if self.qgis_version >= 29900:
                da.setSourceCrs(layer.crs(), QgsCoordinateTransformContext())
            else:
                da.setSourceCrs(layer.crs())

            if layer.isEditable() == False:
                layer.startEditing()
            for f in layer.getFeatures():
                if property == self.tr('Area'):
                    res = da.measureArea(f.geometry())
                    res = da.convertAreaMeasurement(res, self.AreaUnits.index(units))
                elif property == self.tr('Perimeter'):
                    res = da.measurePerimeter(f.geometry())
                    res = da.convertLengthMeasurement(res, self.DistanceUnits.index(units))
                elif property == self.tr('Length'):
                    res = da.measureLength(f.geometry())
                    res = da.convertLengthMeasurement(res, self.DistanceUnits.index(units))
                else:
                    self.iface.messageBar().pushWarning(
                            self.tr('Warning'), self.tr('{} property is not supported').format(property))
                f[field] = res
                layer.updateFeature(f)

    def property_changed(self):
        if self.dialog.comboBox_property.currentIndex() == -1:
            return
        if self.dialog.comboBox_units.currentIndex() != -1:
            if ((self.iface.activeLayer().geometryType() != self.Polygon) if self.qgis_version >= 29900
                    else (self.iface.legendInterface().currentLayer().geometryType() != self.Polygon)):
                return

        self.dialog.comboBox_units.clear()
        proj = QgsProject.instance()
        if self.dialog.comboBox_property.currentText() == self.tr('Area'):
            self.dialog.comboBox_units.addItems(self.AreaUnits[:-1])
            idx = proj.areaUnits()
            if self.AreaUnits[idx] is None:
                if self.qgis_version >= 29900:
                    idx = 8 if self.iface.mapCanvas().mapUnits() == 6 else 0
                else:
                    idx = 8 if self.iface.mapCanvas().mapUnits() == 2 else 0
            self.dialog.comboBox_units.setCurrentIndex(idx)
        else:
            self.dialog.comboBox_units.addItems(self.DistanceUnits)
            idx = proj.distanceUnits()
            if self.DistanceUnits[idx] is None:
                idx = self.iface.mapCanvas().mapUnits()
            self.dialog.comboBox_units.setCurrentIndex(idx)
            for i, v in reversed([x for x in enumerate(self.DistanceUnits)]):
                if v is None:
                    self.dialog.comboBox_units.removeItem(i)


if __name__ == "__main__":
    pass
