# !/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

import re
import os
import csv

# Constants

regex_patterns_keep_contents = [
    '<a[^>]*?>(.*?)</a>',
    '<div[^>]*?class="closing">(.*?)</div>',
    '<div[^>]*?class="closingBlock">(.*?)</div>',
    '<div[^>]*?class="topic">(.*?)</div>',
    '<page-break[^>]*?>(.*?)</page-break>',
    '<span[^>]*?class="language[^>]*?emphasis"[^>]*?xml:lang="la">(.*?)</span>',
    '<span[^>]*?class="language[^>]*?>(.*?)</span>',
    '<span[^>]*?class="clarityWord">(.*?)</span>',
    '<span[^>]*?class="selah">(.*?)</span>',
    '<p[^>]*?class=""[^>]*?>(.*?)</p>',
    '<span[^>]*?class="">(.*?)</span>', # Added for Portugese
    '<span[^>]*?class="small">(.*?)</span>', # Added for Italian
    '<span>(.*?)</span>', # Added for Italian
]

regex_patterns_delete_contents = [
    '<sup[^>]*?class="studyNoteMarker">(.*?)</sup>',
    '<span[^>]*?class="verse">[0-9]</span>',
    '<div[^>]*?class="summary">(.*?)</div',
    '<h2>(.*?)</h2>',
    '<p>(.*?)</p>',
    '<span[^>]*?class="translit"[^>]*?xml:lang="he">(.*?)</span>',
]

tags_to_keep = [
    '<div eid="" words="2" class="signature">',
    '</div>',
    '<em>',
    '</em>',
    '<span class="allCaps">',
    '<span class="smallCaps">',
    '<span class="answer">',
    '<span class="question">',
    '<span class="line">',
    '</span>',
]

special_case_filenames = [
    'bofm-title?lang=spa',
    'eight?lang=spa',
    # 'introduction?lang=spa',
    #TODO: Uncomment above and delete line below this.
    'bofmintroduction?lang=spa',
    'three?lang=spa',
    'dcintroduction?lang=spa',
    'od1?lang=spa',
    'od2?lang=spa',
    '119?lang=spa',
    'fac-1?lang=spa',
    'fac-2?lang=spa',
    'fac-3?lang=spa',
]

special_case_remove_tags_keep_contents = [
    # '<div[^>]*?class="subtitle">(.*?)</div>',
    # '<div[^>]*?class="studyIntro">(.*?)</div>',
    '<span[^>]*?class="dominant">(.*?)</span>',
    '<div[^>]*?class="article"[^>]*?id="[^>]*?">(.*?)</div>',
    # '<div[^>]*?class="openingBlock">(.*?)</div>',
    # '<div[^>]*?class="closingBlock">(.*?)</div>',
    '<div[^>]*?class="closing">(.*?)</div>',
    '<span[^>]*?class="language[^>]*?>(.*?)</span>',
    # '<div[^>]*?class="topic">(.*?)</div>',
    # '<div[^>]*?class="addressee">(.*?)</div>',
    '<div[^>]*?class="preamble">(.*?)</div>',
    '<div[^>]*?class="figure">(.*?)</div>',
    # '<li[^>]*?>(.*?)</li>',

]

special_case_remove_tags_and_contents = [
    '<div[^>]*?id="media">(.*?)</div>',
    '<ul[^>]*?>(.*?)</ul>',
    '<li[^>]*?class="prev">(.*?)</li>',
    '<li[^>]*?class="next">(.*?)</li>',
    '<ul[^>]*?>',
    '<p>',
    '</p>',
    '<a[^>]*?href="[^>]*?"[^>]*?class="scriptureRef">',
    '<a[^>]*?>',
    '</a>',
    '<h2>',
    '</h2>',
    '<li>',
    '</li>',
]


