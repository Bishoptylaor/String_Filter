# -*- coding: utf-8 -*-
__author__ = 'wxy'
import re
import traceback
from HTMLParser import HTMLParser
from urllib2 import unquote

from transCell.handlers.character_handler.filter_base import all_consealedUni2blank_mapping, common_concealedUni2blank_mapping
from transCell.handlers.character_handler.filter_base import full_half_mapping, Ch2En_punctuation_mapping

reg_replace_white_space_obj = re.compile('\s+')
PUNCTUATION = "(,|\.|:|;|!|~|`|@|#|\$|%|^|&|\*|\(|\)|\-|_|\+|=|\\|\{|\}|\[|\]|<|>|\?|/|\||Ω|●|°|\'|\"|®|©|™|×|÷|，|。|；|？|：|±|²|³|«|¤|¯|»|›|⊥|≤|≥|≠|≡|≈|∝|∼|∴|∠|∨|∞|∀|∈|∉|∋|∅|※)"
CHINESE_REG = re.compile(u"[\u4e00-\u9fa5]+")
FULLCOMMA_REG = re.compile(u"([\uff00-\uffef]|[\u3000-\u303f]|[\u3300-\u33ff])+")
RUSSIAN_REG = re.compile(r"[АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийкдмнопрстуфхцчшщъыьэюя]+")
DIGIT_PUN_REG = re.compile('(\d|%s)+$' % PUNCTUATION)
ENGLISH_REG = re.compile(r"[a-zA-Z]")
BLANK_REG = re.compile(u"\\t|\\n|\\r")
JAPANESE_REG = re.compile(u"([\u3040-\u309f]|[\u30a0-\u30ff]|[\u310f-\u31ff])+")
KOREAN_REG = re.compile(u"([\uac00-\ud7af]|[\u1100-\u11ff]|[\u3130-\u318f]|[\u3100-\u312f])+")


def html_unescape(word):
    """
    :param word: '&#19968;&#24180;&#19968;&#24230;&#30340;&apos;abc&copy;&nbsp;&nbsp;&gt;'
    :return: word： '一年一度的'abc©  >'
    """
    try:
        h = HTMLParser()
        return h.unescape(word)
    except:
        return word


def unicode_string(word):
    '''
    :param all kinds of string type
    :return: formed unicode string
    '''
    if isinstance(word, str):
        word = re.sub(r"[\\]+", r"\\", word)
        word = get_unicode(word)
        word = re.sub(r"\\u[a-zA-Z0-9]{4}", unicode_escape, word)
    elif isinstance(word, unicode):
        word = re.sub(r"\\u[a-zA-Z0-9]{4}", unicode_escape, word)
        word = re.sub(u"[\x7e-\xff]{1,}", unicode_escape, word)
    return word


def unicode_escape(matchobj):
    '''
    "\\u559c\\u6b22\\u4e00\\u4e2a\\u4eba我们(utf8)" to u"\u559c\u6b22\u4e00\u4e2a\u4eba"
    If matchobj like \xc3\xbb, pass
    '''
    try:
        word = matchobj.group(0)
        for item in ["\\u", "\u"]:
            if item in word:
                word = word.decode("unicode-escape")
                return word
            else:
                word = word.encode("ISO-8859-1").decode("utf8")
                return word
    except:
        return matchobj.group(0)


def get_unicode(str):
    '''
    str: str in other coding change into unicode
    '''
    if isinstance(str, unicode):
        return str
    for c in ('utf8', 'gbk', 'utf16', 'utf32', 'gb2312', 'ISO-8859-2'):
        try:
            return str.decode(c)
        except:
            pass
    return str


def str2utf8(str):
    if isinstance(str, unicode):
        try:
            return str.encode('utf8'), "utf8"
        except:
            pass
    for c in ('utf8', 'gbk', 'utf16', 'utf32', 'gb2312', 'ISO-8859-2'):
        try:
            return str.decode(c).encode('utf8'), c
        except:
            pass
    return str, ""


def common_unicode_form(word):
    """
    :param word: "\u559c\u6b22\u00a0\u4e00\u4e2a\u4eba\ueffe"
    :return: word: "\u559c\u6b22 \u4e00\u4e2a\u4eba\ueffe"
    Change common undisplayed unicode character into english halfwidth blank.
    """
    word = unicode_string(word)
    for key, value in common_concealedUni2blank_mapping.items():
        word = word.replace(key, value)
    return word


