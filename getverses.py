import re
import os
import csv
from bs4 import BeautifulSoup

soup=BeautifulSoup(1?lang=spa, 'html.parser')
print(soup.prettify())

# Just change this line to change what language the files are in
language_string = '?lang=spa'

def getItemLocations(sub_string, list_to_parse, char_offset, use_end):
    location_list = []
    for index in re.finditer(sub_string, list_to_parse):
        if use_end:
            location_list.append(index.end() + char_offset)
        else:
            location_list.append(index.start() + char_offset)
    return location_list

def getVerses(path, fileName):
    with open('%s/%s' % (path, fileName), 'r') as html:
        data = html.read().replace('\n', '')
        try:
            verses = re.search('<div class="verses" id="0">(.+?)</div>', data).group(1)
        except AttributeError:
            verses = 'ERROR: Verses not found'

        verse_number_locations = getItemLocations('class="verse">', verses, 1, True)
        verse_text_start_locations = getItemLocations('</span>', verses, 0, True)
        verse_text_end_locations = getItemLocations('</p>', verses, 1, True)
        footnote_letter_locations = getItemLocations('</sup>', verses, -1, False)

        # TODO: Fix this horrible mess.  NOTE:  I don't think this way is going to work.  I think I need to do more REGEX stuff below.
        # Helpful? http://stackoverflow.com/questions/14198497/remove-char-at-specific-index-python
        counter = 0
        for footnote_index in footnote_letter_locations:
            # Trying to do it using string slicing right now
            verses = verses[:footnote_index + counter] + verses[footnote_index + counter + 1:]
            counter -= 1

        verse_texts = []
        counter = 0
        for text in range(len(verse_text_start_locations)):
            verse_texts.append(verses[verse_text_start_locations[counter]:verse_text_end_locations[counter]])
            # TODO: Fix REGEX to remove <sup></sup> that contains the footnotes.  So it doesn't leave the letter behind.
            # verse_texts[counter] = re.sub('sup.+\/sup', '', verse_texts[counter])

            verse_texts[counter] = re.sub('<[^>]+>', '', verse_texts[counter])
            counter += 1

        with open('%s/%s.csv' % (path, fileName), 'w') as csvfile:
            fieldnames = ['Verse', 'Text']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # TODO: Check with Dr. Liddle about including header row
            # writer.writeheader()

            counter = 0
            for v in range(len(verse_number_locations)):
                writer.writerow({'Verse': counter + 1, 'Text': verse_texts[counter]})
                counter += 1


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
    # TODO: Do you wanna put them in their own folder?  Ask Dr. Liddle at next meeting.
    # if not os.path.exists('%s-csv' % path_to_dir):
    #     os.makedirs('%s-csv' % path_to_dir)
    for name in os.listdir(path_to_dir):
        if name.endswith(language_string):
            getVerses(path_to_dir, name)
else:
    filename = input('\nWhat is the filename to convert to CSV: ')
    getVerses(path_to_dir, filename)

# Garbage for Later:
# TODO: Empty Garbage
    # verse_number_locations = []
    # verse_text_start_locations = []
    # verse_text_end_locations = []
    # footnote_letter_locations = []
    #
    # for m in re.finditer('class="verse">', verses):
    #     verse_number_locations.append(m.end() + 1)
    #
    # for m in re.finditer('</span>', verses):
    #     verse_text_start_locations.append(m.end())
    #
    # for m in re.finditer('</p>', verses):
    #     verse_text_end_locations.append(m.end() + 1)
    #
    # for m in re.finditer('</sup>', verses):
    #     footnote_letter_locations.append(m.start() - 1)
