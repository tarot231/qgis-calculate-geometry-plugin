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
from CalculateGeometryDialog import CalculateGeometryDialog


class CalculateGeometry:
    def __init__(self, iface):
        self.iface = iface

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

        self.action = QAction(self.tr('&Calculate Geometry...'),
                self.iface.legendInterface())
        self.action.triggered.connect(self.run)

        self.iface.legendInterface().addLegendLayerAction(
                self.action, None, 'CalculateGeometry',
                QgsMapLayer.VectorLayer, True)

        try:
            qgis_version = QGis.QGIS_VERSION_INT
        except:
            qgis_version = Qgis.QGIS_VERSION_INT

        self.AreaUnit = [self.tr('Square Meters'),
                         self.tr('Square Kilometers'),
                         self.tr('Square Feet'),
                         self.tr('Square Yards'),
                         self.tr('Square Miles'),
                         self.tr('Hectares'),
                         self.tr('Acres'),
                         self.tr('Square Nautical Miles'),
                         self.tr('Square Degrees')]
        if qgis_version >= 29900:
            self.AreaUnit += [self.tr('Square Centimeters'),
                              self.tr('Square Millimeters')]
            self.DistanceUnit = [self.tr('Meters'),
                                 self.tr('Kilometers'),
                                 self.tr('Feet'),
                                 self.tr('Nautical Miles'),
                                 self.tr('Yards'),
                                 self.tr('Miles'),
                                 self.tr('Degrees'),
                                 self.tr('Centimeters'),
                                 self.tr('Millimeters')]
        else:
            self.DistanceUnit = [self.tr('Meters'),
                                 self.tr('Feet'),
                                 self.tr('Degrees'), None, None, None, None,
                                 self.tr('Nautical Miles')]
            if qgis_version >= 21600:
                self.DistanceUnit += [self.tr('Kilometers'),
                                      self.tr('Yards'),
                                      self.tr('Miles')]

    def unload(self):
        self.iface.legendInterface().removeLegendLayerAction(
                self.action)

    def run(self):
        self.dialog.comboBox_property.clear()
        self.dialog.comboBox_field.clear()
        self.dialog.comboBox_units.clear()

        layer = self.iface.legendInterface().currentLayer()
        if layer.geometryType() == QGis.Point:
            self.iface.messageBar().pushWarning(
                    self.tr('Warning'), self.tr('Point is not supported'))
            return
        elif layer.geometryType() == QGis.Line:
            self.dialog.comboBox_property.addItems([self.tr('Length')])
            self.dialog.comboBox_units.addItems(
                    [x for x in self.DistanceUnit if x is not None])
        elif layer.geometryType() == QGis.Polygon:
            self.dialog.comboBox_property.addItems([self.tr('Area')])#, self.tr('Perimeter')])
            self.dialog.comboBox_units.addItems(self.AreaUnit)
        else:
            self.iface.messageBar().pushWarning(
                    self.tr('Warning'), self.tr('Unknown geometry type'))
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
            da.setSourceCrs(layer.crs())

            if layer.isEditable() == False:
                layer.startEditing()
            for f in layer.getFeatures():
                if property == self.tr('Area'):
                    res = da.measureArea(f.geometry())
                    res = da.convertAreaMeasurement(res, self.AreaUnit.index(units))
                elif property == self.tr('Perimeter'):
                    res = da.measurePerimeter(f.geometry())
                    res = da.convertLengthMeasurement(res, self.DistanceUnit.index(units))
                elif property == self.tr('Length'):
                    res = da.measureLength(f.geometry())
                    res = da.convertLengthMeasurement(res, self.DistanceUnit.index(units))
                else:
                    self.iface.messageBar().pushWarning(
                            self.tr('Warning'), self.tr('{} property is not supported').format(property))
                f[field] = res
                layer.updateFeature(f)


if __name__ == "__main__":
    pass
