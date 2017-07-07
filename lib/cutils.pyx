# distutils: language = c++
# coding=utf-8

from libcpp.string cimport string
from libcpp.vector cimport vector

def get_idx(string case):

    return [int(e[:e.find(":")])-1 for e in case.split(" ") if ("qid" in e)==False and (":" in e)==True]
