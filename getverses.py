#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3

# !/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

import re     # Pythons REGEX library
import os     # Gives us access to file system to search for other files
import csv    # Enables us to write results out to CSV files
import sys    # To redirect errors to STDERR, and be able to access command-line args

# ---------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------  CONSTANTS ------------------------------------------------------ #
# ---------------------------------------------------------------------------------------------------------------------- #

# Language code.  Change last 3 letters to run for a new language
language_code = '?lang=spa'

# URLs for the 3 images for the facimilies.  Will need to change alt tag for new languages
fac_1_img_url = '<img src="http://lds.org/scriptures/bc/scriptures/content/english/bible-maps/images/03990_000_fac-1.jpg" alt="Facsímile Nº 1" width="408" height="402">'
fac_2_img_url = '<img src="http://lds.org/scriptures/bc/scriptures/content/english/bible-maps/images/03990_000_fac-2.jpg" alt="Facsímile Nº 2" width="408" height="402">'
fac_3_img_url = '<img src="http://lds.org/scriptures/bc/scriptures/content/english/bible-maps/images/03990_000_fac-3.jpg" alt="Facsímile Nº 3" width="408" height="402">'


# These are the filenames for table of contents files, and we don't need to convert those.
toc_files_to_skip = [
    'bible%s' % language_code,
    'bofm%s' % language_code,
    'dc-testament%s' % language_code,
    'pgp%s' % language_code,
]

# All the html tags that should be left over after cleaning
tags_to_keep = [
    # Signatures for 3 Witnesses
    '<div eid="2" words="2" class="signature">',
    '<div eid="3" words="2" class="signature">',
    '<div eid="4" words="2" class="signature">',
    # Signatures for 8 Witnesses
    '<div eid="4" words="3" class="signature">',
    '<div eid="5" words="2" class="signature">',
    '<div eid="5" words="3" class="signature">',
    '<div eid="6" words="2" class="signature">',
    '<div eid="7" words="3" class="signature">',
    '<div eid="8" words="2" class="signature">',
    '<div eid="9" words="2" class="signature">',
    # For OD 1
    '<div eid="1" words="3" class="salutation">',
    '<div eid="7" words="2" class="signature">',
    '<div eid="8" words="13" class="office">',
    '<div eid="7" words="2" class="signature">',
    '<div eid="11" words="10" class="date">',
    # For OD 2
    '<div eid="7" words="2" class="salutation">',
    '<div eid="13" words="2" class="signature">',
    '<div eid="14" words="3" class="signature">',
    '<div eid="15" words="2" class="signature">',
    '<div eid="16" words="3" class="office">',
    '<div eid="13" words="2" class="signature">',
    '<div eid="19" words="9" class="date">',
    # For Facsimilies
    '<img src="http://lds.org/scriptures/bc/scriptures/content/english/bible-maps/images/03990_000_fac-1.jpg" alt="Facsímile Nº 1" width="408" height="402">',
    '<img src="http://lds.org/scriptures/bc/scriptures/content/english/bible-maps/images/03990_000_fac-2.jpg" alt="Facsímile Nº 2" width="408" height="402">',
    '<img src="http://lds.org/scriptures/bc/scriptures/content/english/bible-maps/images/03990_000_fac-3.jpg" alt="Facsímile Nº 3" width="408" height="402">',
    # Other
    '<div class="closingBlock">',
    '<em>',
    '</em>',
    '<span class="allCaps">',
    '<span class="smallCaps">',
    '<span class="answer">',
    '<span class="question">',
    '</span>',
    '</div>',
]

