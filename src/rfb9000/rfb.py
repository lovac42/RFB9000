# -*- coding: utf-8 -*-
# Copyright: (C) 2020 Lovac42
# Support: https://github.com/lovac42/RFB9000
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


import re
from aqt import mw
from aqt.qt import *
from aqt.utils import getFile, showInfo
from anki.lang import _

from .error import *
from .const import TITLE
from .translator.google import GoogleTranslator

from .lib.com.lovac42.anki.backend.notes import fieldNamesForNotes
from .lib.com.lovac42.anki.version import ANKI21


class RFB9000:
    translator=GoogleTranslator()

    def __init__(self, browser, conf):
        self.browser=browser
        self.conf=conf

        #Must have some notes selected in browser
        try:
            self.setNotes()
        except NoNoteError as err:
            showInfo(str(err))
            return

        #Note in editor must be removed to update templates.
        if ANKI21:
            self.browser.editor.saveNow(self.hideEditor)
        else:
            self.browser.editor.saveNow()
            self.hideEditor()

        self.showDialog()


    def setNotes(self):
        self.notes=self.browser.selectedNotes()
        if not self.notes:
            raise NoNoteError


    def hideEditor(self):
        self.browser.editor.setNote(None)
        self.browser.singleCard=False


    def showDialog(self):
        fields=fieldNamesForNotes(self.notes)

        r=0
        gridLayout=QGridLayout()
        layout=QVBoxLayout()
        layout.addLayout(gridLayout)

        fieldLayout=QHBoxLayout()
        fieldLayout.addWidget(QLabel("Read From:"))

        idx=self.conf.get("read_field",0)
        self.readField=QComboBox()
        self.readField.setMinimumWidth(180)
        self.readField.addItems(fields)
        self.readField.setCurrentIndex(idx)
        self.readField.currentIndexChanged.connect(self.checkWritable)
        fieldLayout.addWidget(self.readField)
        gridLayout.addLayout(fieldLayout,r,0, 1, 1)

        fieldLayout=QHBoxLayout()
        fieldLayout.addWidget(QLabel("Lang:"))
        idx=self.conf.get("read_lang",0)
        self.readLang=QComboBox()
        self.readLang.setMinimumWidth(120)
        self.readLang.addItems(['Auto Detect'])
        self.readLang.addItems(self.translator.LANGUAGES)
        self.readLang.setCurrentIndex(idx)
        self.readLang.currentIndexChanged.connect(self.checkWritable)
        fieldLayout.addWidget(self.readLang)
        gridLayout.addLayout(fieldLayout,r,1, 1, 1)


        r+=1
        fieldLayout=QHBoxLayout()
        fieldLayout.addWidget(QLabel("Write To:    "))

        idx=self.conf.get("write_field",0)
        self.writeField=QComboBox()
        self.writeField.setMinimumWidth(180)
        self.writeField.addItems(fields)
        self.writeField.setCurrentIndex(idx)
        self.writeField.currentIndexChanged.connect(self.checkWritable)
        fieldLayout.addWidget(self.writeField)
        gridLayout.addLayout(fieldLayout,r,0, 1, 1)

        fieldLayout=QHBoxLayout()
        fieldLayout.addWidget(QLabel("Lang:"))
        idx=self.conf.get("write_lang",0)
        self.writeLang=QComboBox()
        self.writeLang.setMinimumWidth(120)
        self.writeLang.addItems(self.translator.LANGUAGES)
        self.writeLang.setCurrentIndex(idx)
        self.writeLang.currentIndexChanged.connect(self.checkWritable)
        fieldLayout.addWidget(self.writeLang)
        gridLayout.addLayout(fieldLayout,r,1, 1, 1)


        r+=1
        self.cb_overWrite=QCheckBox()
        self.cb_overWrite.setText(_('Overwrite field if not empty?'))
        self.cb_overWrite.setToolTip(_('Do you seriously need a tooltip for this?'))
        gridLayout.addWidget(self.cb_overWrite, r, 0, 1, 1)


        r+=1
        cbs=self.conf.get("strip_html",0)
        self.cb_rm_html=QCheckBox()
        self.cb_rm_html.setCheckState(cbs)
        self.cb_rm_html.clicked.connect(self.onChangedCB)
        self.cb_rm_html.setText(_('Strip HTML'))
        self.cb_rm_html.setToolTip(_('Strip HTML during search'))
        gridLayout.addWidget(self.cb_rm_html, r, 0, 1, 1)


        r+=1
        lbl_help=QLabel()
        lbl_help.setText(_("""<br><i>Exact matches only, 
                           beware of hidden html tags.</i><br>
                           <b>Make sure to backup first!</b>"""))
        gridLayout.addWidget(lbl_help,r,0,1,1)

        self.btn_save=QPushButton('Translate')
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.onWrite)
        gridLayout.addWidget(self.btn_save,r,1,1,1)

        self.checkWritable()
        self.dialog=QDialog(self.browser)
        self.dialog.setLayout(layout)
        self.dialog.setWindowTitle(TITLE)
        self.dialog.exec_()


    def onChangedCB(self):
        htm=self.cb_rm_html.checkState()
        self.conf.set("strip_html",htm)

    def checkWritable(self):
        idx=self.readField.currentIndex()
        self.conf.set("read_field",idx)

        idx=self.readLang.currentIndex()
        self.conf.set("read_lang",idx)

        idx=self.writeField.currentIndex()
        self.conf.set("write_field",idx)

        idx=self.writeLang.currentIndex()
        self.conf.set("write_lang",idx)

        rf=self.readField.currentText()
        rl=self.readLang.currentText()
        wf=self.writeField.currentText()
        wl=self.writeLang.currentText()
        if not rf or not wf or not rl or not wl or rl==wl or rf==wf:
            self.btn_save.setEnabled(False)
        else:
            self.btn_save.setEnabled(True)


    def onWrite(self):
        if self.btn_save.isEnabled():
            tag=self.conf.get("autotag","RFB9K")
            src=self.readLang.currentText()
            dest=self.writeLang.currentText()
            rField=self.readField.currentText()
            wField=self.writeField.currentText()
            ow=self.cb_overWrite.checkState()
            htm=self.cb_rm_html.checkState()

            if len(self.notes)>20 and \
            self.conf.get("run_in_bg", False):
                self.dialog.close() #run in background
                self.translator.parent=None
            else:
                self.translator.parent=self.dialog

            self.translator.setLanguages(src,dest)
            self.translator.setFields(rField,wField)
            self.translator.setProperties(tag,ow,htm)
            self.translator.process(self.notes)
            self.showStats()


    def showStats(self):
        tot=self.translator.stat["total"]
        w=self.translator.stat["written"]
        s=self.translator.stat["skipped"]
        ow=self.translator.stat["overwritten"]
        ne=self.translator.stat["netError"]
        e=self.translator.stat["nofield"]
        txt="""Process completed!

SUMMARY:\t\t\t( %d / %d )
\tTotal Notes:\t\t%d
\tMatches:\t\t%d
\tWritten:\t\t%d
\tOverwritten:\t\t%d
\tNot overwr.:\t\t%d
\tNo FieldName:\t\t%d
\tNet Error:\t\t%d
\tSkipped:\t\t%d
"""%(w,tot,tot,w+s,w,ow,s,e,ne,e+s+ne)

        if self.translator.stat["interrupted"]:
            txt+="\nTHE PROCESS WAS ABORTED!"
        showInfo(txt)
