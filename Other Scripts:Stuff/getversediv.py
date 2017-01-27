#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

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
            verses = re.search('<div\s+class="verses"\s+id="[^"]*">(.+?)</div>', data).group(1)
        except AttributeError:
            print("something with horribly wrong with %s/%s" % (path, fileName))
            verses = 'ERROR: Verses not found in this file'

        f = open('%s/%s.div' % (path, fileName), 'w')
        f.write(verses + '\n')
        f.close()
            

# TODO: Ask about just hard coding this or using command-line question
language_string = input('\nWhat is the 3-character abbreviation for the language you want to extract: ')
language_string = '?lang=' + language_string
print('\nUsing ' + language_string)
# language_string = '?lang=spa'

# Command-line interface stuff to run script
path_to_dir = input("\nPlease input the path to the directory you'd like to run this script against. (Enter '.' for current directory): ")
print('\n-- All chapter files in %s directory: ---\n' % path_to_dir)
for name in os.listdir(path_to_dir):
    if name.endswith(language_string):
        print(name)
print('\n-- ' + path_to_dir  + ' also contains the following sub-directories: --\n')
print(next(os.walk(path_to_dir))[1])

for subdir, dirs, files in os.walk(path_to_dir):
    for file in files:
        if file.endswith(language_string):
            getVerses(subdir, file)