patterns = {
    # These are all the patterns we want remove without removing their contents.
    'standard_keep': [
        '<div[^>]*?class="closing">(.*?)</div>',
        '<div[^>]*?class="topic">(.*?)</div>',
        '<page-break[^>]*?>(.*?)</page-break>',
        '<span[^>]*?class="language[^>]*?emphasis"[^>]*?xml:lang="la">(.*?)</span>',
        '<span[^>]*?class="language[^>]*?>(.*?)</span>',
        '<span[^>]*?class="clarityWord">(.*?)</span>',
        '<span[^>]*?class="selah">(.*?)</span>',
        '<span[^>]*?class="line">(.*?)</span>',
        '<p[^>]*?class=""[^>]*?>(.*?)</p>',
        '<span[^>]*?class="">(.*?)</span>', # Added for Portugese
        '<span[^>]*?class="small">(.*?)</span>', # Added for Italian
        '<span>(.*?)</span>', # Added for Italian
    ],

    # Patterns to delete where we don't want to keep their contents
    'standard_remove': [
        '<sup[^>]*?class="studyNoteMarker">(.*?)</sup>',
        '<span[^>]*?class="verse">[0-9]</span>',
        '<div[^>]*?class="summary">(.*?)</div',
        '<h2>(.*?)</h2>',
        '<p>(.*?)</p>',
        '<span[^>]*?class="translit"[^>]*?xml:lang="he">(.*?)</span>',
        '<a[^>]*?>',
        '</a>',
    ],

    # The special-case tags for the BofM Title Page
    'bofm_title_keep': [
        '<div[^>]*?class="article"[^>]*?id="[^>]*?">(.*?)</div>',
        '<div[^>]*?class="subtitle">(.*?)</div>',
        '<span[^>]*?class="dominant">(.*?)</span>',
        '<div[^>]*?class="closing">(.*?)</div>',
    ],

    'bofm_title_remove': [
        '<a[^>]*?name="p[0-9]"[^>]*?class="bookmark[^>]*?dontHighlight">(.*?)</a>',
        '<div[^>]*?id="media">(.*?)</div>',
        '<li[^>]*?class="prev">(.*?)</li>',
        '<li[^>]*?class="next">(.*?)</li>',
        '<ul[^>]*?>',
        '<p>',
        '</p>',
    ],

    # The special-case tags for the BofM introduction
    'bofm_intro_keep': [
        '<div[^>]*?class="article"[^>]*?id="[^>]*?">(.*?)</div>',
    ],

    'bofm_intro_remove': [
        '<a[^>]*?name="p[0-9]"[^>]*?class="bookmark[^>]*?dontHighlight">(.*?)</a>',
        '<a[^>]*?href="[^>]*?"[^>]*?class="scriptureRef">',
        '</a>',
        '<div[^>]*?id="media">(.*?)</div>',
        '<li[^>]*?class="prev">(.*?)</li>',
        '<li[^>]*?class="next">(.*?)</li>',
        '<ul[^>]*?>',
        '<p>',
        '</p>',
    ],

    # The special-case tags for the 2 witnesses sections (they're the same)
    'witnesses_keep': [
        '<div[^>]*?class="article"[^>]*?id="[^>]*?">(.*)</div>',
    ],

    'witnesses_remove': [
        '<a[^>]*?name="p[0-9]"[^>]*?class="bookmark[^>]*?dontHighlight">(.*?)</a>',
        '<div[^>]*?id="media">(.*?)</div>',
        '<li[^>]*?class="prev">(.*?)</li>',
        '<li[^>]*?class="next">(.*?)</li>',
        '<ul[^>]*?>',
        '<p>',
        '</p>',
    ],

    # The special-case tags for the D&C Introduction
    'dc_intro_keep': [
        '<span[^>]*?class="language[^>]*?emphasis"[^>]*?xml:lang="en">(.*?)</span>',
        '<div[^>]*?class="article"[^>]*?id="[^>]*?">(.*?)</div>',
        '<div[^>]*?id="media">(.*?)</div>',
        '<div[^>]*?class="preamble">(.*?)</div>',
        '<h2>(.*?)</h2>',

    ],

    'dc_intro_remove': [
        '<a[^>]*?name="p[0-9]*?"[^>]*?class="bookmark[^>]*?dontHighlight">(.*?)</a>',
        '<a[^>]*?href="[^>]*?"[^>]*?class="scriptureRef">',
        '<div[^>]*?class="article"[^>]*?id="[^>]*?">',
        '<div[^>]*?class="topic">',
        '</a>',
        '<p>',
        '</p>',
        '<li>',
        '</li>',
        '<ul[^>]*?>',
    ],

    # The special-case tags for Official Declaration 1
    'od_1_keep': [
        '<span[^>]*?class="language[^>]*?emphasis"[^>]*?xml:lang="en">(.*?)</span>',
        '<div[^>]*?class="article"[^>]*?id="[^>]*?">(.*?)</div>',
        '<div[^>]*?class="openingBlock">(.*?)</div>',
        '<div[^>]*?class="studyIntro">(.*?)</div>',
        '<h2>(.*?)</h2>',
    ],

    'od_1_remove': [
        '<a[^>]*?name="p[0-9]*?"[^>]*?class="bookmark[^>]*?dontHighlight">(.*?)</a>',
        '<a[^>]*?href="[^>]*?"[^>]*?class="scriptureRef">',
        '</a>',
        '<div[^>]*?class="topic">',
        '<div[^>]*?id="media">(.*?)</div>',
        '<p>',
        '</p>',
    ],

    # The special-case tags for Official Declaration 2
    'od_2_keep': [
        '<h2>(.*?)</h2>',
        '<div[^>]*?class="studyIntro">(.*?)</div>',
        '<div[^>]*?class="addressee">(.*?)</div>',
        '<div[^>]*?class="article"[^>]*?id="[^>]*?">(.*?)</div>',
        '<div[^>]*?class="closing">(.*?)</div>',
        '<div[^>]*?class="openingBlock">(.*?)</div>',

    ],

    'od_2_remove': [
        '<div[^>]*?id="media">(.*?)</div>',
        '<a[^>]*?name="p[0-9]*?"[^>]*?class="bookmark[^>]*?dontHighlight">(.*?)</a>',
        '<a[^>]*?href="[^>]*?"[^>]*?class="scriptureRef">',
        '</a>',
        '<p>',
        '</p>',
        '<li[^>]*?class="prev">(.*?)</li>',
        '<li[^>]*?class="next">(.*?)</li>',
        '<ul[^>]*?>',
    ],

    # The special-case tags for Facsimile No 1
    'fac_1_keep': [
        '<table\s+class="definition">(.*?)</table>',
    ],

    'fac_1_remove': [
        '<page-break[^>]*?page="32"></page-break>',
        '<div[^>]*?class="verses\s+maps">',
        '<p>',
        '</p>',
        '<div[^>]*?class="figure">',
        '<td>',
        '</td>',
        '<tr>',
        '</tr>',
    ],

    # The special-case tags for Facsimile No 2
    'fac_2_keep': [
        '<table\s+class="definition">(.*?)</table>',
        '<div[^>]*?class="figure">(.*?)</div>',
    ],

    'fac_2_remove': [
        '<page-break[^>]*?page="40"></page-break>',
        '<div[^>]*?class="verses\s+maps">',
        '<wbr></wbr>',
        '<p\s+uri="[^>]*?"\s+class="">',
        '<p>',
        '</p>',
        '<td>',
        '</td>',
        '<tr>',
        '</tr>',
        '<li[^>]*?class="prev">(.*?)</li>',
        '<li[^>]*?class="next">(.*?)</li>',
        '<ul[^>]*?>',
        '</div>',
    ],

    # The special-case tags for Facsimile No 3
    'fac_3_keep': [
        '<table\s+class="definition">(.*?)</table>',
        '<div[^>]*?class="figure">(.*?)</div>',
    ],

    'fac_3_remove': [
        '<a[^>]*?href="[^>]*?"[^>]*?class="scriptureRef">',
        '</a>',
        '<page-break[^>]*?page="47"></page-break>',
        '<div[^>]*?class="verses\s+maps">',
        '<p\s+uri="[^>]*?"\s+class="">',
        '<p>',
        '</p>',
        '<td>',
        '</td>',
        '<tr>',
        '</tr>',
        '<li[^>]*?class="prev">(.*?)</li>',
        '<li[^>]*?class="next">(.*?)</li>',
        '<ul[^>]*?>',
        '</div>',
    ],

    # The special-case tags for JS-H
    'jsh_pre_clean': [
        '<a[^>]*?>',
        '</a>',
        '<sup[^>]*?class="studyNoteMarker">(.*?)</sup>',
        '<div[^>]*?class="summary">(.*?)</div>'
    ],

    # The special-case tags for Psalm 119
    'ps_119_pre_clean': [
        '<h2>(.*?)</h2>',
        '<div[^>]*?class="summary">(.*?)</div>',
        '<div[^>]*?class="topic">',
        '</div>',
        '<sup[^>]*?class="studyNoteMarker">(.*?)</sup>',
        '<a[^>]*?class="bookmark-anchor[^>]*?dontHighlight"[^>]*?name="[0-9]*?">(.*?)</a>',
        '<a[^>]*?class="footnote"[^>]*?href="[^>]*?"[^>]*?rel="[^>]*?">',
        '</a>',
        '<p[^>]*?class=""[^>]*?uri="[^>]*?">',
    ],

    'ps_119_keep': [
        '<span[^>]*?class="clarityWord">(.*?)</span>',
    ],

    'ps_119_remove': [
        '</p>',
        '<span[^>]*?class="verse">[0-9]+[^<]*?</span>',
        '<span[^>]*?class="line">',
        '</span>',
    ],

}


