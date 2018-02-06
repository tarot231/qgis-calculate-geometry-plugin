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
    from PyQt4.QtGui import *
except:
    from PyQt5.QtWidgets import *


class CalculateGeometryDialog(QDialog):
    def __init__(self, parent=None):
        super(CalculateGeometryDialog, self).__init__(parent=parent)

        self.comboBox_property = QComboBox()
        self.comboBox_field = QComboBox()
        self.comboBox_units = QComboBox()

        grid = QGridLayout()
        grid.addWidget(QLabel('Property:'), 0, 0)
        grid.addWidget(QLabel('Field:'), 1, 0)
        grid.addWidget(QLabel('Units:'), 2, 0)
        grid.addWidget(self.comboBox_property, 0, 2)
        grid.addWidget(self.comboBox_field, 1, 2)
        grid.addWidget(self.comboBox_units, 2, 2)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 4)

        buttonBox = QDialogButtonBox(accepted=self.accept,
                                     rejected=self.reject)
        buttonBox.setStandardButtons(QDialogButtonBox.Cancel |
                                     QDialogButtonBox.Ok)

        vbox = QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addWidget(buttonBox)

        self.setWindowTitle('Calculate Geometry')
        self.setModal(True)
        self.setLayout(vbox)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    dialog = CalculateGeometryDialog()
    dialog.comboBox_property.addItems(['Length'])
    dialog.comboBox_field.addItems(['length'])
    dialog.comboBox_units.addItems(['Meters'])
    dialog.show()
    sys.exit(dialog.exec_())
