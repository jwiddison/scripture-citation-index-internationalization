# !/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

import re
import os
import csv

# ---------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------  CONSTANTS ------------------------------------------------------ #
# ---------------------------------------------------------------------------------------------------------------------- #

# These are the table of contents files, and we don't need to convert those.
toc_files_to_skip = [
    'bible?lang=spa',
    'bofm?lang=spa',
    'dc-testament?lang=spa',
    'pgp?lang=spa',
]

# These are all the patterns we want remove without removing their contents.
general_patterns_keep_contents = [
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

# Patterns to delete where we don't want to keep their contents
general_patterns_remove_contents = [
    '<sup[^>]*?class="studyNoteMarker">(.*?)</sup>',
    '<span[^>]*?class="verse">[0-9]</span>',
    '<div[^>]*?class="summary">(.*?)</div',
    '<h2>(.*?)</h2>',
    '<p>(.*?)</p>',
    '<span[^>]*?class="translit"[^>]*?xml:lang="he">(.*?)</span>',
]

# All the tags that should be left over after cleaning
tags_to_keep = [
    # # Signatures for 3 Witnesses
    # '<div eid="2" words="2" class="signature">', '<div eid="3" words="2" class="signature">', '<div eid="4" words="2" class="signature">',
    # # Signatures for 8 Witnesses
    # '<div eid="4" words="3" class="signature">','<div eid="5" words="2" class="signature">','<div eid="5" words="3" class="signature">',
    # '<div eid="6" words="2" class="signature">','<div eid="7" words="3" class="signature">','<div eid="8" words="2" class="signature">',
    # '<div eid="9" words="2" class="signature">',
    # # For OD 1
    # '<div eid="1" words="3" class="salutation">', '<div eid="7" words="2" class="signature">',
    # '<div eid="8" words="13" class="office">', '<div eid="7" words="2" class="signature">',
    # # For OD 2
    #
    #
    # '</div>',
    # '<em>','</em>',
    # '<span class="allCaps">',
    # '<span class="smallCaps">',
    # '<span class="answer">',
    # '<span class="question">',
    # '<span class="line">',
    # '</span>',
]

# The filenames for each file that has to be processed individually.
special_case_filenames = [
    'bofm-title?lang=spa',
    'eight?lang=spa',
    'bofmintroduction?lang=spa',
    # 'introduction?lang=spa',
    #TODO: Uncomment above and delete line below this.
    'three?lang=spa',
    'dcintroduction?lang=spa',
    'od1?lang=spa',
    'od2?lang=spa',
    '119?lang=spa',
    'fac-1?lang=spa',
    'fac-2?lang=spa',
    'fac-3?lang=spa',
]

# The special-case tags for the 2 witnesses sections (they're the same)
witnesses_keep_contents = [
    '<div[^>]*?class="article"[^>]*?id="[^>]*?">(.*?)</div>',
    '<div[^>]*?class="closingBlock">(.*?)</div>',
]

witnesses_remove_contents = [
    '<a[^>]*?name="p[0-9]"[^>]*?class="bookmark[^>]*?dontHighlight">(.*?)</a>',
    '<div[^>]*?id="media">(.*?)</div>',
    '<li[^>]*?class="prev">(.*?)</li>',
    '<li[^>]*?class="next">(.*?)</li>',
    '<ul[^>]*?>',
    '<p>',
    '</p>',
]

# ---------------------------------------------------------------------------------------------------------------------- #
# -----------------------------------------------------  HELPERS  ------------------------------------------------------ #
# ---------------------------------------------------------------------------------------------------------------------- #

def cleanVerse(patterns_keep_contents, patterns_delete_contents, string_to_clean):
    for pattern in patterns_keep_contents:
        capture_group = re.search(pattern, string_to_clean)
        if capture_group:
            string_to_clean = re.sub(pattern, capture_group.group(1), string_to_clean)

    for pattern in patterns_delete_contents:
        string_to_clean = re.sub(pattern, '', string_to_clean)

    string_to_clean = re.sub('^\s\s+', '', string_to_clean) # Remove all leading whitespace

    return string_to_clean


def checkForRemainingTagsForSpecialCase(verse_to_check, path, fileName):
    all_other_tags = re.findall('<[^>]*?>', verse_to_check)
    for tag in all_other_tags:
        if tag not in tags_to_keep:
            print('%s/%s also contains %s' % (path, fileName, tag))

def checkFormRemainingTags(verse_to_check, index, path, fileName):
    all_other_tags = re.findall('<[^>]*?>', verse)
    for tag in all_other_tags:
        if tag not in tags_to_keep:
            print('%s/%s also contains %s in verse %i' % (path, fileName, tag, index + 1))


def writeToCsv(path, fileName, verse_texts):
    with open('%s/%s.csv' % (path, fileName), 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Verse', 'Text'])
        for index, verse in enumerate(verse_texts):
            writer.writerow({'Verse': index + 1, 'Text': verse})


def writeToCsvSpecialCase(path, fileName, verses):
    with open('%s/%s.csv' % (path, fileName), 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Verse', 'Text'])
        writer.writerow({'Verse': 1, 'Text': verses})

special_case_remove_tags_keep_contents = [
    # '<div[^>]*?class="studyIntro">(.*?)</div>',
    # '<span[^>]*?class="language[^>]*?>(.*?)</span>',
    # # '<div[^>]*?class="topic">(.*?)</div>',
    # # '<div[^>]*?class="addressee">(.*?)</div>',
    # '<div[^>]*?class="figure">(.*?)</div>',
    # # '<li[^>]*?>(.*?)</li>',

]


def getVerses(path, fileName):
    with open('%s/%s' % (path, fileName), 'r') as html:
        data = html.read().replace('\n', ' ')

        if fileName in toc_files_to_skip:
            return
        elif fileName in special_case_filenames:
            # if path.endswith('bofm') and fileName == 'bofm-title?lang=spa':
            if fileName == 'bofm-title?lang=spa':
                verses = re.search('<div\s+id="primary">(.*?)</ul>[^<]*?</div>', data).group(1)

                bofm_title_keep_contents = [
                    '<div[^>]*?class="article"[^>]*?id="[^>]*?">(.*?)</div>',
                    '<div[^>]*?class="subtitle">(.*?)</div>',
                    '<span[^>]*?class="dominant">(.*?)</span>',
                    '<div[^>]*?class="closingBlock">(.*?)</div>',
                    '<div[^>]*?class="closing">(.*?)</div>',
                ]

                bofm_title_remove_contents = [
                    '<a[^>]*?name="p[0-9]"[^>]*?class="bookmark[^>]*?dontHighlight">(.*?)</a>',
                    '<div[^>]*?id="media">(.*?)</div>',
                    '<li[^>]*?class="prev">(.*?)</li>',
                    '<li[^>]*?class="next">(.*?)</li>',
                    '<ul[^>]*?>',
                    '<p>',
                    '</p>',
                ]

                verses = cleanVerse(bofm_title_keep_contents, bofm_title_remove_contents, verses)
                checkForRemainingTagsForSpecialCase(verses, path, fileName)
                writeToCsvSpecialCase(path, fileName, verses)
                return

            elif fileName == 'bofmintroduction?lang=spa':
                verses = re.search('<div\s+id="primary">(.*?)</ul>[^<]*?</div>', data).group(1)

                bofm_intro_keep_contents = [
                    '<div[^>]*?class="article"[^>]*?id="[^>]*?">(.*?)</div>',
                ]

                bofm_intro_remove_contents = [
                    '<a[^>]*?name="p[0-9]"[^>]*?class="bookmark[^>]*?dontHighlight">(.*?)</a>',
                    '<a[^>]*?href="[^>]*?"[^>]*?class="scriptureRef">',
                    '</a>',
                    '<div[^>]*?id="media">(.*?)</div>',
                    '<li[^>]*?class="prev">(.*?)</li>',
                    '<li[^>]*?class="next">(.*?)</li>',
                    '<ul[^>]*?>',
                    '<p>',
                    '</p>',
                ]

                verses = cleanVerse(bofm_intro_keep_contents, bofm_intro_remove_contents, verses)
                checkForRemainingTagsForSpecialCase(verses, path, fileName)
                writeToCsvSpecialCase(path, fileName, verses)
                return

            elif fileName == 'three?lang=spa':
                verses = re.search('<div\s+id="primary">(.*?)</ul>[^<]*?</div>', data).group(1)
                verses = cleanVerse(witnesses_keep_contents, witnesses_remove_contents, verses)
                checkForRemainingTagsForSpecialCase(verses, path, fileName)
                writeToCsvSpecialCase(path, fileName, verses)
                return

            elif fileName == 'eight?lang=spa':
                verses = re.search('<div\s+id="primary">(.*?)</ul>[^<]*?</div>', data).group(1)
                verses = cleanVerse(witnesses_keep_contents, witnesses_remove_contents, verses)
                checkForRemainingTagsForSpecialCase(verses, path, fileName)
                writeToCsvSpecialCase(path, fileName, verses)
                return

            elif fileName == 'dcintroduction?lang=spa':
                # TODO: Check and make sure this one is actually working.  Check text against itself.
                verses = re.search('<div\s+id="primary">(.*?)</p>[^<]*?</div>', data).group(1)

                dc_intro_keep_contents = [
                    '<span[^>]*?class="language[^>]*?emphasis"[^>]*?xml:lang="en">(.*?)</span>',
                    '<div[^>]*?class="article"[^>]*?id="[^>]*?">(.*?)</div>',
                    '<div[^>]*?id="media">(.*?)</div>',
                    '<div[^>]*?class="preamble">(.*?)</div>',
                    '<h2>(.*?)</h2>',

                ]

                dc_intro_remove_contents = [
                    '<a[^>]*?name="p[0-9]*?"[^>]*?class="bookmark[^>]*?dontHighlight">(.*?)</a>',
                    '<a[^>]*?href="[^>]*?"[^>]*?class="scriptureRef">',
                    '<div[^>]*?class="article"[^>]*?id="[^>]*?">',
                    '<div[^>]*?class="topic">',
                    '</a>',
                    '<p>','</p>',
                    '<li>','</li>',
                    '<ul[^>]*?>',
                ]

                verses = cleanVerse(dc_intro_keep_contents, dc_intro_remove_contents, verses)
                checkForRemainingTagsForSpecialCase(verses, path, fileName)
                writeToCsvSpecialCase(path, fileName, verses)
                return

            elif fileName == "od1?lang=spa":
                verses = re.search('<div\s+id="primary">(.*?)</p>[^<]*?</div>', data).group(1)

                od_1_keep_contents = [
                    '<span[^>]*?class="language[^>]*?emphasis"[^>]*?xml:lang="en">(.*?)</span>',
                    '<div[^>]*?class="article"[^>]*?id="[^>]*?">(.*?)</div>',
                    '<div[^>]*?class="openingBlock">(.*?)</div>',
                    '<div[^>]*?class="closingBlock">(.*?)</div>',
                    '<div[^>]*?class="studyIntro">(.*?)</div>',
                    '<h2>(.*?)</h2>',
                ]

                od_1_remove_contents = [
                    '<a[^>]*?name="p[0-9]*?"[^>]*?class="bookmark[^>]*?dontHighlight">(.*?)</a>',
                    '<a[^>]*?href="[^>]*?"[^>]*?class="scriptureRef">',
                    '</a>',
                    '<div[^>]*?class="topic">',
                    '<div[^>]*?id="media">(.*?)</div>',
                    '<p>','</p>',
                ]

                verses = cleanVerse(od_1_keep_contents, od_1_remove_contents, verses)
                checkForRemainingTagsForSpecialCase(verses, path, fileName)
                writeToCsvSpecialCase(path, fileName, verses)
                return

            elif fileName == "od2?lang=spa":
                verses = re.search('<div\s+id="primary">(.*?)</ul>[^<]*?</div>', data).group(1)

                od_2_keep_contents = [
                    # '<span[^>]*?class="language[^>]*?emphasis"[^>]*?xml:lang="en">(.*?)</span>',
                    # '<div[^>]*?class="article"[^>]*?id="[^>]*?">(.*?)</div>',
                    # '<div[^>]*?class="openingBlock">(.*?)</div>',
                    # '<div[^>]*?class="closingBlock">(.*?)</div>',
                    '<h2>(.*?)</h2>',
                    '<div[^>]*?class="studyIntro">(.*?)</div>',
                    '<div[^>]*?class="article"[^>]*?id="[^>]*?">(.*?)</div>',
                ]

                od_2_remove_contents = [
                    '<div[^>]*?id="media">(.*?)</div>',
                    '<a[^>]*?name="p[0-9]*?"[^>]*?class="bookmark[^>]*?dontHighlight">(.*?)</a>',
                    '<a[^>]*?href="[^>]*?"[^>]*?class="scriptureRef">',
                    '</a>',
                    # '<div[^>]*?class="topic">',
                    '<p>','</p>',

                ]

                verses = cleanVerse(od_2_keep_contents, od_2_remove_contents, verses)
                print(verses)
                checkForRemainingTagsForSpecialCase(verses, path, fileName)
                writeToCsvSpecialCase(path, fileName, verses)
                return

            elif fileName == "fac1?lang=spa":
                return

            elif fileName == "fac2?lang=spa":
                return

            elif fileName == "fac3?lang=spa":
                return

            # elif path.endswith('ps') and fileName == "119?lang=spa":
            elif fileName == "119?lang=spa":
                return

        else:
            try:
                verses = re.search('<div\s+class="verses"\s+id="[^"]*">(.+?)</div>', data).group(1)
            except AttributeError:
                print('Verses not found in %s/%s. Please Handle Manually' % (path, fileName))
                return

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

            # Get raw HTML for verses using string slicing
            for index in range(len(verse_number_locations)):
                verse_html.append(verses[verse_text_start_locations[index]:verse_text_end_locations[index]])

            # Clean HTML
            for index, verse in enumerate(verse_html):
                verse = cleanVerse(general_patterns_keep_contents, general_patterns_remove_contents, verse)
                checkFormRemainingTags(verse, index, path, fileName)

                # # Check if there are any other html tags not accounted for
                # all_other_tags = re.findall('<[^>]*?>', verse)
                # for tag in all_other_tags:
                #     if tag not in tags_to_keep:
                #         print('%s/%s also contains %s in verse %i' % (path, fileName, tag, index + 1))


                verse_texts.append(verse)

            writeToCsv(path, fileName, verse_texts)

        # with open('%s/%s.csv' % (path, fileName), 'w') as csvfile:
        #     writer = csv.DictWriter(csvfile, fieldnames=['Verse', 'Text'])
        #     for index, verse in enumerate(verse_texts):
        #         writer.writerow({'Verse': index + 1, 'Text': verse})

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