# ---------------------------------------------------------------------------------------------------------------------- #
# -----------------------------------------------------  HELPERS  ------------------------------------------------------ #
# ---------------------------------------------------------------------------------------------------------------------- #


def cleanVerse(patterns_keep, patterns_remove, string_to_clean):
    for pattern in patterns_keep:
        capture_group = re.search(pattern, string_to_clean)

        if capture_group:
            string_to_clean = re.sub(pattern, capture_group.group(1), string_to_clean)

    for pattern in patterns_remove:
        string_to_clean = re.sub(pattern, '', string_to_clean)

    # Remove all leading whitespace
    string_to_clean = re.sub('^\s\s+', '', string_to_clean)
    # Replace multiple spaces with one, and remove trailing whitespace
    string_to_clean = re.sub('\s+', ' ', string_to_clean).strip()

    return string_to_clean


def checkForRemainingTagsForSpecialCase(verses_block, path, fileName):
    all_other_tags = re.findall('<[^>]*?>', verses_block)

    # Because we left <h2></h2> in the facsimiles and nowhere else
    if fileName.startswith('fac'):
        tags_to_keep.append('<h2>')
        tags_to_keep.append('</h2>')

    for tag in all_other_tags:
        if tag not in tags_to_keep:
            print('>>>>>>>>>>>>>>>>>>> %s/%s also contains %s' % (path, fileName, tag), file=sys.stderr)


