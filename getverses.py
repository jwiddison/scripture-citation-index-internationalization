import re
import os
import csv
from glob import glob

# Change last 3 characters of this string variable if working with different language
language_string = '?lang=spa'

def getItemLocations(sub_string, list_to_parse, char_offset, use_end):
    location_list = []
    for index in re.finditer(sub_string, list_to_parse):
        location_list.append(index.end() + char_offset) if use_end else location_list.append(index.start() + char_offset)
    return location_list

def getVerses(path, fileName):

    # Get HTML from between "verses" divs from file(s) passed into script
    with open('%s/%s' % (path, fileName), 'r') as html:
        data = html.read().replace('\n', '')
        try:
            verses = re.search('<div class="verses" id="0">(.+?)</div>', data).group(1)
        except AttributeError:
            print("something with horribly wrong with %s/%s" % (path, fileName))
            verses = 'ERROR: Verses not found in this file'

        # Get substring-index for relevant elements in string
        verse_number_locations = getItemLocations('class="verse">', verses, 1, True)
        verse_text_start_locations = getItemLocations('</span>', verses, 0, True)
        verse_text_end_locations = getItemLocations('</p>', verses, 0, False)
        footnote_letter_locations = getItemLocations('</sup>', verses, -1, False)

        verse_html = [] # To hold raw HTML for verse
        verse_texts = [] # To hold cleaned text for verse

        # Get raw HTML for verses
        for index in range(len(verse_number_locations)):
            verse_html.append(verses[verse_text_start_locations[index]:verse_text_end_locations[index]])

        # Clean HTML to get plaintext
        for verse in verse_html:
            offset = -1
            for index in re.finditer('</sup>', verse):
                verse = verse[:index.start() + offset] + verse[index.start() + 1 + offset:]
                offset -= 1
            verse = re.sub('<[^>]+>', '', verse)
            verse_texts.append(verse)

        # Write plaintext into CSV file
        with open('%s/%s.csv' % (path, fileName), 'w') as csvfile:
            fieldnames = ['Verse', 'Text']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # TODO: Check with Dr. Liddle about including header row.  If yes, uncomment next line.
            # writer.writeheader()
            for index in range(len(verse_number_locations)):
                writer.writerow({'Verse': index + 1, 'Text': verse_texts[index]})



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
    getVerses(path_to_dir, filename)
elif choice == '2':
    for name in os.listdir(path_to_dir):
        if name.endswith(language_string):
            try:
                getVerses(path_to_dir, name)
                print(path_to_dir + '/' + name + ' done')
            except:
                print('Unable to convert: ' + path_to_dir + '/' + name)
elif choice == '3':
    for subdir, dirs, files in os.walk(path_to_dir):
        for file in files:
            if file.endswith(language_string):
                try:
                    getVerses(subdir, file)
                    print(subdir + '/' + file + ' done')
                except:
                    print('Unable to convert: ' + subdir + '/' + file)
