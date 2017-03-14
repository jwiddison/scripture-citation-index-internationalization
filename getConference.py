#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3

import bs4                            #Beautiful soup
import sys                            #To read command-line args
# import xml.etree.ElementTree as ET    #For parsing XML documents


'''
    -----  Notes  ------ 

    I'm using bs4 (external package beautiful soup) instead of xml.etree.ElementTree
    because the built-in xml library can't read files with mismatched tags.  The scripture
    files I tested had mismatched tags, and wouldn't parse properly
'''


# ---------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------  CONSTANTS ------------------------------------------------------ #
# ---------------------------------------------------------------------------------------------------------------------- #


language_code = '?lang=spa'

options = {
    'fileOpenMode': 'r',
    'bs4RunMode': 'html.parser',
}





fileName = sys.argv[1]
with open(fileName + language_code, options['fileOpenMode']) as html:
    raw_html = html.read()

soup = bs4.BeautifulSoup(raw_html, options['bs4RunMode'])
print(soup)
