# coding=utf-8

from joblib import Parallel, delayed
from collections import Counter, defaultdict

class Ngrams():
    """ The class to create vocabulary of ngrams.
    The initializer generates uni-, bi-, tri-gram vocabulary, but you can generate arbitral N>=4 by calling the make_ngrams(N).
    """

    def __init__(self, text_paths, process_num, THR=10000):
        self.text_paths = text_paths # input text paths to generate ngram vocabs
        self.process_num = process_num # # of parallel process to generate ngram vocabs
        self.THR = THR # thr for vocabulary size
        self.univocab = self.make_ngrams(1)
        self.bivocab = self.make_ngrams(2)
        self.trivocab = self.make_ngrams(3)

    @staticmethod
    def ngramalize(self, tokens, N=1):
        """ generate ngram from tokens parameterized by N.
        Params:
            tokens(list): the list of str to generate Ngrams
            N(int): context size of Ngrams (e.g., N=1 -> unigram, N=2 -> bigram, N=3 -> trigram, ...)
        Returns:
            list: the list of ngrams. Ngrams are represented by str. Tokens are concated by '_'.
        """
        ngrams = []
        for i in xrange(len(tokens)+(-N+1)):
            ngrams.append(u"_".join(tokens[i:i+N]))
        return ngrams
    
    def _sub_make_ngrams(self, p, N):
        N = len(self.text_paths)
        ini = N * (p) / self.process_num
        fin = N * (p + 1) / self.process_num
   
        ngram_list = []
        for i in xrange(ini, fin):
            path = self.text_paths[i]
            sents = open(path).read().decode("utf-8", "ignore").split(u"\n")
            sents_tokens = [s.split(u"\t") for s in sents]
           
            # flatten
            ngram_list += [token for tokens in sents_tokens for token in Ngrams.ngramalize(tokens, N=N)]
    
        return Counter(ngram_list)
   
    def make_ngrams(self, N):
                
        callback = Parallel(n_jobs=self.process_num)(delayed(self._sub_make_ngrams)(i, N) for i in range(self.process_num))
        cnt = Counter()
        for _cnt in callback:
            cnt += _cnt

        # use ngrams that appeared more than self.THR times as vocabs.
        # ngrams = filter(lambda x: x[1]>=self.THR, cnt.most_common())

        # use ngrams that most common top_N(self.THR) as vocabs.
        ngrams = cnt.most_common()[:self.THR]
    
        # generate vocab from ngrams
        vocab = defaultdict(lambda: len(vocab))
        [vocab[tok[0]] for tok in ngrams]

        return vocab   
