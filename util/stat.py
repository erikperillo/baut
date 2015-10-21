#!/usr/bin/python2.7

import math
import numpy
import scipy
import scipy.stats
import csv

GUARANTEED_MEASURES = ["mean", "std", "var", "sum", "prod", "ci"] 

def error(msg, ret_code=1):
    print "error: " + msg
    exit(ret_code)

def getConfidenceInterval(data, confidence=0.95):
    """
    assumes a normal distribution
    input: numpy.array
    """
    se = scipy.stats.sem(data)
    h = se * scipy.stats.t._ppf((1+confidence)/2., len(data)-1)
    return h

def getMeasure(data, measure, *args):
    """input: numpy.array"""
    if measure == "ci":
        return getConfidenceInterval(data, *args)
    return getattr(data, measure)()

def main():
    try:
        import oarg_exp as oarg
    except ImportError:
        import oarg
    import sys
    import os
    sys.path.append(os.path.join("..", "core"))
    import table as tb

    input_filename = oarg.Oarg("-i --input", "", "input file", 0)
    delimiter = oarg.Oarg("-d --delimiter", ",", "delimiter of each colummn in file")
    col_numbers = oarg.Oarg("-n --numbers", 0, "numbers of columns")
    col_names = oarg.Oarg("-N --names", "", "names of column to be analysed", single=False)
    measures = oarg.Oarg("-m --measures", "mean", "statistical measure(s) to make", single=False)
    header = oarg.Oarg("-H --header", False, "consider header in file")
    hlp = oarg.Oarg("-h --help", False, "this help message")

    oarg.parse(delim=":")

    if hlp.val:
        oarg.describeArgs("options:", def_val=True)
        exit()

    if not input_filename.found:
        error("no input file specified (use '-h' for help)") 

    #defining specifier
    specifiers = col_numbers.vals if not col_names.found else col_names.vals

    if col_names.found:
        header.val = True
        print ",".join("%s_%s" % (str(n), m) for n in col_names.vals for m in measures.vals)
    else:
        print ",".join("col_%d_%s" % (n, m) for n in col_numbers.vals for m in measures.vals)

    #creating table
    table = tb.Table(input_filename.val, header=header.val)

    results = []
    for specifier in specifiers:
        array = numpy.array(table[specifier], dtype=float)
        for measure in measures.vals:
            value = getMeasure(array, measure)
            results.append(str(value))

    print ",".join(results)

if __name__ == "__main__":
    main() 
