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
from qgis.PyQt.QtGui import QFont, QFontMetrics
from qgis.PyQt.QtWidgets import *
from qgis.core import QgsUnitTypes, QgsCoordinateReferenceSystem
from qgis.gui import QgsProjectionSelectionWidget


distance_units = (QgsUnitTypes.DistanceMeters,
                  QgsUnitTypes.DistanceKilometers,
                  QgsUnitTypes.DistanceFeet,
                  QgsUnitTypes.DistanceYards,
                  QgsUnitTypes.DistanceMiles,
                  QgsUnitTypes.DistanceNauticalMiles,
                  QgsUnitTypes.DistanceCentimeters,
                  QgsUnitTypes.DistanceMillimeters,
                  QgsUnitTypes.DistanceDegrees,
                  QgsUnitTypes.DistanceUnknownUnit,)
area_units     = (QgsUnitTypes.AreaSquareMeters,
                  QgsUnitTypes.AreaSquareKilometers,
                  QgsUnitTypes.AreaSquareFeet,
                  QgsUnitTypes.AreaSquareYards,
                  QgsUnitTypes.AreaSquareMiles,
                  QgsUnitTypes.AreaHectares,
                  QgsUnitTypes.AreaAcres,
                  QgsUnitTypes.AreaSquareNauticalMiles,
                  QgsUnitTypes.AreaSquareCentimeters,
                  QgsUnitTypes.AreaSquareMillimeters,
                  QgsUnitTypes.AreaSquareDegrees,
                  QgsUnitTypes.AreaUnknownUnit,)


class FramedLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)


class ExclusiveGroup(QButtonGroup):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setExclusive(False)
        self.buttonClicked.connect(self.clicked)

    def clicked(self, button):
        for b in self.buttons():
            if not b is button:
                b.setEnabled(not button.isChecked())


class CalculateGeometryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        cols = lambda cx, lx: (QCheckBox(cx), QLineEdit(lx), FramedLabel())

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

        cols = lambda cx, lx: (QCheckBox(cx), QLineEdit(lx), QComboBox())

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
        self.rows = (self.rowXcoord,
                     self.rowYcoord,
                     self.rowZcoord,
                     self.rowMvalue,
                     self.rowLength,
                     self.rowArea,
                     self.rowPerimeter,)
        for row, w in enumerate(self.rows):
            w[0].setChecked(True)
            for col in range(3):
                grid.addWidget(w[col], row + 1, col)
        for col in range(3):
            grid.setColumnStretch(col, 1)

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

        self.selectorCrs = QgsProjectionSelectionWidget()
        self.selectorCrs.setMinimumWidth(QFontMetrics(QFont()).height() * 28)
        self.selectorCrs.setOptionVisible(
                QgsProjectionSelectionWidget.CurrentCrs, False)
        self.selectorCrs.setLayerCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
        self.comboCrs = self.selectorCrs.layout().itemAt(0).widget()
        self.comboCrs.setCurrentIndex(
                self.comboCrs.findData(QgsProjectionSelectionWidget.LayerCrs))
        self.labelEllips = FramedLabel()

        grid = QGridLayout()
        grid.addWidget(self.radio1, 0, 0, 1, 0)
        grid.addWidget(self.selectorCrs, 1, 1)
        grid.addWidget(self.radio2, 2, 0, 1, 0)
        grid.addWidget(self.labelEllips, 3, 1)
        grid.setColumnMinimumWidth(0, QRadioButton().sizeHint().width())
        grid.setRowMinimumHeight(3, QLineEdit().sizeHint().height())

        groupSystem = QGroupBox(self.tr('Calculation System'))
        groupSystem.setLayout(grid)

        self.checkSelected = QCheckBox(self.tr('Selected features only'))
        self.checkVirtual = QCheckBox(self.tr('Create virtual field'))
        self.checks = ExclusiveGroup()
        self.checks.addButton(self.checkSelected)
        self.checks.addButton(self.checkVirtual)

        form = QFormLayout()
        form.addRow(groupProp)
        form.addRow(groupSystem)
        form.addRow(self.checkSelected)
        form.addRow(self.checkVirtual)

        self.buttonBox = QDialogButtonBox(
                accepted=self.accept, rejected=self.reject)

        vbox = QVBoxLayout()
        vbox.addLayout(form)
        vbox.addWidget(self.buttonBox)

        self.setLayout(vbox)
        self.setMaximumSize(QWIDGETSIZE_MAX, 0)
        self.setWindowTitle(self.tr('Calculate Geometry'))

    def reset_standard_buttons(self):
        self.buttonBox.clear()
        self.buttonBox.setStandardButtons(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

    def prepare_rows(self, rows):
        for row in self.rows:
            for col in range(3):
                row[col].hide()
        for row in rows:
            for col in range(3):
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
