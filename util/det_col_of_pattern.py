#!/usr/bin/python2.7

import sys

def main():
    if len(sys.argv) < 3:
        exit()
    
    header, pattern = sys.argv[1], sys.argv[2]

    try:
        print header.split(",").index(pattern) + 1
    except ValueError:
        print 0

if __name__ == "__main__":
    main()
