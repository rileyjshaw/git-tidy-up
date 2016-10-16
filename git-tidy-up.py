#!/usr/bin/env python

import re
import subprocess


process = subprocess.Popen(['git', 'diff', '-U0'], stdout=subprocess.PIPE)
output, err = process.communicate()

# For each modified file's patch...
# TODO(riley): I am bad at programming lol help.
for f in re.findall(re.compile('^(diff.*?)(?=^diff|\Z)', re.M | re.S), output):
    sections = re.split(re.compile('^@@', re.M), f)
    header = sections[0]
    diffs = ['@@' + s for s in sections[1:]]
    for diff in diffs:
        patch = header + '\n' + diff
        print patch
        while True:
            c = raw_input('\033[1m\033[94mWhat should I do [[1-9],y,n]?\033[0m ')
            if len(c) is 1 and c.isdigit() and c != '0':
                print 'Let\'s commit that to batch ' + c + '.'
            elif c == 'y':
                print 'Okay, we will skip it.'
            elif c == 'n':
                print 'Hoo boy, deleted.'
            else:
                continue

            print '\n'
            break
