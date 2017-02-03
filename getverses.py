# !/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

import re
import os
import csv

# I just decided to abstract this out 'cause it got called 4 times in a row
def getItemLocations(sub_string, list_to_parse, char_offset, use_end):
    location_list = []
    for index in re.finditer(sub_string, list_to_parse):
        location_list.append(index.end() + char_offset) if use_end else location_list.append(index.start() + char_offset)
    return location_list

# Function that returns verse text for file passed in
def getVerses(path, fileName):
    # Get HTML from between "verses" divs from file(s) passed into script
    with open('%s/%s' % (path, fileName), 'r') as html:
        data = html.read().replace('\n', ' ')
        try:
            if path.endswith('ps') and fileName == '119?lang=spa':
                verses = re.search('<div\s+class="verses"\s+id="[^"]*">(.+)</span></div>', data).group(1)
                print('PSALM 119')
                print(verses)
            else:
                verses = re.search('<div\s+class="verses"\s+id="[^"]*">(.+?)</div>', data).group(1)
        except AttributeError:
            #TODO: Process in special way for files with no verses (facsimilies, etc.)
            # BOFM title pages <div id="primary">
            print("Verses not found in %s/%s. Handling as special case." % (path, fileName))
            verses = 'ERROR: Verses not found in this file'

        # print(verses)

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
            '<em>',
            '<span class="allCaps">',
            '<span class="smallCaps">',
            '<span class="answer">',
            '<span class="question">',
            '<span class="line">',
        ]

        regex_patterns_to_remove = [
            # Remove all <a> starting tags
            '<a[^>]*?class="footnote"[^>]*?>',
            '<a[^>]*?class="bookmark-anchor\s+dontHighlight"[^>]*?>',
            # '<a[^>]*?>',
            # Remove closing </a> tag.  Okay because we don't want to keep any <a> stuff.
            '</a>',

            # Can't test if these work yet, becuase they're not contained inside the verse <p> tag.  But we still want the content.
            '<div\s+class="closing">.*?</div>',
            '<div\s+class="closingBlock">.*?</div>',

            # '<div\s+class="topic">([.*?])</div>',
            '<div\s+class="topic">.*?</div>',

            '<page-break[^>]*?page="[0-9]"></page-break>',

            '<span\s+class="language\s+emphasis"\s+xml:lang="la">[.*?]</span>',
            '<span\s+class="language"\s+xml:lang="he">[.*?]</span>',
            '<span\s+class="clarityWord">[.*?]</span>',
            '<span\s+class="selah">[.*?]</span>',

            # Delete <p> container for verse itself
            '<p[^>]*?class=""[^>]*?uri="[^>]*?">',
            # Delete all standalone <p> tags and their contents
            '<p>[^>]*</p>',
            # Catch all closing </p> tags from verse container
            '</p>',

            '<sup[^>]*>[a-z]</sup>',
            '<span\s+class="verse">[^>]*</span>',
            '<div\s+class="summary"[^>]*>[a-z]</div>',
            '<h2>[.*?]</h2>',

            '<span\s+class="translit"\s+xml:lang="he">[^>]*</span>',
        ]

        # Clean HTML
        for verse in verse_html:
            for pattern in regex_patterns_to_remove:
                verse = re.sub(pattern,'',verse)
            capture_group = re.search('<div\s+class="topic">([.*?])</div>', verse).group(1)
            verse = re.sub('<div\s+class="topic">([.*?])</div>', capture_group, verse)
            capture_group = re.search('<h2>([.*?])</h2>', verse).group(1)
            verse re.sub('<h2>[.*?]</h2>', capture_group, verse)

            # To check if there are any other html tags not accounted for.  #TODO: finish this.
            # matches = re.findall('<.*?>', verse)
            # for match in matches:
            #     if match not in tags_to_keep:
            #         # print('%s/%s also contains %s' % (path, fileName, match))
            #         pass

            #TODO Handle other tags

            # verse = re.sub('<a(.*?)>[^>?]</a>','',verse)
            # verse = re.sub('<a[^>]+>[.*?]</a>','',verse)
            # verse = re.sub('<div class="closing">[.*?]</div>','',verse)
            # verse = re.sub('<div class="closingBlock">[.*?]</div>','',verse)
            # verse = re.sub('<div class="topic">[.*?]</div>','',verse)
            # verse = re.sub('<page-break page="[^>]*">[.*?]</page-break>','',verse)
            # verse = re.sub('<span class="language emphasis" xml:lang="la">[.*?]</span>','',verse)
            # verse = re.sub('<span class="language" xml:lang="he">[.*?]</span>','',verse)
            # verse = re.sub('<span class="clarityWord">[.*?]</span>','',verse)
            # verse = re.sub('<span class="selah">[.*?]</span>','',verse)
            # verse = re.sub('<sup[^>]*>[a-z]</sup>','',verse) # sup and its contents
            # verse = re.sub('<span class="verse">[^>]*</span>','',verse)
            # verse = re.sub('<p class="[^>]*" uri="[^>]*">[.*?]</p>','',verse) # verse parent p
            # verse = re.sub('<div class="summary"[^>]*>[a-z]</div>','',verse) # div class="summary" and its contents
            # verse = re.sub('<h2>[.*?]</h2>','',verse) # H2 / non-greedy
            # verse = re.sub('<p>[^>]*</p>','',verse)
            # verse = re.sub('<span class="translit" xml:lang="he">[^>]*</span>','',verse)

            # Check for any tags that don't match the 'keep' patterns when we're done.
            # verse = re.sub('<[^>]+>', '', verse) # Don't do this.
            verse_texts.append(verse)

        # Write plaintext into CSV file
        with open('%s/%s.csv' % (path, fileName), 'w') as csvfile:
            fieldnames = ['Verse', 'Text']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # TODO: Check with Dr. Liddle about including header row.  If yes, uncomment next line.
            # writer.writeheader()
            for index in range(len(verse_number_locations)):
                writer.writerow({'Verse': index + 1, 'Text': verse_texts[index]})

# TODO: Ask about just hard coding this or using command-line question
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
                # print(path_to_dir + '/' + name + ' done')
            except:
                print('Unable to convert: ' + path_to_dir + '/' + name)
elif choice == '3':
    for subdir, dirs, files in os.walk(path_to_dir):
        for file in files:
            if file.endswith(language_string):
                try:
                    getVerses(subdir, file)
                    # print(subdir + '/' + file + ' done')
                except:
                    print('Unable to convert: ' + subdir + '/' + file)
