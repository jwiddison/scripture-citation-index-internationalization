#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3

import bs4    # Beautiful soup
import os     # Gives us access to file system to search for other files
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
    'confFolder': 'crawl-es-conference',
    'liahonaFolder': 'crawl-es-liahona'
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
def extractTalkContent(path, fileName, container_selector):
    with open(path + '/' + fileName, options['fileOpenMode']) as html:
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

    writeToFile(path, fileName, bar)


# Writes talk content out to file of type specified in options dictionary (Default is .txt)
def writeToFile(path, fileName, talk_content):
    file = open(path + '/' + fileName + options['outputFileType'], options['fileWriteMode'])
    file.write(str(talk_content))
    file.close()


# ---------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------  COMMAND-LINE  --------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------- #


# Check if there is a command-line parameter for the directory to run the script against
if len(sys.argv) > 1:
    path = sys.argv[1]

else:
    print("\nPlease enter the path to the directory you'd like to run this script against. (Enter '.' for current directory): ")
    path = input()

    if path == '.':
        print('\n-- The following are all talk files in the current directory: --\n')
    else:
        print('\n-- The following are all talk files in the directory /%s: --\n' % path)

    for name in os.listdir(path):
        if name.endswith(language_code):
            print(name)

    if path == '.':
        print('\n-- The current directory also contains the following sub-directories: --\n')
    else:
        print('\n-- ' + path  + ' also contains the following sub-directories: --\n')

    print(next(os.walk(path))[1])


# Check if there is a command-line parameter for the run_mode
if len(sys.argv) > 2:
    run_mode = sys.argv[2]

else:
    print(
        '\nWhat would you like to do?\n\n' +
        '(1) Run for one specific talk file in this directory\n' +
        '(2) Run for all talk files in this directory\n' +
        '(3) Run for all talk files in this directory, and all subdirectories\n' +
        '\nPlease enter 1, 2, or 3: '
    )
    run_mode = input()

    while run_mode not in ['1', '2', '3']:
        print('Please enter 1, 2, or 3: ')
        run_mode = input()

if run_mode == '1':
    # If the user specificies a single file, try to read it off the command line first
    if len(sys.argv) > 3:
        fileName = sys.argv[3]

    else:
        print('\n-- Files in the specified directory: --\n')
        for name in os.listdir(path):
            if name.endswith(language_code):
                print(name)
        print('\nWhich file would you like to convert?')
        fileName = input()

    try:
        if fileName.startswith(options['confFolder']):
            extractTalkContent(path, fileName, options['confContainerDivSelector'])
        elif fileName.startswith(options['liahonaFolder']):
            extractTalkContent(path, fileName, options['liahonaContainerDivSelector'])
        print('%s/%s DONE' % (path, fileName), file=sys.stderr)
    except:
        print('>>>>>>>>>>>>>>>> Unable to convert: %s/%s' % (path, fileName), file=sys.stderr)

elif run_mode == '2':
    for fileName in os.listdir(path):
        if fileName.endswith(language_code):
            try:
                if fileName.startswith(options['confFolder']):
                    extractTalkContent(path, fileName, options['confContainerDivSelector'])
                elif fileName.startswith(options['liahonaFolder']):
                    extractTalkContent(path, fileName, options['liahonaContainerDivSelector'])
                print('%s/%s DONE' % (path, fileName), file=sys.stderr)
            except:
                print('>>>>>>>>>>>>>>>> Unable to convert: %s/%s' % (path, fileName), file=sys.stderr)

elif run_mode == '3':
    for subdir, dirs, files in os.walk(path):
        for fileName in files:
            if fileName.endswith(language_code):
                print(fileName)
                # try:
                if fileName.startswith(options['confFolder']):
                    extractTalkContent(path, fileName, options['confContainerDivSelector'])
                elif fileName.startswith(options['liahonaFolder']):
                    extractTalkContent(path, fileName, options['liahonaContainerDivSelector'])
                #     print('%s/%s DONE' % (subdir, fileName), file=sys.stderr)
                # except:
                #     print('>>>>>>>>>>>>>>>> Unable to convert: %s/%s' % (subdir, fileName), file=sys.stderr)
