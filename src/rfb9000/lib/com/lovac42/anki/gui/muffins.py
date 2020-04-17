# -*- coding: utf-8 -*-
# Copyright (c) 2019-2020 Lovac42
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


from aqt.qt import *


def getMuffinsTab(ui_pref):
    try:
        return ui_pref.lrnStageGLayout
    except AttributeError:
        ui_pref.lrnStage = QWidget()
        ui_pref.tabWidget.addTab(ui_pref.lrnStage, "Muffins")
        ui_pref.lrnStageGLayout = QGridLayout()
        ui_pref.lrnStageVLayout = QVBoxLayout(ui_pref.lrnStage)
        ui_pref.lrnStageVLayout.addLayout(ui_pref.lrnStageGLayout)
        spacerItem = QSpacerItem(
            1, 1,
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        ui_pref.lrnStageVLayout.addItem(spacerItem)
        return ui_pref.lrnStageGLayout


def getMuffinsGroupbox(ui_pref, title):
    tab_layout = getMuffinsTab(ui_pref)
    groupbox = ui_pref.lrnStage.findChild(QGroupBox, title)
    if not groupbox:
        groupbox = QGroupBox(ui_pref.lrnStage)
        groupbox.setObjectName(title)
        groupbox.setTitle(title)
        r = tab_layout.rowCount()
        tab_layout.addWidget(groupbox, r, 0, 1, 3)
    return groupbox