def checkForRemainingTags(verse_to_check, index, path, fileName):
    all_other_tags = re.findall('<[^>]*?>', verse_to_check)

    for tag in all_other_tags:
        if tag not in tags_to_keep:
            print('>>>>>>>>>>>>>>>>>>> %s/%s also contains %s in verse %i' % (path, fileName, tag, index + 1), file=sys.stderr)


def writeToCsv(path, fileName, verse_texts):
    with open('%s/%s.csv' % (path, fileName), 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Verse', 'Text'])

        for index, verse in enumerate(verse_texts):
            writer.writerow({'Verse': index + 1, 'Text': verse})


def writeToCsvSpecialCase(path, fileName, verses):
    with open('%s/%s.csv' % (path, fileName), 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Verse', 'Text'])
        writer.writerow({'Verse': 1, 'Text': verses})


def processStandardChapter(verses, path, fileName):
    verse_number_locations = [] # Holds the index of the verse numbers
    verse_text_start_locations = [] #Holds the substring index where verses start
    verse_text_end_locations = [] # Holds the substring index where verses end
    verse_html = [] # Holds raw Html for split verses
    verse_texts = [] # Holds finished cleaned text for verses

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
        verse = cleanVerse(patterns['standard_keep'], patterns['standard_remove'], verse)
        checkForRemainingTags(verse, index, path, fileName)
        verse_texts.append(verse)

    writeToCsv(path, fileName, verse_texts)
    return


def processSpecialCaseChapter(keep_list, remove_list, verses, path, fileName):
    verses = cleanVerse(keep_list, remove_list, verses)
    checkForRemainingTagsForSpecialCase(verses, path, fileName)
    writeToCsvSpecialCase(path, fileName, verses)


def fixFacsimileImgUrl(verses, new_url):
    return re.sub('<img[^>]*?>', new_url, verses)


def getVerses(path, fileName):

    ### Properties ###

    verse_number_locations = [] # Holds the index of the verse numbers
    verse_text_start_locations = [] #Holds the substring index where verses start
    verse_text_end_locations = [] # Holds the substring index where verses end
    verse_html = [] # Holds raw Html for split verses
    verse_texts = [] # Holds finished cleaned text for verses

    with open('%s/%s' % (path, fileName), 'r') as html:
        raw_html = html.read().replace('\n', ' ')

        # Skip Table of Contents files for each volume
        if fileName in toc_files_to_skip:
            return

        # Handle Special Cases
        if fileName == 'bofm-title%s' % language_code:
            verses = re.search('<div\s+id="primary">(.*?)</ul>[^<]*?</div>', raw_html).group(1)
            processSpecialCaseChapter(patterns['bofm_title_keep'], patterns['bofm_title_remove'], verses, path, fileName)
            return

        elif path.endswith('bofm') and fileName == 'introduction%s' % language_code:
            verses = re.search('<div\s+id="primary">(.*?)</ul>[^<]*?</div>', raw_html).group(1)
            processSpecialCaseChapter(patterns['bofm_intro_keep'], patterns['bofm_intro_remove'], verses, path, fileName)
            return

        elif fileName == 'three%s' % language_code:
            verses = re.search('<div\s+id="primary">(.*?)</ul>[^<]*?</div>', raw_html).group(1)
            processSpecialCaseChapter(patterns['witnesses_keep'], patterns['witnesses_remove'], verses, path, fileName)
            return

        elif fileName == 'eight%s' % language_code:
            verses = re.search('<div\s+id="primary">(.*?)</ul>[^<]*?</div>', raw_html).group(1)
            processSpecialCaseChapter(patterns['witnesses_keep'], patterns['witnesses_remove'], verses, path, fileName)
            return

        elif path.endswith('dc-testament') and fileName == 'introduction%s' % language_code:
            verses = re.search('<div\s+id="primary">(.*?)</p>[^<]*?</div>', raw_html).group(1)
            processSpecialCaseChapter(patterns['dc_intro_keep'], patterns['dc_intro_remove'], verses, path, fileName)
            return

        elif path.endswith('od') and fileName == '1%s' % language_code:
            verses = re.search('<div\s+id="primary">(.*?)</p>[^<]*?</div>', raw_html).group(1)
            processSpecialCaseChapter(patterns['od_1_keep'], patterns['od_1_remove'], verses, path, fileName)
            return

        elif path.endswith('od') and fileName == '2%s' % language_code:
            verses = re.search('<div\s+id="primary">(.*?)</ul>[^<]*?</div>', raw_html).group(1)
            processSpecialCaseChapter(patterns['od_2_keep'], patterns['od_2_remove'], verses, path, fileName)
            return

        elif fileName == 'fac-1%s' % language_code:
            verses = re.search('<div\s+id="primary">(.*?)</div>', raw_html).group(1)
            verses = fixFacsimileImgUrl(verses, fac_1_img_url)
            processSpecialCaseChapter(patterns['fac_1_keep'], patterns['fac_1_remove'], verses, path, fileName)
            return

        elif fileName == 'fac-2%s' % language_code:
            verses = re.search('<div\s+id="primary">(.*?)</ul>[^>]*?</div>', raw_html).group(1)
            verses = fixFacsimileImgUrl(verses, fac_2_img_url)
            processSpecialCaseChapter(patterns['fac_2_keep'], patterns['fac_2_remove'], verses, path, fileName)
            return

        elif fileName == 'fac-3%s' % language_code:
            verses = re.search('<div\s+id="primary">(.*?)</ul>[^>]*?</div>', raw_html).group(1)
            verses = fixFacsimileImgUrl(verses, fac_3_img_url)
            processSpecialCaseChapter(patterns['fac_3_keep'], patterns['fac_3_remove'], verses, path, fileName)
            return

        elif path.endswith('js-h') and fileName == '1%s' % language_code:
            verses = re.search('<div[^>]*?class="verses"[^>]*?id="0">(.*?)</div>[^>]*?<ul class="prev-next[^>]*?large">', raw_html).group(1)

            for pattern in patterns['jsh_pre_clean']:
                verses = re.sub(pattern, '', verses)

            processStandardChapter(verses, path, fileName)
            return

        elif path.endswith('ps') and fileName == '119%s' % language_code:
            verses = re.search('<div\s+class="verses"\s+id="[^"]*">(.*?)</div>[^<]*?</div>', raw_html).group(1)

            for pattern in patterns['ps_119_pre_clean']:
                verses = re.sub(pattern, '', verses)

            # Fix all multiple <span class="line"> instances by adding a space between them.
            verses = re.sub('</span><span[^>]*?class="line">', '</span> <span class="line">', verses)

            for index in re.finditer('<span class="verse">', verses):
                verse_number_locations.append(index.end() + 1)

            for index in re.finditer('</p>', verses):
                verse_text_end_locations.append(index.end())

            for index in re.finditer('<span class="verse">', verses):
                verse_text_start_locations.append(index.start())

            for index in range(len(verse_number_locations)):
                verse_html.append(verses[verse_text_start_locations[index]:verse_text_end_locations[index]])

            for index, verse in enumerate(verse_html):
                verse = cleanVerse(patterns['ps_119_keep'], patterns['ps_119_remove'], verse)
                checkForRemainingTags(verse, index, path, fileName)
                verse_texts.append(verse)

            writeToCsv(path, fileName, verse_texts)

            return

        # Handle All Other Files Besides Special Cases
        else:
            try:
                verses = re.search('<div\s+class="verses"\s+id="[^"]*">(.+?)</div>', raw_html).group(1)
            except AttributeError:
                print('>>>>>>>>>>>>>>>> Unable to get verses in file: %s/%s.' % (path, fileName), file=sys.stderr)
                return

            processStandardChapter(verses, path, fileName)



# ---------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------- COMMAND LINE INTERFACE ----------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------- #

# Check if there is a command-line parameter for the directory to run the script against
if len(sys.argv) > 1:
    path_to_dir = sys.argv[1]

else:
    print("\nPlease enter the path to the directory you'd like to run this script against. (Enter '.' for current directory): ")
    path_to_dir = input()

    if path_to_dir == '.':
        print('\n-- The following are all chapter files in the current directory: --\n')
    else:
        print('\n-- The following are all chapter files in the directory /%s: --\n' % path_to_dir)

    for name in os.listdir(path_to_dir):
        if name.endswith(language_code):
            print(name)

    if path_to_dir == '.':
        print('\n-- The current directory also contains the following sub-directories: --\n')
    else:
        print('\n-- ' + path_to_dir  + ' also contains the following sub-directories: --\n')

    print(next(os.walk(path_to_dir))[1])


# Check if there is a command-line parameter for the run_mode
if len(sys.argv) > 2:
    run_mode = sys.argv[2]

else:
    print(
        '\nWhat would you like to do?\n\n' +
        '(1) Run for one specific file in this directory\n' +
        '(2) Run for all files in this directory\n' +
        '(3) Run for all files in this directory, and all subdirectories\n' +
        '\nPlease enter 1, 2, or 3: '
    )
    run_mode = input()

    while run_mode not in ['1', '2', '3']:
        print('Please enter 1, 2, or 3: ')
        run_mode = input()

if run_mode == '1':
    print('\nWhat is the filename to convert to CSV: ')
    filename = input()
    try:
        getVerses(path_to_dir, filename)
    except:
        print('>>>>>>>>>>>>>>>> Unable to convert: %s/%s' % (path_to_dir, filename))

elif run_mode == '2':
    for name in os.listdir(path_to_dir):
        if name.endswith(language_code):
            try:
                getVerses(path_to_dir, name)
            except:
                print('>>>>>>>>>>>>>>>> Unable to convert: %s/%s' % (path_to_dir, name))

elif run_mode == '3':
    for subdir, dirs, files in os.walk(path_to_dir):
        for file in files:
            if file.endswith(language_code):
                # try:
                getVerses(subdir, file)
                    # print('%s/%s DONE' % (subdir, file), file=sys.stderr)
                # except:
                #     print('>>>>>>>>>>>>>>>> Unable to convert: %s/%s' % (subdir, file), file=sys.stderr)
