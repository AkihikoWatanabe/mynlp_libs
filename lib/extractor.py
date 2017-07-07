# coding=utf-8

import scipy.sparse as sp
import numpy as np
import re
from cutils import get_idx

# ToDo: リファクタリング
def sparse_data_format_to_index_dic(path, feature_num):
    def get_features(path):
        with open(path) as f:
            features = f.read().strip().split("\n")
        return features[:1000]

    x_dic = {}
    y_dic = {}
    features = get_features(path)
    qid_p = re.compile("qid:(\d+)")
    x_data, x_row_ind, x_col_ind = [], [], []
    y_list, past_qid, i = [], None, 0
    for case in features:
        # for qid
        m = qid_p.search(case)
        qid = int(m.group(1))

        if past_qid == None:
            past_qid = qid
        elif qid != past_qid:
            x_list = sp.csr_matrix((x_data, (x_row_ind, x_col_ind)), (len(y_list), feature_num))
            y_list = np.asarray(y_list, dtype=np.int8)
            x_dic[past_qid], y_dic[past_qid] = x_list, y_list
            # init
            x_data, x_row_ind, x_col_ind = [], [], []
            y_list, past_qid, i = [], qid, 0

        # for y
        label = 0 if case[0] == "0" else 1
        y_list.append(label)

        # for x
        feature_idx = get_idx(case)
        x_data += [1.0 for _ in xrange(len(feature_idx))]
        x_row_ind += [i for _ in xrange(len(feature_idx))]
        x_col_ind += feature_idx

        i += 1
                
    x_list = sp.csr_matrix((x_data, (x_row_ind, x_col_ind)), (len(y_list), feature_num))
    y_list = np.asarray(y_list, dtype=np.int8)
    x_dic[past_qid], y_dic[past_qid] = x_list, y_list

    return x_dic, y_dic

def sparse_data_format_to_index_list(path, feature_num, is_get_qid=False):
    y_list = []
    qid_list = []

    def get_features(path):
        with open(path) as f:
            features = f.read().strip().split("\n")
        return features

    features = get_features(path)
    qid_p = re.compile("qid:(\d+)")
    x_data, x_row_ind, x_col_ind = [], [], []
    for i, case in enumerate(features):
        # for y
        label = -1.0 if case[0] == "0" else 1.0
        y_list.append(label)

        # for x
        feature_idx = get_idx(case)
        x_data += [1.0 for _ in xrange(len(feature_idx))]
        x_row_ind += [i for _ in xrange(len(feature_idx))]
        x_col_ind += feature_idx

        # for qid
        if is_get_qid:
            m = qid_p.search(case)
            qid_list += [int(m.group(1))] if m!=None else []

    N = len(y_list)
    x_list = sp.csr_matrix((x_data, (x_row_ind, x_col_ind)), (N, feature_num))
    y_list = np.asarray(y_list, dtype=np.int8)
    qid_list = np.asarray(qid_list, dtype=np.int32)

    return x_list, y_list, qid_list
