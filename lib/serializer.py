# coding=utf-8

import cPickle
import gzip

class Serializer:
   
    @staticmethod
    def dump_data(frms, file_path, suffix=".pkl.gz"):
        """ dump data to file_path using cPickle
        Params:
            frms(list): dump data
            file_path(str): path to dump
        """
        with gzip.open(file_path, 'wb') as gf:
            [cPickle.dump(frm, gf, cPickle.HIGHEST_PROTOCOL) for frm in frms]
        
    @staticmethod
    def load_data(file_path):
        """ load dump data from file_path
        Params:
            file_path(str): path for load
        """
        data = []
        with gzip.open(file_path, 'rb') as gf:
            while True:
                try:
                    data.append(cPickle.load(gf))
                except EOFError:
                    break
        return data[0] if len(data)==1 else data
