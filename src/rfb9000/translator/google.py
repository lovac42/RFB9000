# -*- coding: utf-8 -*-
# Copyright: (C) 2020 Lovac42
# Support: https://github.com/lovac42/RFB9000
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


import os, re, time
from aqt import *
from aqt.utils import showInfo
from anki.lang import _
from requests.exceptions import ConnectionError

from ..const import ADDON_NAME
from ..clean import Cleaner
from ..error import NoNoteError, BlacklistedError

from ..lib.googletrans import Translator


LANG_MAPS = {
    'af': 'Afrikaans',
    'sq': 'Albanian',
    'am': 'Amharic',
    'ar': 'Arabic',
    'hy': 'Armenian',
    'az': 'Azerbaijani',
    'eu': 'Basque',
    'be': 'Belarusian',
    'bn': 'Bengali',
    'bs': 'Bosnian',
    'bg': 'Bulgarian',
    'ca': 'Catalan',
    'ceb': 'Cebuano',
    'ny': 'Chichewa',
    'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)',
    'co': 'Corsican',
    'hr': 'Croatian',
    'cs': 'Czech',
    'da': 'Danish',
    'nl': 'Dutch',
    'en': 'English',
    'eo': 'Esperanto',
    'et': 'Estonian',
    'tl': 'Filipino',
    'fi': 'Finnish',
    'fr': 'French',
    'fy': 'Frisian',
    'gl': 'Galician',
    'ka': 'Georgian',
    'de': 'German',
    'el': 'Greek',
    'gu': 'Gujarati',
    'ht': 'Haitian Creole',
    'ha': 'Hausa',
    'haw': 'Hawaiian',
    'iw': 'Hebrew',
    'he': 'Hebrew',
    'hi': 'Hindi',
    'hmn': 'Hmong',
    'hu': 'Hungarian',
    'is': 'Icelandic',
    'ig': 'Igbo',
    'id': 'Indonesian',
    'ga': 'Irish',
    'it': 'Italian',
    'ja': 'Japanese',
    'jw': 'Javanese',
    'kn': 'Kannada',
    'kk': 'Kazakh',
    'km': 'Khmer',
    'ko': 'Korean',
    'ku': 'Kurdish (Kurmanji)',
    'ky': 'Kyrgyz',
    'lo': 'Lao',
    'la': 'Latin',
    'lv': 'Latvian',
    'lt': 'Lithuanian',
    'lb': 'Luxembourgish',
    'mk': 'Macedonian',
    'mg': 'Malagasy',
    'ms': 'Malay',
    'ml': 'Malayalam',
    'mt': 'Maltese',
    'mi': 'Maori',
    'mr': 'Marathi',
    'mn': 'Mongolian',
    'my': 'Myanmar (Burmese)',
    'ne': 'Nepali',
    'no': 'Norwegian',
    'or': 'Odia',
    'ps': 'Pashto',
    'fa': 'Persian',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'pa': 'Punjabi',
    'ro': 'Romanian',
    'ru': 'Russian',
    'sm': 'Samoan',
    'gd': 'Scots Gaelic',
    'sr': 'Serbian',
    'st': 'Sesotho',
    'sn': 'Shona',
    'sd': 'Sindhi',
    'si': 'Sinhala',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'so': 'Somali',
    'es': 'Spanish',
    'su': 'Sundanese',
    'sw': 'Swahili',
    'sv': 'Swedish',
    'tg': 'Tajik',
    'ta': 'Tamil',
    'te': 'Telugu',
    'th': 'Thai',
    'tr': 'Turkish',
    'uk': 'Ukrainian',
    'ur': 'Urdu',
    'ug': 'Uyghur',
    'uz': 'Uzbek',
    'vi': 'Vietnamese',
    'cy': 'Welsh',
    'xh': 'Xhosa',
    'yi': 'Yiddish',
    'yo': 'Yoruba',
    'zu': 'Zulu',
}