def full_unicode_form(word):
    """
    :param word: "\u559c\u6b22\u00a0\u4e00\u4e2a\u4eba\ueffe"
    :return: word: "\u559c\u6b22 \u4e00\u4e2a\u4eba "
    Change ALL undisplayed unicode character (from \u0000 to \uffff) into english halfwidth blank.
    """
    word = unicode_string(word)
    for key, value in all_consealedUni2blank_mapping.items():
        word = word.replace(key, value)
    return word


def url_unquote(word):
    '''
    If b = qoute(qoute(a)),then you have to unqoute 2 times to get the original string a;
    If b = qoute(a), then if you unqoute b more than once doesn`t make any difference, you will always get the original string a.
    '''
    return unquote(word)


def multi_blank2single_blank(content):
    '''
    :param content: "abc   ss d high   ,    hello"
    :return: "abc ss d high , hello"
    '''
    try:
        tmp_content = content
        tmp_content = re.sub(reg_replace_white_space_obj, ' ', tmp_content)
        return tmp_content
    except:
        return content


def half2full(word):
    """
    Halfwidth character into Fullwidth, except digits and english.The output type is unicode
    """
    word = unicode_string(word)
    try:
        fstring = ""
        for ch in word:
            inside_code = ord(ch)
            if (inside_code > 32 and inside_code < 48) \
                    or(inside_code >57 and inside_code < 65) \
                    or(inside_code > 90 and inside_code < 97) \
                    or(inside_code > 122 and inside_code < 128):#除 数字 大小写字母 外，其他均转换为全角
                inside_code += 65248
            for key, value in full_half_mapping.items():
                if inside_code == value:
                    inside_code = int(key)
            fstring += unichr(inside_code)
        return fstring
    except:
        return word


def full2half(word):
    """
    Fullwidth character into Halfwidth, except digits and english
    Only accept word in Unicode, like '～！＠＃＄％＾＆＊（',
        u'\uff5e\uff01\uff20\uff03\uff04\uff05\uff3e\uff06\uff0a\uff08'
        or '\xef\xbd\x9e\xef\xbc\x81\xef\xbc\xa0\xef\xbc\x83\xef\xbc\x84\xef\xbc\x85\xef\xbc\xbe\xef\xbc\x86\xef\xbc\x8a\xef\xbc\x88'
        We will change the coding into unicode automaticlly.
    :return ~!@#$%^&*(
    """
    word = unicode_string(word)
    try:
        hstring = u""
        for ch in word:
            inside_code = ord(ch)
            if (inside_code>(32+65248) and inside_code < (48+65248))\
                    or(inside_code > (57+65248) and inside_code < (65+65248))\
                    or(inside_code > (90+65248) and inside_code < (97+65248))\
                    or(inside_code > (122+65248) and (inside_code < 127+65248)):
                inside_code -= 65248
            for key, value in full_half_mapping.items():
                if str(inside_code) == key:
                    inside_code = value
            hstring += unichr(inside_code)
        return hstring
    except:
        return traceback.format_exc()


def isUseful(ch):
    if re.search(ENGLISH_REG, ch) or re.search(CHINESE_REG, ch) or re.search(RUSSIAN_REG, ch) \
        or re.search(DIGIT_PUN_REG, ch) or re.search(FULLCOMMA_REG, ch) or re.search(JAPANESE_REG, ch) \
            or re.search(KOREAN_REG, ch):
        return True
    else:
        return False


def isMessyCode(word):
    '''
    :param word:类似"²Ã#²WBÑ¨ÍØÒ'2¥ÈYÝ¤Q"， 不支持"灏忔暟杩涜闄ゆ硶杩愮畻鐨勬纭柟娉曠ず渚�,姝ｇ‘鐨勬"
    :return: True表示乱码， False表示不是乱码
    '''
    word = unicode_string(word)
    word = re.sub(BLANK_REG, " ", word)
    word = re.sub(u"\s+", u" ", word)
    total_length = len(word)
    count = 0
    for ch in word:
        if not isUseful(ch):
            count += 1
    result = float(count)/total_length
    if result > 0.2:
        return True
    else:
        return False


def remove_nrt(word):
    '''
    :param word: u"a\r+b\n+c\t"    \r,\t,\n in Unicode to blank
    :return: u"a +b +c"
    '''
    word = re.sub(BLANK_REG, " ", word)
    return word

def C2E(word):
    """
    中文标点符号的替换
    :param [ "“", "”", "‘", "’", "。", "，", "；", "：", "？", "！", "……", "—", "～", "（", "）", "《", "》", "【", "】" ]
    :return: [ "\"", "\"", "'", "'", ".", ",", ";", ":", "?", "!", "…", "-", "~", "(", ")", "<", ">" , "[", "]"]
    """
    for k, v in Ch2En_punctuation_mapping.items():
        word = word.replace(k, v)
    return word