def getVerses(path, fileName):
    with open('%s/%s' % (path, fileName), 'r') as html:
        data = html.read().replace('\n', ' ')

        if fileName in special_case_filenames:
            verses = re.search('<div\s+id="primary">(.*?)</ul>[^<]*?</div>', data).group(1)
            # print('------------------BEFORE CLEANING---------------------')
            # print(verses)

            # verses = re.sub('\s\s+', '', verses)

            for pattern in special_case_remove_tags_keep_contents:
                capture_group = re.search(pattern, verses)
                if capture_group:
                    verses = re.sub(pattern, capture_group.group(1), verses)

            for pattern in special_case_remove_tags_and_contents:
                verses = re.sub(pattern, '', verses)

            # verses = verses.strip('  ')
            # verses = verses.strip(' ')
            print('\n')
            print('%s/%s' % (path, fileName))
            print('------------- AFTER CLEANING: -----------------')
            print(verses)

            all_other_tags = re.findall('<[^>]*?>', verses)
            for tag in all_other_tags:
                if tag not in tags_to_keep:
                    print('%s/%s also contains %s' % (path, fileName, tag))


            with open('%s/%s.csv' % (path, fileName), 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['Verse', 'Text'])
                writer.writerow({'Verse': 1, 'Text': verses})

            return
        # try:
        #     if path.endswith('ps') and fileName == '119?lang=spa':
        #         verses = re.search('<div\s+class="verses"\s+id="[^"]*">(.+)</span></div>', data).group(1)
        #     elif fileName in special_case_filenames:
        #         print('in here')
        #         verses = re.search('<div[^>]*?id="primary">(.+)</ul></div>', data).group(1)
        #         print(verses)
        #     else:
        #         verses = re.search('<div\s+class="verses"\s+id="[^"]*">(.+?)</div>', data).group(1)
        # except AttributeError:
        #     #TODO: Process in special way for files with no verses (facsimilies, etc.)
        #     # BOFM title pages <div id="primary">
        #     print("Verses not found in %s/%s. Handling as special case." % (path, fileName))
        #     verses = 'ERROR: Verses not found in this file'


        # Get sub-string index for each verse number
        verse_number_locations = []
        for index in re.finditer('<span class="verse">', verses):
            verse_number_locations.append(index.end() + 1)

        # Get index for the beginning of each verse
        verse_text_end_locations = []
        for index in re.finditer('</p>', verses):
            verse_text_end_locations.append(index.start())

        # Get index for the end of each verse
        verse_text_start_locations = []
        for index in range(len(verse_number_locations)):
            location = verses.find('</span>', verse_number_locations[index])
            verse_text_start_locations.append(location + len('</span>'))

        verse_html = [] # To hold raw HTML for verse
        verse_texts = [] # To hold cleaned text for verse

        # Get raw HTML for verses
        for index in range(len(verse_number_locations)):
            verse_html.append(verses[verse_text_start_locations[index]:verse_text_end_locations[index]])

        # Clean HTML
        for index, verse in enumerate(verse_html):

            # Clean out tags where we want to keep the contents
            for pattern in regex_patterns_keep_contents:
                capture_group = re.search(pattern, verse)
                if capture_group:
                    verse = re.sub(pattern, capture_group.group(1), verse)

            # Remove other tags and their contents
            for pattern in regex_patterns_delete_contents:
                verse = re.sub(pattern, '', verse)

            # Check if there are any other html tags not accounted for
            all_other_tags = re.findall('<[^>]*?>', verse)
            for tag in all_other_tags:
                if tag not in tags_to_keep:
                    print('%s/%s also contains %s in verse %i' % (path, fileName, tag, index + 1))

            verse_texts.append(verse)

        with open('%s/%s.csv' % (path, fileName), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['Verse', 'Text'])
            for index, verse in enumerate(verse_texts):
                writer.writerow({'Verse': index + 1, 'Text': verse})

# ---------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------- COMMAND LINE INTERFACE ----------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------- #

# print('\nCurrently using \'spa\' for language code.  Change in script if desired.')
language_string = '?lang=spa'

# path_to_dir = input("\nPlease input the path to the directory you'd like to run this script against. (Enter '.' for current directory): ")

# if path_to_dir == '.':
#     print('\n-- The following are all chapter files in the current directory: --\n')
# else:
#     print('\n-- The following are all chapter files in the directory /%s: --\n' % path_to_dir)

# TODO: Uncomment above and delete this
path_to_dir = 'special'

for name in os.listdir(path_to_dir):
    if name.endswith(language_string):
        print(name)

if path_to_dir == '.':
    print('\n-- The current directory also contains the following sub-directories: --\n')
else:
    print('\n-- ' + path_to_dir  + ' also contains the following sub-directories: --\n')

