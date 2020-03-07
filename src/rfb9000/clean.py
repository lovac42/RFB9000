# -*- coding: utf-8 -*-
# Copyright: (C) 2020 Lovac42
# Support: https://github.com/lovac42/RFB9000
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


from html.parser import HTMLParser


class Cleaner(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.reset()

    def reset(self):
        HTMLParser.reset(self)
        self.dat=[]

    def handle_data(self, txt):
        self.dat.append(txt)

    def toString(self):
        return ''.join(self.dat)
