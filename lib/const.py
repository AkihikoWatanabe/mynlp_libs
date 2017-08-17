# coding=utf-8

from collections import Enum

# loggerがログを書き出すディレクトリ
LOG_DIR = "./log"


class MeCabConst(Enum):
    """ MeCab関連の定数を定義。Preprocessingモジュールで用いる。

    Attributes:
        BASEFORM_IDX (int): node.featureが保持する基本形のindex
        POS_IDX (int): node.featureが保持する品詞のindex
        TYPE_IDX (int): node.featureが保持する品詞細分類のindex
        EMPTY_STR (str): 要素が空であることを示す文字列
        CTYPE_NOUN (list): 内容語として扱う名詞の細分類
        CTYPE_VERB_ADJ (str): 内容語として扱う動詞・形容詞の細分類
    """

    BASEFORM_IDX = 6
    POS_IDX = 0
    TYPE_IDX = 1
    EMPTY_STR = r"*"
    CTYPE_NOUN = [
            '一般',
            '固有名詞',
            'サ変接続',
            '形容動詞語幹',
            'ナイ形容詞語幹',
            '副詞可能'
    ]
    CTYPE_VB_ADJ = '自立'


class SentenizerConst(Enum):
    """ Sentenizer関連の定数を定義。Preprocessingモジュールで用いる。

    Attributes:
        SPAN_BEGIN (int): spanの開始位置を表すindex
        SPAN_END (int): spanの終了位置を表すindex
        URL_TAG (str): URLを置換する際に使用する特殊タグ
        URL_REGEX (str): URLを検出するための正規表現
        DLMTR (list): デリミタとして利用する文字のリスト
        INNER_DLMTR_REGEX (str): 「」内にデリミタを含むか否か検出するための正規表現
        DLMTR_REGEX (str): デリミタを含むか否か検出するための正規表現
        ALPHABET_REGEX (str): アルファベットや特殊文字のみで構成された文を検出するための正規表現
    """

    SPAN_BEGIN = 0
    SPAN_END = 1
    URL_TAG = "<URL>"
    URL_REGEX = "https?://[\w:;/.?%#&=+-]+"
    DLMTR = ["。", "？", "！", "?", "!", ".", "．", "…"]
    INNER_DLMTR_REGEX = "「[^「|^」]*?([。|？|！|\?|!|\.|．|…]+)[^「|^」]*?」"
    DLMTR_PLUS_REGEX = "([。|？|！|\?|!|\.|．|…]+)"
    DLMTR_REGEX = "([。|？|！|\?|!|\.|．|…])"
    ALPHABET_REGEX = "^[a-zA-Z0-9!-/:-@[-`{-~]+$"
