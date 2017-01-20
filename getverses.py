import re
import os
import csv

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
            verses = 'ERROR: Verses not found in this file'

        # Get substring-index for relevant elements in string
        verse_number_locations = getItemLocations('class="verse">', verses, 1, True)
        verse_text_start_locations = getItemLocations('</span>', verses, 0, True)
        verse_text_end_locations = getItemLocations('</p>', verses, 0, False)
        footnote_letter_locations = getItemLocations('</sup>', verses, -1, False)

        verse_html = [] # To hold raw HTML for verse
        verse_texts = [] # To hold cleaned text for verse

        # Get raw HTML for verses
        for index in range(len(verse_text_start_locations)):
            verse_html.append(verses[verse_text_start_locations[index]:verse_text_end_locations[index]])

        # Clean HTML to get plaintext
        for verse in verse_html:
            counter = 0
            footnotes = []
            for index in re.finditer('</sup>', verse):
                footnotes.append(index.start() - 1)
            for footnote in footnotes:
                verse = verse[:footnote + counter] + verse[footnote + 1 + counter:]
                counter -= 1
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



path_to_dir = input('\nPlease input the path to the directory containing chapters (Enter "." for current directory): ')

print('\n-- All chapter files in specified directory: ---\n')
for name in os.listdir(path_to_dir):
    if name.endswith(language_string):
        print(name)

# TODO: Ask Dr. Liddle about running the script through sub-directories
# http://stackoverflow.com/questions/800197/how-to-get-all-of-the-immediate-subdirectories-in-python
# ^ A good place to start with how find sub-directories.

do_all = input('\nWould you like to run the script on all chapter files in the directory? (y/n) ')
if do_all == 'y':
    for name in os.listdir(path_to_dir):
        if name.endswith(language_string):
            getVerses(path_to_dir, name)
else:
    filename = input('\nWhat is the filename to convert to CSV: ')
    getVerses(path_to_dir, filename)
