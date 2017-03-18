#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3

import bs4    # Beautiful soup
import re     # Regular Expression Library
import sys    # To read command-line args


'''
    -----  Notes  ------

    I'm using bs4 (external package beautiful soup) instead of xml.etree.ElementTree
    because the built-in xml library can't read files with mismatched tags.  The scripture
    files I tested had mismatched tags, and wouldn't parse properly

    Useful Beautiful Soup stuff:
    - unwrap(): replaces the tag with the contents of the tag.  Good for stripping out markup
    - decompose(): completely removes the tag, and the contents
    - replace_with(): good for replacing tags with others
'''


# ---------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------  CONSTANTS  ----------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------- #


# Change this for additional languages
language_code = '?lang=spa'


# To factor out magic strings
options = {
    'fileOpenMode': 'r',
    'bs4RunMode': 'html.parser', # This is python's built-in html parser.  It's pretty forgiving with poorly formatted html
    'fileWriteMode': 'w',
    'outputFileType': '.txt',
    'confContainerDivSelector': '.article-content',
    'liahonaContainerDivSelector': '#primary',
}

# ---------------------------------------------------------------------------------------------------------------------- #
# -----------------------------------------------------  HELPERS  ------------------------------------------------------ #
# ---------------------------------------------------------------------------------------------------------------------- #


# Cleans tag out of soup
def cleanSoup(content_soup):
    for p in content_soup('p'):
        p.unwrap()
    for p in content_soup('a'):
        p.unwrap()
    for p in content_soup('div'):
        p.unwrap()
    for p in content_soup('span', {'id': 'article-id'}):
        p.decompose()
    for p in content_soup('span'):
        p.unwrap()
    for p in content_soup('ul'):
        p.decompose()

    # for p in content_soup('div', {'class' : 'stanza'}):
    #     p.unwrap()
    # for p in content_soup('div', {'class' : 'article-content'}):
    #     p.unwrap()
    # for p in content_soup('div', {'class' : 'poetry'}):
    #     p.unwrap()
    # for p in content_soup('div', {'class' : 'body-block'}):
    #     p.unwrap()


# Fixes whitespace issues after cleaning
def fixSoupWhiteSpace(cleaned_string):
    cleaned_string = re.sub('\n\n', '\n', cleaned_string)
    # This is called twice to fix places where 3 or more \n characters are found
    cleaned_string = re.sub('\n\n', '\n', cleaned_string)
    cleaned_string = re.sub('\n\s', '\n', cleaned_string)
    cleaned_string = re.sub('^\s+', '', cleaned_string)
    cleaned_string.strip()


# Converts a soup object to a string
def convertSoupToString(soup):
    temp_string = ''

    for tag in soup:
        temp_string += str(tag)

    return temp_string


# Returns the containing block of text in list form
def extractTalkContent(fileName, container_selector):
    with open(fileName + language_code, options['fileOpenMode']) as html:
        markup = html.read()

    # Add single whitespace between tags so there will be spaces between words when tags are removed
    markup = re.sub('><', '> <', markup)

    soup = bs4.BeautifulSoup(markup, options['bs4RunMode'])

    # Find the containing element for talk
    foo = soup.select(container_selector)

    # Build what we found back into a string
    bar = convertSoupToString(foo)

    # And make a new soup out of it
    content_soup = bs4.BeautifulSoup(bar, options['bs4RunMode'])

    cleanSoup(content_soup)

    bar = convertSoupToString(content_soup)

    fixSoupWhiteSpace(bar)

    return bar


# Writes talk content out to file of type specified in options dictionary (Default is .txt)
def writeToFile(fileName, talk_content):
    file = open(fileName + language_code + options['outputFileType'], options['fileWriteMode'])
    file.write(str(talk_content))
    file.close()


# ---------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------  COMMAND-LINE  --------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------- #

fileName = sys.argv[1]

if fileName.startswith('conf'):
    talk_html = extractTalkContent(fileName, options['confContainerDivSelector'])
elif fileName.startswith('liahona'):
    talk_html = extractTalkContent(fileName, options['liahonaContainerDivSelector'])

writeToFile(fileName, talk_html)
