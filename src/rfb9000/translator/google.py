# -*- coding: utf-8 -*-
# Copyright: (C) 2020 Lovac42
# Support: https://github.com/lovac42/RFB9000
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


import os, re
import time
from aqt import mw
from aqt.utils import showInfo
from anki.lang import _
from requests.exceptions import ConnectionError

from ..const import ADDONNAME
from ..clean import Cleaner
from ..error import NoNoteError

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
    'uz': 'Uzbek',
    'vi': 'Vietnamese',
    'cy': 'Welsh',
    'xh': 'Xhosa',
    'yi': 'Yiddish',
    'yo': 'Yoruba',
    'zu': 'Zulu',
    'fil': 'Filipino',
    'he': 'Hebrew'
}



class GoogleTranslator:
    LANGUAGES = [v for k,v in LANG_MAPS.items()]
    translator=Translator()
    htmlCleaner=Cleaner()
    startTime=0
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
        }
        mw.checkpoint(ADDONNAME)
        self.processNotes(nids)


    def processNotes(self, nids):
        self.startTime=0
        for nid in nids:
            note=mw.col.getNote(nid)
            if self.read_field not in note or \
               self.write_field not in note or \
               not note[self.read_field]:
                self.stat["nofield"]+=1
                continue
            f=self.processField(note)
            self.totalChars+=len(f)

            # Aggressive pauses are used to prevent IP bans.
            if self.totalChars>500:
                mw.progress.update("Pausing for 100 secs, you hit the limit.")
                time.sleep(100)
                self.totalChars=0
            elif self.totalChars%25==0:
                mw.progress.update("Pausing for 30 secs...")
                time.sleep(30)
            elif len(f.split())>2:
                time.sleep(2)


    def processField(self, note, retry=True):
        try:
            if note[self.write_field].strip():
                if not self.overwrite:
                    self.stat["skipped"]+=1
                    return "k"
                self.stat["overwritten"]+=1

            o=note[self.read_field]
            o=self.cleanWord(o)
            if not o:
                return "n"

            t = self.translator.translate(
                str(o), src=self.src, dest=self.dest
            )
            note[self.write_field]=t.text
            # note[self.write_field]=t.pronunciation #TODO: add option

            if self.tag:
                note.addTag(self.tag)
            note.flush()
            self.stat["written"]+=1
            self.updatePTimer(o)
            return o
        except ConnectionError:
            self.stat["netError"]+=1
            return "e"
        except ValueError:
            print("You hit the google char limit!")
            if not retry:
                raise ValueError
            mw.progress.update("Pausing for 300 secs, you may have been banned.")
            time.sleep(300)
            return self.processField(note, retry=False)


    def cleanWord(self, txt):
        if self.no_html:
            self.htmlCleaner.reset()
            self.htmlCleaner.feed(txt)
            txt=self.htmlCleaner.toString()
        return txt.strip() #leading & trailing space


    def updatePTimer(self, labelText):
        now = time.time()
        if now-self.startTime >= 0.5:
            self.startTime=now
            mw.progress.update(_("%s"%labelText))
