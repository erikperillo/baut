import csv

def transposeRawTable(raw_table):
    """input: list of lists of strings"""
    return [[line[i] for line in raw_table] for i in range(len(raw_table[0]))]

def getRawTable(filename, delim=","):
    """input: string"""
    with open (filename, "r") as f:
        reader = csv.reader(f, delimiter=delim)
        raw_table = [col for col in reader]

    return raw_table

class Table:
    def __init__(self, source, header=True):
        if isinstance(source, str):
            raw_table = transposeRawTable(getRawTable(source))
        else:
            raw_table = transposeRawTable(source)

        if header:
            self._data = dict((col[0], col[1:]) for col in raw_table)
        else:
            self._data = raw_table

    def __getitem__(self, specifier):
        return self._data[specifier]