print(next(os.walk(path_to_dir))[1])

choice = input(
    '\nWhat would you like to do?\n\n' +
    '(1) Run for one specific file in this directory\n' +
    '(2) Run for all files in this directory\n' +
    '(3) Run for all files in this directory, and all subdirectories\n' +
    '\nPlease enter 1, 2, or 3: '
)

while choice not in ['1', '2', '3']:
    choice = input('Please enter 1, 2, or 3: ')

if choice == '1':
    filename = input('\nWhat is the filename to convert to CSV: ')
    try:
        getVerses(path_to_dir, filename)
    except:
        print('Unable to convert: ' + path_to_dir + '/' + filename)

elif choice == '2':
    for name in os.listdir(path_to_dir):
        if name.endswith(language_string):
            # try:
            getVerses(path_to_dir, name)
            # except:
            #     print('Unable to convert: ' + path_to_dir + '/' + name)

elif choice == '3':
    for subdir, dirs, files in os.walk(path_to_dir):
        for file in files:
            if file.endswith(language_string):
                getVerses(subdir, file)


# TODO: Empty Garbage

    # capture_group = re.search('<a[^>]*?>(.*?)</a>', verse)
    # if capture_group:
    #     verse = re.sub('<a[^>]*?>(.*?)</a>', capture_group.group(1), verse)
    #
    # capture_group = re.search('<div[^>]*?class="closing">(.*?)</div>', verse)
    # if capture_group:
    #     verse = re.sub('<div[^>]*?class="closing">(.*?)</div>', capture_group.group(1), verse)
    #
    # capture_group = re.search('<div[^>]*?class="closingBlock">(.*?)</div>', verse)
    # if capture_group:
    #     verse = re.sub('<div[^>]*?class="closingBlock">(.*?)</div>', capture_group.group(1), verse)
    #
    # capture_group = re.search('<div[^>]*?class="topic">(.*?)</div>', verse)
    # if capture_group:
    #     verse = re.sub('<div[^>]*?class="topic">(.*?)</div>', capture_group.group(1), verse)
    #
    # capture_group = re.search('<page-break[^>]*?>(.*?)</page-break>', verse)
    # if capture_group:
    #     verse = re.sub('<page-break[^>]*?>(.*?)</page-break>', capture_group.group(1), verse)
    #
    # capture_group = re.search('<span[^>]*?class="language[^>]*?emphasis"[^>]*?xml:lang="la">(.*?)</span>', verse)
    # if capture_group:
    #     verse = re.sub('<span[^>]*?class="language[^>]*?emphasis"[^>]*?xml:lang="la">(.*?)</span>', capture_group.group(1), verse)
    #
    # capture_group = re.search('<span[^>]*?class="language[^>]*?>(.*?)</span>', verse)
    # if capture_group:
    #     verse = re.sub('<span[^>]*?class="language[^>]*?>(.*?)</span>', capture_group.group(1), verse)
    #
    # capture_group = re.search('<span[^>]*?class="clarityWord">(.*?)</span>', verse)
    # if capture_group:
    #     verse = re.sub('<span[^>]*?class="clarityWord">(.*?)</span>', capture_group.group(1), verse)
    #
    # capture_group = re.search('<span[^>]*?class="selah">(.*?)</span>', verse)
    # if capture_group:
    #     verse = re.sub('<span[^>]*?class="selah">(.*?)</span>', capture_group.group(1), verse)
    #
    # capture_group = re.search('<p[^>]*?class=""[^>]*?>(.*?)</p>', verse)
    # if capture_group:
    #     verse = re.sub('<p[^>]*?class=""[^>]*?>(.*?)</p>', capture_group.group(1), verse)
    #
    # verse = re.sub('<sup[^>]*?class="studyNoteMarker">[a-z]</sup>', '', verse)
    # verse = re.sub('<span[^>]*?class="verse">[0-9]</span>', '', verse)
    # verse = re.sub('<div[^>]*?class="summary">(.*?)</div', '', verse)
    # verse = re.sub('<h2>(.*?)</h2>', '', verse)
    # verse = re.sub('<p>(.*?)</p>', '', verse)
    # verse = re.sub('<span[^>]*?class="translit"[^>]*?xml:lang="he">(.*?)</span>','', verse)
