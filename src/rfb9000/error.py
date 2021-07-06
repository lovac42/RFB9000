# -*- coding: utf-8 -*-
# Copyright: (C) 2020-2021 Lovac42
# Support: https://github.com/lovac42/RFB9000
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


class NoNoteError(Exception):
    """Raised when no note is selected"""
    def __str__(self): 
        return "Select some notes first"

class NoListError(Exception):
    """Raised when there is no list given"""
    def __str__(self): 
        return "Can't process list"

class InvalidFormatError(Exception):
    """Raised when dictionary list has the wrong format"""
    def __init__(self, line_num, line_txt):
        self.message="Invalid Freq List format.\nLine %d, %s"%(line_num,line_txt)
        super(InvalidFormatError, self).__init__(self.message)

    def __str__(self):
        return self.message

class InvalidLanguageError(Exception):
    """Raised when there is no language support"""
    def __str__(self): 
        return "An invalid language code was given."

class BlacklistedError(Exception):
    """Raised when it fails to connect to translation service"""
    def __str__(self): 
        return "Banned from using the translation service."
