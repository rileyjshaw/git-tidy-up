#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from collections import namedtuple
import re
import subprocess

try:
    input = raw_input  # fix for python2
except NameError:
    pass  # no raw_input in py3, but input is already what we want


Hunk = namedtuple('Hunk', ('diff', 'decision'))


def next_undecided(queue, position):
    while True:
        position += 1
        if position + 1 > len(queue) or queue[position].decision is None:
            break
    return position


def hunks(patches):
    queue = list(map(lambda diff: Hunk(diff, None), patches))
    position = 0
    while True:
        current = queue[position]
        decision = yield current
        if decision.lower() == 'j':
            queue[position] = current._replace(decision=None)
            if decision.isupper():
                position += 1
            else:
                position = next_undecided(queue, position)
        elif decision.lower() == 'k':
            queue[position] = current._replace(decision=None)
            if position == 0:
                continue
            if decision.isupper():
                position -= 1
            else:
                next = position
                while next > 0:
                    next -= 1
                    if queue[next].decision is None:
                        position = next
                        break
        else:
            queue[position] = current._replace(decision=decision)
            position = next_undecided(queue, position)

        if position + 1 > len(queue):
            for i, next in enumerate(queue):
                if next.decision is None:
                    position = i
                    break
            else:
                return


def decide():
    while True:
        c = input('\033[1m\033[94mWhat should I do [[1-9],y,n,j,J,k,K,q]?\033[0m ')
        if len(c) is 1 and c.isdigit() and c != '0':
            print('Let\'s commit that to batch ' + c + '.')
        elif c == 'y':
            print('Okay, we will skip it.')
        elif c == 'n':
            print('Hoo boy, deleted.')
        elif c == 'j':
            print('Leaving undecided and skipping to the next undecided hunk')
        elif c == 'J':
            print('Leaving undecided and skipping to the next hunk')
        elif c == 'k':
            print('Leaving undecided and skipping to the previous undecided hunk')
        elif c == 'K':
            print('Leaving undecided and skipping to the previous hunk')
        elif c == 'q':
            raise KeyboardInterrupt
        else:
            continue
        return c


process = subprocess.Popen(['git', 'diff', '-U0'], stdout=subprocess.PIPE)
output, err = process.communicate()
patches = [];
for f in re.findall(re.compile('^(diff.*?)(?=^diff|\Z)', re.M | re.S), output.decode('utf-8')):
    sections = re.split(re.compile('^@@', re.M), f)
    header = sections[0]
    diffs = ['@@' + s for s in sections[1:]]
    for diff in diffs:
        patch = header + '\n' + diff
        patches.append(patch)

try:
    hunker = hunks(patches);
    current = hunker.send(None)
    while True:  # hunker – a generator – raises StopIteration
        print(current.diff)
        decision = decide()
        current = hunker.send(decision)
except (KeyboardInterrupt, StopIteration):
    pass
