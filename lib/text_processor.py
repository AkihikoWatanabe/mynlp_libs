# coding=utf-8

import re
import zenhan


def extract_words(sents, tagger):
    """ Extract words from sents and return the original form.
    Params:
        sents(list[[str1], [str2], ...]): list of sentences
        tagger: Mecab tagger

    Returns:
        list[(surface, pos, class), ...]: 
    """

    sents_words = []
    for i, s in enumerate(sents):
        node = tagger.parseToNode(s)
        words = []
        while node:
            features = node.feature.split(',')
            original_form = features[6] if features[6]!=r"*" else node.surface
            words.append((original_form, features[0], features[1]))
            node = node.next
        sents_words.append(words)
    return sents_words

def sentenizer(text):
    """ Sentenizer for Japanese texts (basically, blog texts).
    Delimiters are as follows: '。', '？', '！', '?', '!', '.', '．', '…'.
    Params:
        text(list[unicode]): list of texts

    Returns:
        sents(list[unicode]): list of sentences
    """
    # TODO: 全体的にリファクタリング

    def __mask(text, span, repl=u"#"):
        """ Replace characters that is located within 'span' with 'repl'
        Params:
            text(unicode): input text
            span(tuple(int, int)): span for replacement, int value of (begin, end)
            repl(unicode): the character that replaced with text

        Returns:
            unicode: text that is replaced with 'repl'
        """
        mask_tokens = u"".join([repl for _ in xrange(span[0], span[1])])
        return text[:span[0]] + mask_tokens + text[span[1]:]
       
    def __demask(text, span, tokens):
        """ Replace characters that is located within 'span' with 'tokens'.
        Params:
            text(unicode): input text
            span(tuple(begin, end)): span for replacement
            tokens(list[unicode]): tokens that replaced with text

        Returns:
            unicode: text that is replaced with 'tokens'
        """
        return text[:span[0]] + tokens + text[span[1]:]

    def __mask_url(text):
        """ Replace URL strings with special tag '<URL>'
        Params:
            text(list[unicode]): input text

        Returns:
            unicode: text after replacement
        """
        for i, par in enumerate(text):
            text[i] = re.sub(u"https?://[\w:;/.?%#&=+-]+", u"<URL>", text[i])
        return text

    def __mask_delimiter(text):
        l = 0
        # 「」内に一つでもdelimiterがあるものを抽出
        p1 = re.compile(u"「[^「|^」]*?([。|？|！|\?|!|\.|．|…]+)[^「|^」]*?」")
        # 「」内のdelimiterを全て見つけ、置換
        p2 = re.compile(u"([。|？|！|\?|!|\.|．|…]+)")
        mask_info = []
        for i, par in enumerate(text):
            for m1 in p1.finditer(par):
                offset = m1.span()[0]
                for m2 in p2.finditer(m1.group()):
                    local_span = tuple(map(lambda x: x+offset, m2.span()))
                    global_span = tuple(map(lambda x: x+l, local_span)) # 全体からみて何番目のcharか
                    tokens = m2.group(1)
                    # 置き換え
                    par = __mask(par, local_span)
                    # maskをした部分のspan(テキスト全体で見たときの位置)とトークンを格納
                    mask_info.append((global_span, tokens))
            text[i] = par
            l += len(par)
        return text, None if mask_info==[] else mask_info

    def demask_delimiter(sents, mask_info):
        global2local = lambda span, offset: (span[0]-offset, span[1]-offset)
        for (begin, end), tokens in mask_info:
            l = 0
            for i, s in enumerate(sents):
                if begin>=l and end<=l+len(s):
                    sents[i] = __demask(s, global2local((begin, end), l), tokens)
                    break
                l += len(s)
        return sents 

    def concat_delimiter(sents, delimiter):
        if len(sents)==1:
            return sents
        idx = []
        for i, s in enumerate(sents):
            for d in delimiter:
                if s==d: idx.append(i)
        d = 0
        for i in idx:
            if i-1-d >= 0:
                sents[i-1-d] += sents.pop(i-d)
                d += 1
        return sents

    def is_alphabet_only(sent):
        replaced = sent.replace(u" ", u"").replace(u"　", u"")
        replaced = zenhan.z2h(replaced, mode=1)
        replaced = zenhan.z2h(replaced, mode=2)

        p = re.compile(u"^[a-zA-Z0-9!-/:-@[-`{-~]+$")
    
        return p.match(replaced) is not None

    delimiter = [u"。", u"？", u"！", u"?", u"!", u".", u"．", u"…"]

    # urlは<URL>タグに置き換え
    text = __mask_url(text)

    # 「...？」「...！」のように、かっこ内に含まれるdelimiterを一時的に特殊文字で置換
    text_masked, mask_info = __mask_delimiter(text)

    sents = []
    # delimiterで分割
    for par in text_masked:
        sents += filter(lambda s: len(s)>0, re.split(u'(。|？|！|\?|!|\.|．|…)', par))
    # リスト内に独立して存在するdelimiterをconcat [u"あいい", u"。", ...] -> [u"あいい。"]
    sents = concat_delimiter(sents, delimiter)
 
    # maskを戻す
    sents = sents if mask_info==None else demask_delimiter(sents, mask_info)

    # アルファベットのみの文は削除する
    sents = [s for s in sents if is_alphabet_only(s)==False]

    return map(lambda sent: sent.strip(), sents)
