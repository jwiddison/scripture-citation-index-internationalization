# !/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

import re
import os
import csv

# ---------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------  CONSTANTS ------------------------------------------------------ #
# ---------------------------------------------------------------------------------------------------------------------- #

# These are the filenames for table of contents files, and we don't need to convert those.
toc_files_to_skip = [
    'bible?lang=spa',
    'bofm?lang=spa',
    'dc-testament?lang=spa',
    'pgp?lang=spa',
]

# These are all the patterns we want remove without removing their contents.
general_patterns_keep_contents = [
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
    '<a[^>]*?>',
    '</a>',
]

# All the tags that should be left over after cleaning
tags_to_keep = [
    # Signatures for 3 Witnesses
    '<div eid="2" words="2" class="signature">', '<div eid="3" words="2" class="signature">', '<div eid="4" words="2" class="signature">',
    # Signatures for 8 Witnesses
    '<div eid="4" words="3" class="signature">','<div eid="5" words="2" class="signature">','<div eid="5" words="3" class="signature">',
    '<div eid="6" words="2" class="signature">','<div eid="7" words="3" class="signature">','<div eid="8" words="2" class="signature">',
    '<div eid="9" words="2" class="signature">',
    # For OD 1
    '<div eid="1" words="3" class="salutation">', '<div eid="7" words="2" class="signature">',
    '<div eid="8" words="13" class="office">', '<div eid="7" words="2" class="signature">',
    # For OD 2
    '<div eid="7" words="2" class="salutation">','<div eid="13" words="2" class="signature">','<div eid="14" words="3" class="signature">',
    '<div eid="15" words="2" class="signature">','<div eid="16" words="3" class="office">','<div eid="13" words="2" class="signature">',
    '</div>',
    # For Facsimilies
    '<img src="http://lds.org/scriptures/bc/scriptures/content/english/bible-maps/images/03990_000_fac-1.jpg" alt="Facsímile Nº 1" width="408" height="402">',
    '<img src="http://lds.org/scriptures/bc/scriptures/content/english/bible-maps/images/03990_000_fac-2.jpg" alt="Facsímile Nº 2" width="408" height="402">',
    '<img src="http://lds.org/scriptures/bc/scriptures/content/english/bible-maps/images/03990_000_fac-3.jpg" alt="Facsímile Nº 3" width="408" height="402">',
    # Other
    '<em>','</em>',
    '<span class="allCaps">',
    '<span class="smallCaps">',
    '<span class="answer">',
    '<span class="question">',
    '<span class="line">',
    '</span>',
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


def checkForRemainingTagsForSpecialCase(verses_block, path, fileName):
    all_other_tags = re.findall('<[^>]*?>', verses_block)
    for tag in all_other_tags:
        if tag not in tags_to_keep:
            print('%s/%s also contains %s' % (path, fileName, tag))


def checkForRemainingTags(verse_to_check, index, path, fileName):
    all_other_tags = re.findall('<[^>]*?>', verse_to_check)
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


def getVerses(path, fileName):

    ### Properties ###

    verse_number_locations = [] # Holds the index of the verse numbers
    verse_text_start_locations = [] #Holds the substring index where verses start
    verse_text_end_locations = [] # Holds the substring index where verses end
    verse_html = [] # Holds raw Html for split verses
    verse_texts = [] # Holds finished cleaned text for verses

    with open('%s/%s' % (path, fileName), 'r') as html:
        data = html.read().replace('\n', ' ')

        # Skip Table of Contents files for each volume
        if fileName in toc_files_to_skip:
            return

        # Handle Special Cases
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

        elif path.endswith('bofm') and fileName == 'introduction?lang=spa':
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

        elif path.endswith('dc-testament') and fileName == 'introduction?lang=spa':
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

        elif path.endswith('od') and fileName == "1?lang=spa":
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

        elif path.endswith('od') and fileName == "2?lang=spa":
            verses = re.search('<div\s+id="primary">(.*?)</ul>[^<]*?</div>', data).group(1)

            od_2_keep_contents = [
                '<h2>(.*?)</h2>',
                '<div[^>]*?class="studyIntro">(.*?)</div>',
                '<div[^>]*?class="addressee">(.*?)</div>',
                '<div[^>]*?class="article"[^>]*?id="[^>]*?">(.*?)</div>',
                '<div[^>]*?class="closing">(.*?)</div>',
                '<div[^>]*?class="closingBlock">(.*?)</div>',
                '<div[^>]*?class="openingBlock">(.*?)</div>',

            ]

            od_2_remove_contents = [
                '<div[^>]*?id="media">(.*?)</div>',
                '<a[^>]*?name="p[0-9]*?"[^>]*?class="bookmark[^>]*?dontHighlight">(.*?)</a>',
                '<a[^>]*?href="[^>]*?"[^>]*?class="scriptureRef">',
                '</a>',
                '<p>','</p>',
                '<li[^>]*?class="prev">(.*?)</li>',
                '<li[^>]*?class="next">(.*?)</li>',
                '<ul[^>]*?>',
            ]

            verses = cleanVerse(od_2_keep_contents, od_2_remove_contents, verses)
            checkForRemainingTagsForSpecialCase(verses, path, fileName)
            writeToCsvSpecialCase(path, fileName, verses)
            return

        elif fileName == "fac-1?lang=spa":
            verses = re.search('<div\s+id="primary">(.*?)</div>', data).group(1)

            fac_1_keep_contents = [
                '<table\s+class="definition">(.*?)</table>',
            ]

            fac_1_remove_contents = [
                '<page-break[^>]*?page="32"></page-break>',
                '<div[^>]*?class="verses\s+maps">',
                '<p>','</p>',
                '<div[^>]*?class="figure">',
                '<td>','</td>',
                '<tr>','</tr>',
                '<h2>','</h2>',
            ]

            # Insert http://lds.org/scriptures/bc into image src. (Full img tag copied from existing tag in english database, but alt attribute changed to spanish version)
            verses = re.sub('<img[^>]*?>', '<img src="http://lds.org/scriptures/bc/scriptures/content/english/bible-maps/images/03990_000_fac-1.jpg" alt="Facsímile Nº 1" width="408" height="402">', verses)
            verses = cleanVerse(fac_1_keep_contents, fac_1_remove_contents, verses)
            checkForRemainingTagsForSpecialCase(verses, path, fileName)
            writeToCsvSpecialCase(path, fileName, verses)
            return

        elif fileName == "fac-2?lang=spa":
            verses = re.search('<div\s+id="primary">(.*?)</ul>[^>]*?</div>', data).group(1)

            fac_2_keep_contents = [
                '<table\s+class="definition">(.*?)</table>',
                '<div[^>]*?class="figure">(.*?)</div>',
            ]

            fac_2_remove_contents = [
                '<page-break[^>]*?page="40"></page-break>',
                '<div[^>]*?class="verses\s+maps">',
                '<wbr></wbr>',
                '<p\s+uri="[^>]*?"\s+class="">',
                '<p>','</p>',
                '<td>','</td>',
                '<tr>','</tr>',
                '<h2>','</h2>',
                '<li[^>]*?class="prev">(.*?)</li>',
                '<li[^>]*?class="next">(.*?)</li>',
                '<ul[^>]*?>',
                '</div>',
            ]

            # Insert http://lds.org/scriptures/bc into image src. (Full img tag copied from existing tag in english database, but alt attribute changed to spanish version)
            verses = re.sub('<img[^>]*?>', '<img src="http://lds.org/scriptures/bc/scriptures/content/english/bible-maps/images/03990_000_fac-2.jpg" alt="Facsímile Nº 2" width="408" height="402">', verses)
            verses = cleanVerse(fac_2_keep_contents, fac_2_remove_contents, verses)
            checkForRemainingTagsForSpecialCase(verses, path, fileName)
            writeToCsvSpecialCase(path, fileName, verses)
            return

        elif fileName == "fac-3?lang=spa":
            verses = re.search('<div\s+id="primary">(.*?)</ul>[^>]*?</div>', data).group(1)

            fac_3_keep_contents = [
                '<table\s+class="definition">(.*?)</table>',
                '<div[^>]*?class="figure">(.*?)</div>',
            ]

            fac_3_remove_contents = [
                '<a[^>]*?href="[^>]*?"[^>]*?class="scriptureRef">',
                '</a>',
                '<page-break[^>]*?page="47"></page-break>',
                '<div[^>]*?class="verses\s+maps">',
                '<p\s+uri="[^>]*?"\s+class="">',
                '<p>','</p>',
                '<td>','</td>',
                '<tr>','</tr>',
                '<h2>','</h2>',
                '<li[^>]*?class="prev">(.*?)</li>',
                '<li[^>]*?class="next">(.*?)</li>',
                '<ul[^>]*?>',
                '</div>',
            ]

            # Insert http://lds.org/scriptures/bc into image src. (Full img tag copied from existing tag in english database, but alt attribute changed to spanish version)
            verses = re.sub('<img[^>]*?>', '<img src="http://lds.org/scriptures/bc/scriptures/content/english/bible-maps/images/03990_000_fac-3.jpg" alt="Facsímile Nº 3" width="408" height="402">', verses)
            verses = cleanVerse(fac_3_keep_contents, fac_3_remove_contents, verses)
            checkForRemainingTagsForSpecialCase(verses, path, fileName)
            writeToCsvSpecialCase(path, fileName, verses)
            return

        elif path.endswith('ps') and fileName == "119?lang=spa":
            verses = re.search('<div\s+class="verses"\s+id="[^"]*">(.*?)</div>[^<]*?</div>', data).group(1)

            ps_119_pre_clean = [
                '<h2>(.*?)</h2>',
                '<div[^>]*?class="summary">(.*?)</div>',
                '<div[^>]*?class="topic">',
                '</div>',
                '<sup[^>]*?class="studyNoteMarker">(.*?)</sup>',
                '<a[^>]*?class="bookmark-anchor[^>]*?dontHighlight"[^>]*?name="[0-9]*?">(.*?)</a>',
                '<a[^>]*?class="footnote"[^>]*?href="[^>]*?"[^>]*?rel="[^>]*?">',
                '</a>',
                '<p[^>]*?class=""[^>]*?uri="[^>]*?">',
            ]

            for pattern in ps_119_pre_clean:
                verses = re.sub(pattern, '', verses)

            for index in re.finditer('<span class="verse">', verses):
                verse_number_locations.append(index.end() + 1)

            for index in re.finditer('</p>', verses):
                verse_text_end_locations.append(index.end())

            for index in re.finditer('<span class="verse">', verses):
                verse_text_start_locations.append(index.start())

            for index in range(len(verse_number_locations)):
                verse_html.append(verses[verse_text_start_locations[index]:verse_text_end_locations[index]])

            ps_119_keep_contents = [
                '<span[^>]*?class="clarityWord">(.*?)</span>',
            ]

            ps_119_remove_contents = [
                '</p>',
                '<span[^>]*?class="verse">[0-9]+[^<]*?</span>',
            ]

            for index, verse in enumerate(verse_html):
                verse = cleanVerse(ps_119_keep_contents, ps_119_remove_contents, verse)
                checkForRemainingTags(verse, index, path, fileName)
                verse_texts.append(verse)

            writeToCsv(path, fileName, verse_texts)

            return

        # Handle All Other Files Besides Special Cases
        else:
            try:
                verses = re.search('<div\s+class="verses"\s+id="[^"]*">(.+?)</div>', data).group(1)
            except AttributeError:
                print('Verses not found in %s/%s. Please Handle Manually' % (path, fileName))
                return

            # Get sub-string index for each verse number
            for index in re.finditer('<span class="verse">', verses):
                verse_number_locations.append(index.end() + 1)

            # Get index for the beginning of each verse
            for index in re.finditer('</p>', verses):
                verse_text_end_locations.append(index.start())

            # Get index for the end of each verse
            for index in range(len(verse_number_locations)):
                location = verses.find('</span>', verse_number_locations[index])
                verse_text_start_locations.append(location + len('</span>'))

            # Get raw HTML for verses using string slicing
            for index in range(len(verse_number_locations)):
                verse_html.append(verses[verse_text_start_locations[index]:verse_text_end_locations[index]])

            # Clean verse, check for other tags, and write cleaned text into verse_texts list
            for index, verse in enumerate(verse_html):
                verse = cleanVerse(general_patterns_keep_contents, general_patterns_remove_contents, verse)
                checkForRemainingTags(verse, index, path, fileName)
                verse_texts.append(verse)

            writeToCsv(path, fileName, verse_texts)


# ---------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------- COMMAND LINE INTERFACE ----------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------- #

language_string = '?lang=spa'

path_to_dir = input("\nPlease input the path to the directory you'd like to run this script against. (Enter '.' for current directory): ")

if path_to_dir == '.':
    print('\n-- The following are all chapter files in the current directory: --\n')
else:
    print('\n-- The following are all chapter files in the directory /%s: --\n' % path_to_dir)

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
        print('Unable to convert: %s/%s' % (path_to_dir, filename))

elif choice == '2':
    for name in os.listdir(path_to_dir):
        if name.endswith(language_string):
            try:
                getVerses(path_to_dir, name)
            except:
                print('Unable to convert: %s/%s' % (path_to_dir, name))

elif choice == '3':
    for subdir, dirs, files in os.walk(path_to_dir):
        for file in files:
            if file.endswith(language_string):
                try:
                    getVerses(subdir, file)
                    # TODO: DO you want confirmation a chapter worked or not?
                    print('%s/%s DONE' % (subdir, file))
                except:
                    print('Unable to convert: %s/%s' % (subdir, file))
