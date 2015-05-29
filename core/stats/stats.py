import numpy as np
import scipy.stats as sp

def mean(arr):
    try:
        return sum(arr) / float(len(arr))
    except ZeroDivisionError:
        return 0.0

def std(arr):
    return np.array(arr,dtype=np.float).std()

def var(arr):
    return np.array(arr,dtype=np.float).var()

def cin(arr, confidence=0.95):
    np_arr = np.array(arr,dtype=np.float)
    n = len(np_arr)
    sem = sp.sem(np_arr)
    cin = sem * sp.t._ppf((1+confidence)/2., n-1)
    return cin

ops = {"std":std, "mean":mean, "var":var, "cin":cin}
