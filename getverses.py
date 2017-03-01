#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3

# !/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

import re     # Python's REGEX library
import os     # Gives us access to file system to search for other files
import csv    # Enables us to write results out to CSV files
import sys    # To redirect errors to STDERR, and be able to access command-line args

# ---------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------  CONSTANTS ------------------------------------------------------ #
# ---------------------------------------------------------------------------------------------------------------------- #


# Language code.  Change last 3 letters to run for a new language
language_code = '?lang=spa'


# Dictionary of URLs for the 3 images for the facimilies.  Will need to change alt tag for new languages
img_urls = {
    'fac_1': '<img src="http://lds.org/scriptures/bc/scriptures/content/english/bible-maps/images/03990_000_fac-1.jpg" alt="Facsímile Nº 1" width="408" height="402">',
    'fac_2': '<img src="http://lds.org/scriptures/bc/scriptures/content/english/bible-maps/images/03990_000_fac-2.jpg" alt="Facsímile Nº 2" width="408" height="402">',
    'fac_3': '<img src="http://lds.org/scriptures/bc/scriptures/content/english/bible-maps/images/03990_000_fac-3.jpg" alt="Facsímile Nº 3" width="408" height="402">',
}


# These are the filenames for table of contents files, and we don't need to convert those.
toc_files_to_skip = [
    'bible%s' % language_code,
    'bofm%s' % language_code,
    'dc-testament%s' % language_code,
    'pgp%s' % language_code,
]


# All the html tags that we expect to be left over after cleaning, which will be ignored by the checks
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
    '<div eid="11" words="10" class="date">',
    # For OD 2
    '<div eid="7" words="2" class="salutation">',
    '<div class="addressee">',
    '<div eid="13" words="2" class="signature">',
    '<div eid="14" words="3" class="signature">',
    '<div eid="15" words="2" class="signature">',
    '<div eid="16" words="3" class="office">',
    '<div eid="19" words="9" class="date">',
    # For facsimiles
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
    # Added to preserve tables in special cases
    '<br />',

    # TODO: Remove this
    '<span class="line">',
]


# Because we left <h2></h2> in the facsimiles and nowhere else.  Need this for additional checks so we don't throw an error
tags_to_keep_if_facsimile = [
    '<h2>',
    '</h2>',
]


