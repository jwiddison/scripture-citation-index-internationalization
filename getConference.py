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
    'liahonaContainerDivSelector': '#content',
    'confFolder': 'crawl-es-conference',
    'liahonaFolder': 'crawl-es-liahona'
}

template_dom = [
    '<div id="talkcontent"><div class="nano"><div id="talkwrapper" class="nano-content" tabindex="0"><div id="content" class="two-col"><div id="bottom-gradient"><div id="details" class="clearfix">',
    'INSERT H1',
    '<h2 class="author"><div class="byline" id="">',
    'INSERT 2 Ptags for author',
    '</div></h2><hr></div><!-- end #details --><div id="primary"><blockquote class="intro dontHighlight"><a href="javascript:void(0);" target="_blank" class="nolink"><img id="talkPhoto" src="images/cache/thomas-s-monson-10.jpg" alt="Thomas S. Monson" class="img-decor"></a></blockquote>',
    'INSERT ARITICLE-ID',
    '<div class="figure"></div>',
    'INSERT Ptags for Talk'
    '</div><!-- end #primary --><!-- end #secondary --></div></div></div><div class="nano-pane" style="display: block;"><div class="nano-slider" style="height: 65px; transform: translate(0px, 0px);"></div></div></div></div>'
]

# ---------------------------------------------------------------------------------------------------------------------- #
# -----------------------------------------------------  HELPERS  ------------------------------------------------------ #
# ---------------------------------------------------------------------------------------------------------------------- #


# Cleans tag out of soup
def cleanSoup(content_soup):

    # Clean out all the comments first
    for p in content_soup.findAll(text=lambda text:isinstance(text, bs4.Comment)):
        p.extract()

    for p in content_soup('ul'):
        p.decompose()
    for p in content_soup('div', {'class' : 'lumen-template-read'}):
        p.unwrap()
    for p in content_soup('div', {'id' : 'details'}):
        p.unwrap()
    for p in content_soup('div', {'id': 'bottom-gradient'}):
        p.unwrap()
    for p in content_soup('div', {'class': 'primary-article'}):
        p.unwrap()
    for p in content_soup('section', {'class': 'author'}):
        p.unwrap()
    for p in content_soup('figure', {'class': 'head-shot'}):
        p.unwrap()
    for p in content_soup('noscript'):
        p.decompose()
    # There is weird white-space in the <h1> titles, this fixes it
    for p in content_soup('h1'):
        foo = str(p)
        capture_group = re.search('<h1>(\s+)(.*?)(\s+)</h1>', foo)

        if capture_group:
            foo = re.sub('<h1>(\s+)(.*?)(\s+)</h1>', '<h1>%s</h1>' % capture_group.group(2), foo)

        p.replace_with(foo)
    for p in content_soup('a'):
        p.unwrap()
    for p in content_soup('section', {'class': 'sash-icons'}):
        p.decompose()
    for p in content_soup('div', {'id': 'audio-player'}):
        p.decompose()
    for p in content_soup('div', {'class': 'figure'}):
        p.unwrap()
    for p in content_soup('span', {'class': 'emphasis'}):
        p.decompose()
    for p in content_soup('p', {'class': 'intro'}):
        p.decompose()

def buildDOM(soup):
    


# Fixes whitespace issues after cleaning
def fixSoupWhiteSpace(cleaned_string):
    cleaned_string = re.sub('\n\n', '\n', cleaned_string)
    cleaned_string = re.sub('\n\s', '\n', cleaned_string)
    cleaned_string = re.sub('^\s+', '', cleaned_string)
    # cleaned_string = re.sub('<!--[.*?]-->', '', cleaned_string)
    cleaned_string = re.sub('\n\n', '\n', cleaned_string)
    cleaned_string.strip()
    return cleaned_string


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

    page_soup = bs4.BeautifulSoup(markup, options['bs4RunMode'])

    # Find the containing element for talk
    talk = page_soup.select(container_selector)

    # Build what we found back into a string and make a new soup out of it
    talk_soup = bs4.BeautifulSoup(convertSoupToString(talk), options['bs4RunMode'])

    cleanSoup(talk_soup)

    buildDOM(talk_soup)

    # Turn soup back into string so we can use some REGEX to clean
    cleaned_string = convertSoupToString(talk_soup)

    # Use REGEX to clean up white-space issues
    cleaned_string = fixSoupWhiteSpace(cleaned_string)

    # Write results out to a file
    writeToFile(path, fileName, cleaned_string)


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

    # try:
    if path.startswith(options['confFolder']):
        extractTalkContent(path, fileName, options['confContainerDivSelector'])
    elif path.startswith(options['liahonaFolder']):
        extractTalkContent(path, fileName, options['liahonaContainerDivSelector'])
        print('%s/%s DONE' % (path, fileName), file=sys.stderr)
    # except:
    #     print('>>>>>>>>>>>>>>>> Unable to convert: %s/%s' % (path, fileName), file=sys.stderr)

elif run_mode == '2':
    for fileName in os.listdir(path):
        if fileName.endswith(language_code):
            try:
                if path.startswith(options['confFolder']):
                    extractTalkContent(path, fileName, options['confContainerDivSelector'])
                elif path.startswith(options['liahonaFolder']):
                    extractTalkContent(path, fileName, options['liahonaContainerDivSelector'])
                print('%s/%s DONE' % (path, fileName), file=sys.stderr)
            except:
                print('>>>>>>>>>>>>>>>> Unable to convert: %s/%s' % (path, fileName), file=sys.stderr)

elif run_mode == '3':
    for subdir, dirs, files in os.walk(path):
        for fileName in files:
            if fileName.endswith(language_code):
                # try:
                if path.startswith(options['confFolder']):
                    extractTalkContent(subdir, fileName, options['confContainerDivSelector'])
                elif path.startswith(options['liahonaFolder']):
                    extractTalkContent(subdir, fileName, options['liahonaContainerDivSelector'])
                #     print('%s/%s DONE' % (subdir, fileName), file=sys.stderr)
                # except:
                #     print('>>>>>>>>>>>>>>>> Unable to convert: %s/%s' % (subdir, fileName), file=sys.stderr)
