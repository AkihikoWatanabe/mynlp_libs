# coding=utf-8

import re
import zenhan
from collections import namedtuple

from .const import MeCabConst as mc
from .const import SentenizerConst as sc


WordData = namedtuple(
    'MeCabData',
    ('surface', 'baseform', 'pos', 'type')
)


class WordDataWithDocstring(WordData):
    """ 形態素解析して得られた個々の単語のデータを格納するnamedtuple

    Attributes:
        surface (str): 単語の表層
        baseform (str): 単語の原形
        pos (str): 単語の品詞
        type (str): 単語の品詞細分類
    """


def extract_words(sents, tagger, content_filter=True):
    """ taggerを用いて形態素解析し、sentsに含まれる単語の情報を返す。

    Args:
        sents (list): 解析する文のリスト
        tagger (Mecab.tagger): Mecab tagger
        content_filter (bool): Trueの場合は内容語の情報のみを返す。

    Returns:
        list: WordDataを要素として持つリスト
    """

    def __is_content_word(features):
        """ 単語が内容語かどうか判定する。

        Args:
            features (list): 単語のMeCabでの解析結果

        Returns:
            bool: 内容語ならばTrue, そうでないならFalse
        """

        if features[mc.POS_IDX.value] == '名詞' and (
                features[mc.TYPE_IDX.value] in mc.CTYPE_NOUN.value):
            return True
        elif (features[mc.POS_IDX.value] == '動詞' or
                features[mc.POS_IDX.value] == '形容詞') and (
                        features[mc.TYPE_IDX.value] == mc.CTYPE_VB_ADJ.value):
            return True
        else:
            return False

    sents_words = []
    for i, s in enumerate(sents):
        tagger.parse('')
        node = tagger.parseToNode(s)
        words = []
        while node:
            # 解析後の品詞、表層、細分類などは','区切りの文字列
            features = node.feature.split(',')
            surface = node.surface
            base_form = features[mc.BASEFORM_IDX.value] \
                if features[mc.BASEFORM_IDX.value] != mc.EMPTY_STR.value \
                else surface
            if __is_content_word(features) or not content_filter:
                words.append(
                        # (表層、原形, 品詞, 品詞細分類)のtuple
                        WordData(
                            surface,
                            base_form,
                            features[mc.POS_IDX.value],
                            features[mc.TYPE_IDX.value]
                        )
                )
            node = node.next
        sents_words.append(words)
    return sents_words


