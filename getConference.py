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
# ----------------------------------------------------  CONSTANTS  ----------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------- #


# Change this for additional languages
language_code = '?lang=spa'


# To factor out magic strings
options = {
    'fileOpenMode': 'r',
    'bs4RunMode': 'html.parser',
    'fileWriteMode': 'w',
    'outputFileType': '.txt',
    'confContainerDivSelector': '.article-content',
}

# ---------------------------------------------------------------------------------------------------------------------- #
# -----------------------------------------------------  HELPERS  ------------------------------------------------------ #
# ---------------------------------------------------------------------------------------------------------------------- #




# Returns the containing block of text in list form
def getTalkBlock(fileName, container_selector):
    with open(fileName + language_code, options['fileOpenMode']) as html:
        raw_html = html.read()

    soup = bs4.BeautifulSoup(raw_html, options['bs4RunMode'])

    return soup.select(container_selector)


# Writes talk content out to file of type specified in options dictionary (Default is .txt)
def writeToFile(fileName, talk_content):
    file = open(fileName + language_code + options['outputFileType'], options['fileWriteMode'])
    file.write(str(talk_content))
    file.close()


# ---------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------  COMMAND-LINE  --------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------- #

fileName = sys.argv[1]

talk_html = getTalkBlock(fileName, options['confContainerDivSelector'])

writeToFile(fileName, talk_html)
