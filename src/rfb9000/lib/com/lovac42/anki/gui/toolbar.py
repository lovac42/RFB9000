# -*- coding: utf-8 -*-
# Copyright (c) 2020 Lovac42
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


from aqt import QMenu


def getMenu(parent, menuName):
    menubar = parent.form.menubar
    for a in menubar.actions():
        if menuName == a.text():
            return a.menu()
    return menubar.addMenu(menuName)


def getSubMenu(menu, subMenuName):
    for a in menu.actions():
        if subMenuName == a.text():
            return a.menu()
    subMenu = QMenu(subMenuName, menu)
    menu.addMenu(subMenu)
    return subMenu
