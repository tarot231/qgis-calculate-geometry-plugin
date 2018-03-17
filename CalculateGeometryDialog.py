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
    from qgis.PyQt.QtWidgets import *
except:
    from qgis.PyQt.QtGui import *


class CalculateGeometryDialog(QDialog):
    def __init__(self, parent=None):
        super(CalculateGeometryDialog, self).__init__(parent=parent)

        self.comboBox_property = QComboBox()
        self.comboBox_field = QComboBox()
        self.comboBox_units = QComboBox()

        form = QFormLayout()
        form.addRow(self.tr('&Property:'), self.comboBox_property)
        form.addRow(self.tr('&Field:'), self.comboBox_field)
        form.addRow(self.tr('&Units:'), self.comboBox_units)

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
    import sys
    app = QApplication(sys.argv)
    dialog = CalculateGeometryDialog()
    dialog.comboBox_property.addItems(['Length'])
    dialog.comboBox_field.addItems(['length'])
    dialog.comboBox_units.addItems(['Meters'])
    dialog.show()
    sys.exit(app.exec_())
