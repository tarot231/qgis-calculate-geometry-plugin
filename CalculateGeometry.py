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

try:
    from PyQt4.QtGui import QAction
except:
    from PyQt5.QtWidgets import QAction
from qgis.core import *
from CalculateGeometryDialog import CalculateGeometryDialog


try:
    qgis_version = QGis.QGIS_VERSION_INT
except:
    qgis_version = Qgis.QGIS_VERSION_INT

AreaUnit = ['Square Meters', 'Square Kilometers', 'Square Feet',
            'Square Yards', 'Square Miles', 'Hectares',
            'Acres', 'Square Nautical Miles']
if qgis_version >= 29900:
    DistanceUnit = ['Meters', 'Kilometers', 'Feet',
                    'Nautical Miles', 'Yards', 'Miles',
                    None, 'Centimeters', 'Millimeters']
elif qgis_version >= 21600:
    DistanceUnit = ['Meters', 'Feet', None, None, None, None, None,
                    'Nautical Miles', 'Kilometers', 'Yards', 'Miles']
else:
    DistanceUnit = ['Meters', 'Feet', None, None, None, None, None,
                    'Nautical Miles']


class CalculateGeometry:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.dialog = CalculateGeometryDialog()

        self.action = QAction(u'Calculate Geometry...',
                self.iface.legendInterface())
        self.action.triggered.connect(self.run)

        self.iface.legendInterface().addLegendLayerAction(
                self.action, None, 'CalculateGeometry',
                QgsMapLayer.VectorLayer, True)

    def unload(self):
        self.iface.legendInterface().removeLegendLayerAction(
                self.action)

    def run(self):
        self.dialog.comboBox_property.clear()
        self.dialog.comboBox_field.clear()
        self.dialog.comboBox_units.clear()

        layer = self.iface.legendInterface().currentLayer()
        if layer.geometryType() == QGis.Point:
            iface.messageBar().pushWarning(
                    'Warning', 'Point is not supported')
            return
        elif layer.geometryType() == QGis.Line:
            self.dialog.comboBox_property.addItems(['Length'])
            self.dialog.comboBox_units.addItems(
                    [x for x in DistanceUnit if x is not None])
        elif layer.geometryType() == QGis.Polygon:
            self.dialog.comboBox_property.addItems(['Area'])#, 'Perimeter'])
            self.dialog.comboBox_units.addItems(AreaUnit)
        else:
            iface.messageBar().pushWarning(
                    'Warning', 'Unknown geometry type')
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
            editable = layer.isEditable()

            if not editable:
                layer.startEditing()
            for feat in layer.getFeatures():
                if property == 'Area':
                    res = da.measureArea(feat.geometry())
                    res = da.convertAreaMeasurement(res, AreaUnit.index(units))
                elif property == 'Perimeter':
                    res = da.measurePerimeter(feat.geometry())
                    res = da.convertLengthMeasurement(res, DistanceUnit.index(units))
                elif property == 'Length':
                    res = da.measureLength(feat.geometry())
                    res = da.convertLengthMeasurement(res, DistanceUnit.index(units))
                else:
                    iface.messageBar().pushWarning(
                            'Warning', '%s property is not supported' % property)
                feat[field] = res
                layer.updateFeature(feat)
            if not editable:
                layer.commitChanges()


if __name__ == "__main__":
    pass
