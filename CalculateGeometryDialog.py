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

from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import QFontMetrics
from qgis.gui import QgsProjectionSelectionWidget


class CalculateGeometryDialog(QDialog):
    def __init__(self, parent=None):
        super(CalculateGeometryDialog, self).__init__(parent=parent)

        self.comboBox_property = QComboBox()
        self.comboBox_field = QComboBox()
        self.comboBox_units = QComboBox()

        self.radio1 = QRadioButton(
                self.tr('Use coordinate reference system of the layer'))
        self.crs_layer = QLabel()
        self.crs_layer.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        font_height = QFontMetrics(self.crs_layer.font()).height()
        self.crs_layer.setMinimumHeight(font_height + 6)

        self.radio2 = QRadioButton(
                self.tr('Use the following coordinate reference system'))
        self.crs_select = QgsProjectionSelectionWidget()
        self.crs_select.setOptionVisible(
                QgsProjectionSelectionWidget.ProjectCrs, True)

        grid = QGridLayout()
        grid.addWidget(self.radio1, 0, 0, 1, 2)
        grid.addWidget(self.crs_layer, 1, 1)
        grid.addWidget(self.radio2, 2, 0, 1, 2)
        grid.addWidget(self.crs_select, 3, 1)
        grid.setColumnMinimumWidth(0, int(font_height * 1.5))
        grid.setColumnMinimumWidth(1, font_height * 30 + 6)
        groupBox_crs = QGroupBox(self.tr('Coordinate Reference System'))
        groupBox_crs.setLayout(grid)

        form = QFormLayout()
        form.addRow(self.tr('Property'), self.comboBox_property)
        form.addRow(groupBox_crs)
        form.addRow(self.tr('Field'), self.comboBox_field)
        form.addRow(self.tr('Units'), self.comboBox_units)

        buttonBox = QDialogButtonBox(accepted=self.accept,
                                     rejected=self.reject)
        buttonBox.setStandardButtons(QDialogButtonBox.Cancel |
                                     QDialogButtonBox.Ok)

        vbox = QVBoxLayout()
        vbox.addLayout(form)
        vbox.addWidget(buttonBox)

        self.setWindowTitle(self.tr('Calculate Geometry'))
        self.setModal(True)
        self.setLayout(vbox)


if __name__ == '__main__':
    pass