def sentenize(text):
    """ 日本語テキストを文分割する。

    日本語テキスト（特にブログテキスト）を文分割する。
    デリミタは、次の通り: '。', '？', '！', '?', '!', '.', '．', '…'.
    テキスト中のurlは、URLを表す特殊タグで置換する。
    また、「」内にデリミタが含まれていた場合、「」内のデリミタでは文分割されないように文分割する。

    Args:
        text(list): テキストの段落を要素として持つリスト

    Returns:
        sents(list): sentenize後の文のリスト
    """

    def __mask(text, span, masking_char="#"):
        """ span内に存在する文字列をmasking_charで置換する。

        Args:
            text(str): 置換対象のテキスト
            span(tuple): 置換を行うspan。
                         spanは(begin, end)で表現され、
                         begin、endはそれぞれspanの開始、終了位置を表す定数。
            masking_char(str): 置換後の文字

        Returns:
            str: masking_charでspan内の文字列が置換されたテキスト
        """

        begin, end = span[sc.SPAN_BEGIN.value], span[sc.SPAN_END.value]
        mask_tokens = "".join([masking_char for _ in range(begin, end)])

        return text[:begin] + mask_tokens + text[end:]

    def __demask(text, span, tokens):
        """ span内に存在する文字列をtokensで置換する。

        Args:
            text(str): 置換対象のテキスト
            span(tuple): 置換を行うspan。
                         spanは(begin, end)で表現され、
                         begin、endはそれぞれspanの開始、終了位置を表す定数。
            tokens(list): 置換後のトークン列

        Returns:
            str: span内の文字列がトークン列で置き換えられたテキスト
        """

        begin, end = span[sc.SPAN_BEGIN.value], span[sc.SPAN_END.value]

        return text[:begin] + tokens + text[end:]

    def __mask_url(text):
        """ text内に含まれるURLを特殊タグ('<URL>')に置換する。

        Args:
            text(list): テキストの段落を要素として持つリスト

        Returns:
            str: URLを置換した後の文字列
        """

        for i, par in enumerate(text):
            text[i] = re.sub(sc.URL_REGEX.value, sc.URL_TAG.value, text[i])

        return text

    def __mask_delimiter(text):
        """ 「」内にdelimiterがあった場合、delimiterを特殊文字を用いてマスクする。

        Args:
            text (list): テキストの段落を要素として持つリスト

        Returns:
            list: マスク後の段落を要素として持つリスト
            list: マスキングに関する情報を保持するリスト。
            　　　リストの各要素は、(マスクしたdelimiterの位置, マスクしたdelimiterの表層)のtuple
        """

        # テキスト全体から見たときに、現在参照している段落の開始位置を表すoffset
        global_offset = 0
        p_inner_dlmtr = re.compile(sc.INNER_DLMTR_REGEX.value)
        p_dlmtr = re.compile(sc.DLMTR_PLUS_REGEX.value)
        mask_info = []
        text_masked = text[:]

        for i, par in enumerate(text):
            for m_inner_dlmtr in p_inner_dlmtr.finditer(par):
                # デリミタを含む「」の開始位置をoffsetとして保存
                local_offset = m_inner_dlmtr.span()[sc.SPAN_BEGIN.value]
                # 「」内の個々のデリミタの位置と表層を取得し保存
                for m_dlmtr in p_dlmtr.finditer(m_inner_dlmtr.group()):
                    # 現在参照している段落内でのデリミタのspan
                    local_span = __add_offset(m_dlmtr.span(), local_offset)
                    # テキスト全体でのデリミタのspan
                    global_span = __add_offset(local_span, global_offset)
                    tokens = m_dlmtr.group(1)
                    par = __mask(par, local_span)
                    mask_info.append((global_span, tokens))
            text_masked[i] = par
            global_offset += len(par)

        return text_masked, mask_info

    def __add_offset(span, offset):
        """ 与えられたspanにoffsetを加算したspanを返す。

        Args:
            span (tuple): (begin, end)のtupleで表現されるspan。
                          begin, endはそれぞれspanの開始、終了位置。
            offset (int): 加算するoffset

        Returns:
            tuple: offset分加算したspan
        """

        begin = span[sc.SPAN_BEGIN.value] + offset
        end = span[sc.SPAN_END.value] + offset

        return (begin, end)

    def __demask_delimiter(sents, mask_info):
        """ マスクしたdelimiterを置換前の表層に置換する。

        Args:
            sents (list): 文を要素として持つリスト
            mask_info (list): delimiterのマスキングに関する情報を保持するリスト。
                              要素は、(マスクしたdelimiterの位置, マスクしたdelimiterの表層)のtuple

        Returns:
            list: マスクしたdelimiterを、置換前の表層に置換した文を要素として持つリスト
        """

        for (begin, end), tokens in mask_info:
            # テキストの開始位置から数えた、現在着目している文の位置
            global_offset = 0
            for i, s in enumerate(sents):
                if begin >= global_offset and end <= global_offset+len(s):
                    # begin, endはglobal_spanなので、local_spanに変換してdemaskする
                    local_span = __add_offset((begin, end), -global_offset)
                    sents[i] = __demask(s, local_span, tokens)
                    break
                global_offset += len(s)

        return sents

    def __split_by_delimiter(text):
        """ 文書をデリミタで文に分割する。

        Args:
            text (list): テキストの段落を要素として持つリスト

        Returns:
            list: 文分割後の文を要素として持つリスト
        """

        sents = []
        for par in text:
            sents += filter(
                    lambda s: len(s) > 0, re.split(sc.DLMTR_REGEX.value, par)
            )

        if len(sents) == 1:  # 連結する要素が存在しない場合
            return sents

        # sents内に残っているdelimiterの表層を文と結合する
        # Example: ["こんにちは", "。", ...] -> [u"こんにちは。", ...]
        dlmtr_idx = [i for i, s in enumerate(sents) if s in sc.DLMTR.value]
        del_num = 0
        for i in dlmtr_idx:
            if i-1-del_num >= 0:
                sents[i-1-del_num] += sents.pop(i-del_num)
                del_num += 1

        return sents

    def __is_alphabet_only(sent):
        """ 与えられた文字列が、アルファベットのみで構成されているか否か判定して返す。

        Args:
            sent (str): 判定する文字列

        Returns:
            bool: 文字列がアルファベットのみの場合はTrue、そうでなければFalse
        """

        replaced = sent.replace(" ", "").replace("　", "")  # 空白文字を削除
        replaced = zenhan.z2h(replaced, mode=1)
        replaced = zenhan.z2h(replaced, mode=2)

        p = re.compile(sc.ALPHABET_REGEX.value)

        return p.match(replaced) is not None

    text = __mask_url(text)
    text_masked, mask_info = __mask_delimiter(text)
    sents = __split_by_delimiter(text_masked)
    sents = sents if mask_info == [] else __demask_delimiter(sents, mask_info)
    sents = [s for s in sents if __is_alphabet_only(s) is False]

    return [sent.strip() for sent in sents]
