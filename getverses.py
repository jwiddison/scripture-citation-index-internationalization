# !/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

import re
import os
import csv

def getItemLocations(sub_string, list_to_parse, char_offset, use_end):
    location_list = []
    for index in re.finditer(sub_string, list_to_parse):
        location_list.append(index.end() + char_offset) if use_end else location_list.append(index.start() + char_offset)
    return location_list

def getVerses(path, fileName):
    with open('%s/%s' % (path, fileName), 'r') as html:
        data = html.read().replace('\n', ' ')
        try:
            if path.endswith('ps') and fileName == '119?lang=spa':
                verses = re.search('<div\s+class="verses"\s+id="[^"]*">(.+)</span></div>', data).group(1)
                # TODO: Fix Psalm 119
            else:
                verses = re.search('<div\s+class="verses"\s+id="[^"]*">(.+?)</div>', data).group(1)
        except AttributeError:
            #TODO: Process in special way for files with no verses (facsimilies, etc.)
            # BOFM title pages <div id="primary">
            print("Verses not found in %s/%s. Handling as special case." % (path, fileName))
            verses = 'ERROR: Verses not found in this file'


        verse_number_locations = getItemLocations('<span class="verse">', verses, 1, True)
        verse_text_end_locations = getItemLocations('</p>', verses, 0, False)
        footnote_letter_locations = getItemLocations('</sup>', verses, -1, False)

        verse_text_start_locations = []
        for index in range(len(verse_number_locations)):
            location = verses.find('</span>', verse_number_locations[index])
            verse_text_start_locations.append(location + len('</span>'))

        verse_html = [] # To hold raw HTML for verse
        verse_texts = [] # To hold cleaned text for verse

        # Get raw HTML for verses
        for index in range(len(verse_number_locations)):
            verse_html.append(verses[verse_text_start_locations[index]:verse_text_end_locations[index]])

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


        # Clean HTML
        for verse in verse_html:

            verse = re.sub('<a[^>]*?class="footnote"[^>]*?>', '', verse)
            verse = re.sub('<a[^>]*?class="bookmark-anchor[^>]*?dontHighlight"[^>]*?>', '' ,verse)
            verse = re.sub('<a[^>]*?>', '', verse)
            verse = re.sub('</a>', '', verse)

            if 'class="closing"' in verse:
                capture_group = re.search('<div[^>]*?class="closing">([.*?])</div>', verse).group(1)
                verse = re.sub('<div[^>]*?class="closing">[.*?]</div>', '', verse)

            if 'class="closingBlock"' in verse:
                capture_group = re.search('<div[^>]*?class="closingBlock">([.*?])</div>', verse).group(1)
                verse = re.sub('<div[^>]*?class="closingBlock">[.*?]</div>', '', verse)

            if 'class="topic"' in verse:
                capture_group = re.search('<div[^>]*?class="topic">([.*?])</div>', verse).group(1)
                verse = re.sub('<div[^>]*?class="topic">[.*?]</div>', capture_group, verse)

            verse = re.sub('<page-break[^>]*?>', '', verse)
            verse = re.sub('</page-break>', '', verse)

            if 'class="language emphasis"' in verse:
                capture_group = re.search('<span[^>]*?class="language[^>]*?emphasis"[^>]*?>([.*?])</span>', verse).group(1)
                verse = re.sub('<span[^>]*?class="language[^>]*?emphasis"[^>]*?xml:lang="la">[.*?]</span>', capture_group, verse)

            if 'span class="language' in verse:
                capture_group = re.search('<span[^>]*?class="language[^>]*?>([.*?])</span>', verse).group(1)
                verse = re.sub('<span[^>]*?class="language[^>]*?>[.*?]</span>', capture_group, verse)

            if 'span class="clarityWord"' in verse:
                print(' -------- %s/%s is where its dying -------' % (path, fileName))
                print(verse)
                capture_group = re.search('<span[^>]*?class="clarityWord">([.*?])</span>', verse).group(1)
                verse = re.sub('<span[^>]*?class="clarityWord">[.*?]</span>', capture_group, verse)

            if 'span class="selah"' in verse:
                capture_group = re.search('<span\s+class="selah">([.*?])</span>', verse).group(1)
                verse = re.sub('<span\s+class="selah">[.*?]</span>', capture_group, verse)

            verse = re.sub('<sup[^>]*?class="studyNoteMarker">[a-z]</sup>', '', verse)

            if 'p class=""' in verse:
                capture_group = re.search('<p[^>]*?class=""[^>]*?>([.*?])</p>', verse).group(1)
                verse = re.sub('<p[^>]*?class=""[^>]*?>[.*?]</p>', capture_group, verse)

            verse = re.sub('<span[^>]*?class="verse">[0-9]</span>', '', verse)

            verse = re.sub('<div[^>]*?class="summary">[.*?]</div', '', verse)

            verse = re.sub('<h2>[.*?]</h2>', '', verse)

            verse = re.sub('<p>[.*?]</p>', '', verse)

            verse = re.sub('<span[^>]*?class="translit"[^>]*?xml:lang="he">[.*?]</span>','', verse)

            # # To check if there are any other html tags not accounted for
            # matches = re.findall('<.*?>', verse)
            # for match in matches:
            #     if match not in tags_to_keep:
            #         print('%s/%s also contains %s' % (path, fileName, match))

            verse_texts.append(verse)

        with open('%s/%s.csv' % (path, fileName), 'w') as csvfile:
            fieldnames = ['Verse', 'Text']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for index in range(len(verse_number_locations)):
                writer.writerow({'Verse': index + 1, 'Text': verse_texts[index]})

# language_string = input('\nWhat is the 3-character abbreviation for the language you want to extract: ')
# language_string = '?lang=' + language_string
# print('\nUsing ' + language_string)
language_string = '?lang=spa'

# Command-line interface stuff to run script
path_to_dir = input("\nPlease input the path to the directory you'd like to run this script against. (Enter '.' for current directory): ")
print('\n-- All chapter files in %s directory: ---\n' % path_to_dir)
for name in os.listdir(path_to_dir):
    if name.endswith(language_string):
        print(name)
print('\n-- ' + path_to_dir  + ' also contains the following sub-directories: --\n')
print(next(os.walk(path_to_dir))[1])
choice = input('\nWhat would you like to do?\n(1) Run for specific file in this directory (%s)\n(2) Run for all files in this directory (%s)\n(3) Run for all files in this directory, and all subdirectories\n\nPlease enter 1, 2, or 3: ' % (path_to_dir, path_to_dir))
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
            try:
                getVerses(path_to_dir, name)
            except:
                print('Unable to convert: ' + path_to_dir + '/' + name)
elif choice == '3':
    for subdir, dirs, files in os.walk(path_to_dir):
        for file in files:
            if file.endswith(language_string):
                # try:
                getVerses(subdir, file)
                    # print(subdir + '/' + file + ' done')
                # except:
                #     print('Unable to convert: ' + subdir + '/' + file)