class GoogleTranslator:
    LANGUAGES = [v for k,v in LANG_MAPS.items()]
    translator=Translator()
    htmlCleaner=Cleaner()
    totalChars=0
    stat={}
    tag=""

    def _getLangCode(self, lang):
        if lang=='Auto Detect':
            return "auto"
        for k,v in LANG_MAPS.items():
            if lang==v:
                return k
        raise InvalidLanguageError

    def setLanguages(self, src, dest):
        self.src=self._getLangCode(src)
        self.dest=self._getLangCode(dest)

    def setFields(self, word_field, rank_field):
        self.read_field=word_field
        self.write_field=rank_field

    def setProperties(self, tag, overwrite, no_html):
        self.tag=tag
        self.overwrite=overwrite
        self.no_html=no_html

    def process(self, nids):
        if not nids:
            raise NoNoteError
        self.stat={
            "total":len(nids),
            "written":0,
            "skipped":0,
            "overwritten":0,
            "netError":0,
            "nofield":0,
            "interrupted":False,
        }
        mw.checkpoint(ADDON_NAME)
        self.processNotes(nids)
        mw.col.autosave()


    def processNotes(self, nids):
        end=len(nids)
        self.progress=QProgressDialog("Translating...", "Abort", 0, end, self.parent)
        self.progress.setWindowTitle("Translating...")
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.canceled.connect(self.cancel)
        self.progress.forceShow()

        cnt=0
        for nid in nids:
            self.progress.setValue(cnt)
            cnt+=1

            if cnt%20==0: #prevent crashes, caused by net lag?
                mw.col.autosave()

            note=mw.col.getNote(nid)
            if self.read_field not in note or \
               self.write_field not in note or \
               not note[self.read_field]:
                self.stat["nofield"]+=1
                continue

            try:
                f=self.processField(note)
            except ConnectionError:
                try:
                    self.sleep(30)
                    f=self.processField(note)
                except ConnectionError:
                    self.stat["netError"]+=1
            except ValueError:
                # IP banned!
                try:
                    self.sleep(900)
                    f=self.processField(note)
                except ValueError:
                    self.progress.setValue(end)
                    raise BlacklistedError

            if self.progress.wasCanceled():
                break
            if not f:
                continue
            self.progress.setLabelText(f)
            self.progress.repaint()
            self.totalChars+=len(f)

            # Aggressive pauses are used to prevent IP bans.
            # Exact figures depends on server load and may change at any time.
            if self.totalChars>600:
                self.sleep(120)
                self.totalChars=0
            elif self.totalChars%50==0:
                self.sleep(20)
            elif len(f.split())>2 or len(f)>10:
                self.sleep(2)

        self.progress.setValue(end)


    def processField(self, note):
        if self.progress.wasCanceled():
            return

        if note[self.write_field].strip():
            if not self.overwrite:
                self.stat["skipped"]+=1
                return
            self.stat["overwritten"]+=1

        o=note[self.read_field]
        o=self.cleanWord(o)
        if not o:
            return

        t = self.translator.translate(
            str(o), src=self.src, dest=self.dest
        )
        note[self.write_field]=t.text
        # note[self.write_field]=t.pronunciation #TODO: add option

        if self.tag:
            note.addTag(self.tag)
        note.flush()
        self.stat["written"]+=1
        return o

    def cleanWord(self, txt):
        if self.no_html:
            self.htmlCleaner.reset()
            self.htmlCleaner.feed(txt)
            txt=self.htmlCleaner.toString()
        return txt.strip() #leading & trailing space

    def sleep(self, n):
        loop=QEventLoop()
        for i in range(n):
            if self.progress.wasCanceled():
                return
            if n>3:
                self.progress.setLabelText("Pause for %d secs."%(n-i))
                self.progress.repaint()
            QTimer.singleShot(999, loop.quit)
            loop.exec_()

    def cancel(self):
        self.stat["interrupted"]=True
