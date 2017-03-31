# coding=utf-8

import cPickle

class Pipe:
   
    @staticmethod
    def dump_data(frms, file_path):
        """ dump data to file_path using cPickle
        Params:
            frms(list): dump data
            file_path(str): path to dump
        """
        with open(file_path, 'w') as f:
            [cPickle.dump(frm, f) for frm in frms]
		
    @staticmethod
    def load_data(file_path):
        """ load dump data from file_path
        Params:
            file_path(str): path for load
		"""
        data = []
        with open(file_path) as f:
		    while True:
			    try:
				    data.append(cPickle.load(f))
			    except EOFError:
				    break
        return data[0] if len(data)==1 else data
