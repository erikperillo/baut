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
    file_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(file_dir, ".."))
    import core.table as tb

    input_filename = oarg.Oarg("-i --input", "", "input file", 0)
    delimiter = oarg.Oarg("-d --delimiter", ",", "delimiter of each colummn in file")
    col_numbers = oarg.Oarg("-n --numbers", 0, "numbers of columns", single=False)
    col_names = oarg.Oarg("-N --names", "", "names of column to be analysed", single=False)
    all_cols = oarg.Oarg("-a --all-cols", False, "operates throught all collumns")
    measures = oarg.Oarg("-m --measures", "mean", "statistical measure(s) to make", single=False)
    has_header = oarg.Oarg("-H --header", False, "consider header in file")
    hlp = oarg.Oarg("-h --help", False, "this help message")

    oarg.parse(delim=":")

    if hlp.val:
        oarg.describeArgs("options:", def_val=True)
        exit()

    if not input_filename.found:
        error("no input file specified (use '-h' for help)") 

    #defining if there is header or not
    header = True if col_names.found else has_header.val

    #creating table
    table = tb.Table(input_filename.val, header=header)

    #defining specifier
    if all_cols.val:
        specifiers = range(len(table))
    else:
        specifiers = col_names.vals if col_names.found else col_numbers.vals

    if header:
        if col_names.found:
            names = col_names.vals
        else:
            names = [name for name, __ in table][0:len(table) if all_cols.val else 1]
        print ",".join("%s_%s" % (str(n), m) for n in names for m in measures.vals)
    else:
        print ",".join("col_%d_%s" % (n, m) for n in col_numbers.vals for m in measures.vals)

    results = []
    for specifier in specifiers:
        array = numpy.array(table[specifier], dtype=float)
        for measure in measures.vals:
            value = getMeasure(array, measure)
            results.append(str(value))

    print ",".join(results)

if __name__ == "__main__":
    main() 
