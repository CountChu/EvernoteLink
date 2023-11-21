# Jayme Woogerd
# Comp 116 - Security
# December 12, 2014

# This file implements a simple authentication
# system using the fuzzy vault algorithm.

# to use: python authenticate.py fingerprints/jayme

from vaults import vaults
from fuzzy_vault import (unlock, decode)
from sys import argv
import warnings

import pdb 
br = pdb.set_trace
known = ['jayme woogerd', 'norman ramsey', 'ming chow']

warnings.filterwarnings("ignore")

def main():
    with open(argv[1], 'r') as f:
        template = f.readlines()
        template = [float(t) for t in template]
        print('template = %s' % template)
        print('len(template) = %d' % len(template))

    for vault in vaults:
        coeffs = unlock(template, vault)
        print('coeffs = %s' % coeffs)
        print('len(coeffs) = %d' % len(coeffs))
        try:
            name = decode(coeffs)
            print('name = %s' % name)
            if name in known:
                print('Hello, %s!' % name.title())
                return
        except TypeError:
            pass
    print("Unknown user")

if __name__ == '__main__':
    main()

