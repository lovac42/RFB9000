# -*- coding: utf-8 -*-
# Copyright (c) 2020 Lovac42
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


import re
from anki.lang import currentLang


LANG_MAP = {
    "af": "af_ZA", "ar": "ar_SA", "bg": "bg_BG",
    "ca": "ca_ES", "cs": "cs_CZ", "da": "da_DK",
    "de": "de_DE", "el": "el_GR", "en": "en_US",
    "eo": "eo_UY", "es": "es_ES", "et": "et_EE",
    "eu": "eu_ES", "fa": "fa_IR", "fi": "fi_FI",
    "fr": "fr_FR", "gl": "gl_ES", "he": "he_IL",
    "hr": "hr_HR", "hu": "hu_HU", "hy": "hy_AM",
    "it": "it_IT", "ja": "ja_JP", "ko": "ko_KR",
    "mn": "mn_MN", "ms": "ms_MY", "nl": "nl_NL",
    "nb": "nb_NL", "no": "nb_NL", "oc": "oc_FR",
    "pl": "pl_PL", "pt": "pt_PT", "ro": "ro_RO",
    "ru": "ru_RU", "sk": "sk_SK", "sl": "sl_SI",
    "sr": "sr_SP", "sv": "sv_SE", "th": "th_TH",
    "tr": "tr_TR", "uk": "uk_UA", "vi": "vi_VN",
}


RE_STRIP_DASH = re.compile(r"-")

def getLang(lang=currentLang):
    if lang in LANG_MAP:
        return LANG_MAP[lang]
    return RE_STRIP_DASH.sub("_", lang)

# Note 1:
#   Old profiles may have 2 letter chars
#   saved to the user profile dispite being
#   on a newer version of anki.

# Note 2:
#   2.0.52 - 2.1.15 uses 2 chars for most locales.
#   2.1.16 - 2.1.23 uses 2_2 format.
#   2.1.24 uses a hyphen instead of _ for some locales.
#   (e.g. en_US, en-GB, ja_JP, zh-CN)

