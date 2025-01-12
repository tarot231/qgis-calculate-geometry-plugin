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

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIntValidator
from qgis.PyQt.QtWidgets import *
from qgis.core import QgsUnitTypes
from qgis.gui import QgsProjectionSelectionWidget, QgsFilterLineEdit
if __package__:
    from .units import distance_units, area_units
else:
    from units import distance_units, area_units


class FramedLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)


class EditableComboBox(QComboBox):
    def __init__(self, text):
        super().__init__()

        self.setEditable(True)
        self.setEditText(text)


class PrecisionEdit(QgsFilterLineEdit):
    def __init__(self):
        super().__init__()

        self.setValidator(QIntValidator(-9, 9, self))


class CalculateGeometryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.adjustSize()
        self.base_width = self.fontInfo().pixelSize() * 4

        cols = lambda cx, lx: \
                (QCheckBox(cx), EditableComboBox(lx),
                 FramedLabel(), PrecisionEdit())

        self.rowXcoord = cols(self.tr('X Coordinate'), 'xcoord')
        self.rowYcoord = cols(self.tr('Y Coordinate'), 'ycoord')
        self.rowZcoord = cols(self.tr('Z Coordinate'), 'zcoord')
        self.rowMvalue = cols(self.tr('M Value'), 'mvalue')
        unit = QgsUnitTypes.DistanceDegrees
        self.rowXcoord[2].setText(QgsUnitTypes.toString(unit).title())
        self.rowYcoord[2].setText(QgsUnitTypes.toString(unit).title())
        unit = QgsUnitTypes.DistanceMeters
        self.rowZcoord[2].setText(QgsUnitTypes.toString(unit).title())
        self.rowMvalue[2].setText(QgsUnitTypes.toString(unit).title())

        cols = lambda cx, lx: \
                (QCheckBox(cx), EditableComboBox(lx),
                 QComboBox(), PrecisionEdit())

        self.rowLength = cols(self.tr('Length'), 'length')
        for unit in distance_units:
            self.rowLength[2].addItem(QgsUnitTypes.toString(unit).title(), unit)
        self.rowLength[2].setItemText(self.rowLength[2].count() - 1,
                                      self.tr('Map Units'))
        self.rowArea = cols(self.tr('Area'), 'area')
        for unit in area_units:
            self.rowArea[2].addItem(QgsUnitTypes.toString(unit).title(), unit)
        self.rowArea[2].setItemText(self.rowArea[2].count() - 1,
                                    self.tr('Map Units'))
        self.rowPerimeter = cols(self.tr('Perimeter'), 'perimeter')
        for i in range(self.rowLength[2].count()):
            self.rowPerimeter[2].addItem(self.rowLength[2].itemText(i),
                                         self.rowLength[2].itemData(i))

        grid = QGridLayout()
        grid.addWidget(QLabel(self.tr('Field')), 0, 1)
        grid.addWidget(QLabel(self.tr('Units')), 0, 2)
        grid.addWidget(QLabel(self.tr('Precision')), 0, 3)
        self.rows = (self.rowXcoord,
                     self.rowYcoord,
                     self.rowZcoord,
                     self.rowMvalue,
                     self.rowLength,
                     self.rowArea,
                     self.rowPerimeter,)
        for row, w in enumerate(self.rows):
            w[0].setChecked(True)
            w[1].setMinimumWidth(self.base_width * 2)
            w[3].setMinimumWidth(self.base_width)
            for col in range(len(w)):
                grid.addWidget(w[col], row + 1, col)
        for col, factor in enumerate((0, 10000, 10000, 1)):
            grid.setColumnStretch(col, factor)

        groupProp = QGroupBox(self.tr('Properties'))
        groupProp.setLayout(grid)

        self.radio1 = QRadioButton(
                self.tr('Cartesian calculation with following CRS'))
        self.radio1.setChecked(True)
        self.radio2 = QRadioButton(
                self.tr('Ellipsoidal calculation with following ellipsoid'))
        self.radios = QButtonGroup()
        self.radios.addButton(self.radio1)
        self.radios.addButton(self.radio2)

        self.labelEllips = FramedLabel()

        self.grid = QGridLayout()
        self.grid.addWidget(self.radio1, 0, 0, 1, 0)
        #self.grid.addWidget(self.selectorCrs, 1, 1)
        self.grid.addWidget(self.radio2, 2, 0, 1, 0)
        self.grid.addWidget(self.labelEllips, 3, 1)
        self.grid.setColumnMinimumWidth(0, QRadioButton().sizeHint().width())
        self.grid.setRowMinimumHeight(3, QLineEdit().sizeHint().height())

        groupSystem = QGroupBox(self.tr('Calculation System'))
        groupSystem.setLayout(self.grid)

        self.checkSelected = QCheckBox(self.tr('Selected features only'))
        self.checkDefault = QCheckBox(self.tr('Set expression to default value'))
        self.checkVirtual = QCheckBox(self.tr('Use virtual field for new field'))
        self.checks = QButtonGroup()
        self.checks.setExclusive(False)
        self.checks.addButton(self.checkSelected)
        self.checks.addButton(self.checkDefault)
        self.checks.addButton(self.checkVirtual)

        form = QFormLayout()
        form.addRow(groupProp)
        form.addRow(groupSystem)
        form.addRow(self.checkSelected)
        form.addRow(self.checkDefault)
        form.addRow(self.checkVirtual)

        self.buttonBox = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                accepted=self.accept, rejected=self.reject)

        vbox = QVBoxLayout()
        vbox.addLayout(form)
        vbox.addWidget(self.buttonBox)

        self.setLayout(vbox)
        self.setMaximumSize(QWIDGETSIZE_MAX, 0)

    def prepare_rows(self, rows):
        for row in self.rows:
            for col in range(len(row)):
                row[col].hide()
        for row in rows:
            for col in range(len(row)):
                row[col].show()

    def prepare_for_point(self, hasZ=True, hasM=True):
        rows = [self.rowXcoord, self.rowYcoord]
        if hasZ:
            rows += [self.rowZcoord]
        if hasM:
            rows += [self.rowMvalue]
        self.prepare_rows(rows)

    def prepare_for_line(self):
        self.prepare_rows([self.rowLength])

    def prepare_for_polygon(self):
        self.prepare_rows([self.rowArea, self.rowPerimeter])

    def get_crs(self):
        return self.selectorCrs.crs()

    def reset_crs(self, crs=None):
        self.selectorCrs = QgsProjectionSelectionWidget()
        self.selectorCrs.setMinimumWidth(self.base_width * 8)
        self.grid.addWidget(self.selectorCrs, 1, 1)
        if crs:
            self.selectorCrs.setCrs(crs)


if __name__ == '__main__':
    app = QApplication([])
    w = CalculateGeometryDialog()
    w.reset_crs()
    w.exec()
