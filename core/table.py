import re

def transposeRawTable(raw_table):
    """input: list of lists of strings"""
    return [[line[i] for line in raw_table] for i in range(len(raw_table[0]))]

def getRawTable(filename, delim=",", comment_pattern="#"):
    """input: string"""
    with open (filename, "r") as f:
        raw_table = [re.split(r"(?<!\\)" + delim, line.rstrip())
                     for line in f if line and not line.startswith(comment_pattern)]
    return raw_table

class Table:
    def __init__(self, source, header=True, delim=","):
        if isinstance(source, str):
            raw_table = transposeRawTable(getRawTable(source, delim))
        else:
            raw_table = transposeRawTable(source)

        if header:
            self._data = [((i, col[0]), col[1:]) for i, col in enumerate(raw_table)]
        else:
            self._data = raw_table

        self.header = header

    def __getitem__(self, specifier):
        if self.header:
            for keys, vals in self._data:
                if specifier in keys:
                    return vals
        else:
            return self._data[specifier]

    def __len__(self):
        return len(self._data)

    def transposed(self, header=False):
        if self.header:
            source = [[name] + vals for name, vals in self]
        else:
            source = self._data
        
        return Table(source, header=header)

    def __iter__(self):
        if self.header:
            for i in xrange(len(self._data)):
                yield self._data[i][0][1], self._data[i][1]
        else:
            for val in self._data:
                yield val

if __name__ == "__main__":
    getRawTable("../states.csv")