# Dictionary that holds all the lists of REGEX patterns used to clean the various chapters
patterns = {
    # These are all the patterns we want remove without removing their contents.
    'general_keep': [
        '<div[^>]*?class="closing">(.*?)</div>',
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

        # TODO: This is super broken for some reason.  Need to fix <span class="line">
        # '<span\s+class="line">(.*?)</span>',
    ],

    # Patterns to delete where we don't want to keep their contents
    'general_remove': [
        '<span\s+class="verse">(.*?)</span>',
        '<sup[^>]*?class="studyNoteMarker">(.*?)</sup>',
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
        '<div[^>]*?class="figure">(.*?)</div>',
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
        '</ul>',
    ],

    # The special-case tags for Official Declaration 1
    'od_1_keep': [
        '<div\s+eid="1"\s+words="3"\s+class="salutation">(.*?)</div>',
        '<div[^>]*?class="openingBlock">(.*?)</div>',
        '<span[^>]*?class="language[^>]*?emphasis"[^>]*?xml:lang="en">(.*?)</span>',
        '<h2>(.*?)</h2>',
    ],

    'od_1_remove': [
        '<div[^>]*?id="media">(.*?)</div>',
        '<a[^>]*?name="p[0-9]*?"[^>]*?class="bookmark[^>]*?dontHighlight">(.*?)</a>',
        '<a[^>]*?href="[^>]*?"[^>]*?class="scriptureRef">',
        '</a>',
        '<p>',
        '</p>',
        '<div[^>]*?class="studyIntro">(.*?)</div>',
        '<div[^>]*?class="article"[^>]*?id="[^>]*?">',
        '<div[^>]*?class="topic">',
    ],

    # The special-case tags for Official Declaration 2
    'od_2_keep': [
        '<div[^>]*?class="closing">(.*?)</div>',
        '<div\s+eid="1"\s+words="3"\s+class="salutation">(.*?)</div>',
        '<div[^>]*?class="openingBlock">(.*?)</div>',
    ],

    'od_2_remove': [
        '<div[^>]*?id="media">(.*?)</div>',
        '<a[^>]*?name="p[0-9]*?"[^>]*?class="bookmark[^>]*?dontHighlight">(.*?)</a>',
        '<a[^>]*?href="[^>]*?"[^>]*?class="scriptureRef">',
        '</a>',
        '<div[^>]*?class="studyIntro">(.*?)</div>',
        '<p>',
        '</p>',
        '<div[^>]*?class="article"[^>]*?id="[^>]*?">',
        '<h2>(.*?)</h2>',
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

    'jsh_keep': [
        '<span\s+class="label">(.*?)</span>',
        '<span[^>]*?class="language[^>]*?emphasis"[^>]*?xml:lang="en">(.*?)</span>',
        '<div\s+class="">(.*?)</div>'
    ],

    'jsh_remove': [
        '<span\s+class="verse">(.*?)</span>',
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


# The REGEX patterns that match the verse content for each chapter
search = {
    # 'general' handles all chapters except the special cases that follow
    'general': '<div\s+class="verses"\s+id="[^"]*">(.+?)</div>',
    # Special Case Chapters
    'bofm_title': '<div\s+id="primary">(.*?)</ul>[^<]*?</div>',
    'bofm_intro': '<div\s+id="primary">(.*?)</ul>[^<]*?</div>',
    'three': '<div\s+id="primary">(.*?)</ul>[^<]*?</div>',
    'eight': '<div\s+id="primary">(.*?)</ul>[^<]*?</div>',
    'dc_intro': '<div\s+id="primary">(.*?)</p>[^<]*?</div>[^<]*?<ul\s+class="prev-next\s+large">',
    'od1': '<div\s+id="primary">(.*?)</p>[^<]*?</div>',
    'od2': '<div\s+id="primary">(.*?)</div>[^<]*?<ul\s+class="prev-next\s+large">',
    'fac_1': '<div\s+id="primary">(.*?)</div>',
    'fac_2': '<div\s+id="primary">(.*?)</ul>[^<]*?</div>',
    'fac_3': '<div\s+id="primary">(.*?)</ul>[^>]*?</div>',
    'js_h': '<div[^>]*?class="verses"[^>]*?id="0">(.*?)</div>[^>]*?<ul class="prev-next[^>]*?large">',
    'ps119': '<div\s+class="verses"\s+id="[^"]*">(.*?)</div>[^<]*?</div>',
    # Matches all remaining html tags.  For use in check after cleaning
    'remaining': '<[^>]*?>',
    # Used to match <img> tags in facsimilies
    'facsimile_img': '<img[^>]*?>',
}


# Dictionary that holds different file path names for checking special cases
file_paths = {
    'bofm': 'bofm',
    'dc': 'dc-testament',
    'od': 'od',
    'js_h': 'js-h',
    'ps': 'ps',
}


# Dictionary that holds file names for checking special cases
file_names = {
    'bofm_title': 'bofm-title%s' % language_code,
    'bofm_intro': 'introduction%s' % language_code,
    'three': 'three%s' % language_code,
    'eight': 'eight%s' % language_code,
    'dc_intro': 'introduction%s' % language_code,
    'od_1': '1%s' % language_code,
    'od_2': '2%s' % language_code,
    'fac_1': 'fac-1%s' % language_code,
    'fac_2': 'fac-2%s' % language_code,
    'fac_3': 'fac-3%s' % language_code,
    'js_h': '1%s' % language_code,
    'ps_119': '119%s' % language_code,
}


# ---------------------------------------------------------------------------------------------------------------------- #
# -----------------------------------------------------  HELPERS  ------------------------------------------------------ #
# ---------------------------------------------------------------------------------------------------------------------- #


# Given a verse as a string, and 2 lists of regex patterns, strips unwanted html tags out of verse, and returns cleaned string
def cleanVerse(patterns_keep, patterns_remove, string_to_clean):
    string_to_clean = re.sub('<span[^>]*?class="line">', ' <span class="line">', string_to_clean)

    # Removes HTML tags, but keeps their contents
    for pattern in patterns_keep:
        capture_group = re.search(pattern, string_to_clean)

        if capture_group:
            string_to_clean = re.sub(pattern, capture_group.group(1), string_to_clean)

    # Removes HTML tags and their contents
    for pattern in patterns_remove:
        string_to_clean = re.sub(pattern, '', string_to_clean)

    # Remove all leading whitespace
    string_to_clean = re.sub('^\s\s+', '', string_to_clean)

    # Replace multiple spaces with one, and remove trailing whitespace
    string_to_clean = re.sub('\s+', ' ', string_to_clean).strip()

    return string_to_clean


# Checks for any html tags not already accounted for in tags_to_keep list
def checkForRemainingTags(verse_to_check, index, path, fileName):
    all_other_tags = re.findall(search['remaining'], verse_to_check)

    for tag in all_other_tags:
        if tag not in tags_to_keep:
            print('>>>>>>>>>>>>>>>>>>> %s/%s also contains %s in verse %i' % (path, fileName, tag, index + 1), file=sys.stderr)


# Checks for any remaining tags in special case chapters
def checkForRemainingTagsForSpecialCase(verses_block, path, fileName):
    all_other_tags = re.findall(search['remaining'], verses_block)

    for tag in all_other_tags:
        if tag not in tags_to_keep:

            # Check if tag matches additional <h2> tags found in facsimiles
            if tag not in tags_to_keep_if_facsimile:
                if not fileName.startswith('fac'):
                    print('>>>>>>>>>>>>>>>>>>> %s/%s also contains %s' % (path, fileName, tag), file=sys.stderr)


# Writes verses out to a csv file with the same name as the input file.  Separated into rows by verse
def writeToCsv(path, fileName, verse_texts):
    with open('%s/%s.csv' % (path, fileName), 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Verse', 'Text'])

        for index, verse in enumerate(verse_texts):
            writer.writerow({'Verse': index + 1, 'Text': verse})


# Writes special cases out to CSV in one big 'verse' block
def writeToCsvSpecialCase(path, fileName, verses):
    with open('%s/%s.csv' % (path, fileName), 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Verse', 'Text'])
        writer.writerow({'Verse': 1, 'Text': verses})


# Helper method to break raw_html into separate verses to be cleaned
def getVersesHTML(verses):
    verse_number_locations = [] # Holds the index of the verse numbers
    verse_text_start_locations = [] # Holds the substring index where verses start
    verse_text_end_locations = [] # Holds the substring index where verses end
    verse_html = [] # Holds raw Html for split verses

    # Get sub-string index for each verse number
    for index in re.finditer('<span class="verse">', verses):
        verse_number_locations.append(index.end() + 1)

    # Get index for the beginning of each verse
    for index in re.finditer('<span class="verse">', verses):
        verse_text_start_locations.append(index.start())

    # Get index for the end of each verse
    for index in re.finditer('</p>', verses):
        verse_text_end_locations.append(index.start())

    # Get raw HTML for verses using string slicing
    for index in range(len(verse_number_locations)):
        verse_html.append(verses[verse_text_start_locations[index]:verse_text_end_locations[index]])

    return verse_html


# Just a helper method to factor this function out of the main flow of things
def getVerseTextsFromHTML(verse_html, path, fileName):
    verse_texts = []

    for index, verse in enumerate(verse_html):
        verse = cleanVerse(patterns['general_keep'], patterns['general_remove'], verse)
        checkForRemainingTags(verse, index, path, fileName)
        verse_texts.append(verse)

    return verse_texts


# Helper method to find and extract content for all chapters but special cases
def processStandardChapter(verses, path, fileName):
    verse_html = [] # Holds raw Html for split verses
    verse_texts = [] # Holds finished cleaned text for verses

    verse_html = getVersesHTML(verses)
    verse_texts = getVerseTextsFromHTML(verse_html, path, fileName)

    writeToCsv(path, fileName, verse_texts)
    return


# Similar to above method to process chapter, but smaller for special cases because they don't need to be broken into verses
def processSpecialCaseChapter(keep_list, remove_list, verses, path, fileName):
    verses = cleanVerse(keep_list, remove_list, verses)
    checkForRemainingTagsForSpecialCase(verses, path, fileName)
    writeToCsvSpecialCase(path, fileName, verses)


# Replaces <img> tag in facsimile chapters
def fixFacsimileImgUrl(verses, new_url):
    return re.sub(search['facsimile_img'], new_url, verses)


# Simple helper that will get the verses block from raw html given the pattern to find it
def searchForVerseContent(pattern, raw_html):
    return re.search(pattern, raw_html).group(1)


# Main processing method.  Above helpers are all called at some point in here
def extractContents(path, fileName):

    # Reset Lists to empty each time
    verse_html = []
    verse_texts = []

    with open('%s/%s' % (path, fileName), 'r') as html:
        raw_html = html.read().replace('\n', ' ')

        # Skip Table of Contents files for each volume
        if fileName in toc_files_to_skip:
            return

        # Handle Special Cases
        if fileName == file_names['bofm_title']:
            verses = searchForVerseContent(search['bofm_title'], raw_html)
            processSpecialCaseChapter(patterns['bofm_title_keep'], patterns['bofm_title_remove'], verses, path, fileName)
            return

        elif path.endswith(file_paths['bofm']) and fileName == file_names['bofm_intro']:
            verses = searchForVerseContent(search['bofm_intro'], raw_html)
            processSpecialCaseChapter(patterns['bofm_intro_keep'], patterns['bofm_intro_remove'], verses, path, fileName)
            return

        elif fileName == file_names['three']:
            verses = searchForVerseContent(search['three'], raw_html)
            processSpecialCaseChapter(patterns['witnesses_keep'], patterns['witnesses_remove'], verses, path, fileName)
            return

        elif fileName == file_names['eight']:
            verses = searchForVerseContent(search['eight'], raw_html)
            processSpecialCaseChapter(patterns['witnesses_keep'], patterns['witnesses_remove'], verses, path, fileName)
            return

        elif path.endswith(file_paths['dc']) and fileName == file_names['dc_intro']:
            verses = searchForVerseContent(search['dc_intro'], raw_html)

            # Preserve table in list of names
            verses = re.sub('<ul\s+class="noMarker">', '<br />', verses)
            verses = re.sub('<li>', '<br />', verses)
            verses = re.sub('</ul>', '<br />', verses)

            processSpecialCaseChapter(patterns['dc_intro_keep'], patterns['dc_intro_remove'], verses, path, fileName)
            return

        elif path.endswith(file_paths['od']) and fileName == file_names['od_1']:
            verses = searchForVerseContent(search['od1'], raw_html)
            processSpecialCaseChapter(patterns['od_1_keep'], patterns['od_1_remove'], verses, path, fileName)
            return

        elif path.endswith(file_paths['od']) and fileName == file_names['od_2']:
            verses = searchForVerseContent(search['od2'], raw_html)
            processSpecialCaseChapter(patterns['od_2_keep'], patterns['od_2_remove'], verses, path, fileName)
            return

        elif fileName == file_names['fac_1']:
            verses = searchForVerseContent(search['fac_1'], raw_html)

            # Fix Image URL and preserve tables with <br />
            verses = fixFacsimileImgUrl(verses, img_urls['fac_1'])
            verses = re.sub('<tr>', '<tr><br />', verses)

            processSpecialCaseChapter(patterns['fac_1_keep'], patterns['fac_1_remove'], verses, path, fileName)
            return

        elif fileName == file_names['fac_2']:
            verses = searchForVerseContent(search['fac_2'], raw_html)

            # Fix Image URL and preserve tables with <br />
            verses = fixFacsimileImgUrl(verses, img_urls['fac_2'])
            verses = re.sub('<tr>', '<tr><br />', verses)
            verses = re.sub('</table>', '<br /></table>', verses)

            processSpecialCaseChapter(patterns['fac_2_keep'], patterns['fac_2_remove'], verses, path, fileName)
            return

        elif fileName == file_names['fac_3']:
            verses = searchForVerseContent(search['fac_3'], raw_html)

            # Fix Image URL and preserve tables with <br />
            verses = fixFacsimileImgUrl(verses, img_urls['fac_3'])
            verses = re.sub('<tr>', '<tr><br />', verses)
            verses = re.sub('</table>', '<br /></table>', verses)

            processSpecialCaseChapter(patterns['fac_3_keep'], patterns['fac_3_remove'], verses, path, fileName)
            return

        elif path.endswith(file_paths['js_h']) and fileName == file_names['js_h']:
            verses = searchForVerseContent(search['js_h'], raw_html)

            for pattern in patterns['jsh_pre_clean']:
                verses = re.sub(pattern, '', verses)

            verse_html = getVersesHTML(verses)

            # Add the paragraphs that come after the end of the last verse.
            verse_html.append(re.search('<ol\s+class="symbol"><li>(.*?)</li></ol>', verses).group(1))

            for index, verse in enumerate(verse_html):
                verse = cleanVerse(patterns['jsh_keep'], patterns['jsh_remove'], verse)

                # Handle the paragraphs that occur after the last verse
                verse = re.sub('</p><p>', '<br /><br />', verse)
                verse = re.sub('<p>', '', verse)
                verse = re.sub('</p>', '', verse)

                checkForRemainingTags(verse, index, path, fileName)
                verse_texts.append(verse)

            writeToCsv(path, fileName, verse_texts)
            return

        elif path.endswith(file_paths['ps']) and fileName == file_names['ps_119']:
            verses = searchForVerseContent(search['ps119'], raw_html)

            for pattern in patterns['ps_119_pre_clean']:
                verses = re.sub(pattern, '', verses)

            verse_html = getVersesHTML(verses)

            for index, verse in enumerate(verse_html):
                verse = cleanVerse(patterns['ps_119_keep'], patterns['ps_119_remove'], verse)
                checkForRemainingTags(verse, index, path, fileName)
                verse_texts.append(verse)

            writeToCsv(path, fileName, verse_texts)
            return

        # Handle All Other Files Besides Special Cases
        else:
            try:
                verses = searchForVerseContent(search['general'], raw_html)
            except AttributeError:
                print('>>>>>>>>>>>>>>>> Unable to get verses in file: %s/%s.' % (path, fileName), file=sys.stderr)

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
        extractContents(path_to_dir, filename)
    except:
        print('>>>>>>>>>>>>>>>> Unable to convert: %s/%s' % (path_to_dir, filename))

elif run_mode == '2':
    for name in os.listdir(path_to_dir):
        if name.endswith(language_code):
            try:
                extractContents(path_to_dir, name)
            except:
                print('>>>>>>>>>>>>>>>> Unable to convert: %s/%s' % (path_to_dir, name))

elif run_mode == '3':
    for subdir, dirs, files in os.walk(path_to_dir):
        for file in files:
            if file.endswith(language_code):
                # try:
                extractContents(subdir, file)
                #     print('%s/%s DONE' % (subdir, file), file=sys.stderr)
                # except:
                #     print('>>>>>>>>>>>>>>>> Unable to convert: %s/%s' % (subdir, file), file=sys.stderr)
