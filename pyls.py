#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Pyls

Usage:
    pyls.py [options]
    pyls.py [options] <targetDir>

Options:
    -a, --all                  do not ignore entries starting with .
    -A, --almost-all           do not list implied . and ..
    -C                         list entries by columns
        --color                 colorize the output.  WHEN defaults to `always'
                                 or can be `never' or `auto'.  More info below
    -F, --classify             append indicator (one of */=>@|) to entries
        --file-type            likewise, except do not append `*'
    -g                         like -l, but do not list owner
    -G, --no-group             in a long listing, don't print group names
    -h, --human-readable       with -l, print sizes in human readable format
                                 (e.g., 1K 234M 2G)
    -l                         use a long listing format
    -L, --dereference          when showing file information for a symbolic
                                 link, show information for the file the link
                                 references rather than for the link itself
    -r, --reverse              reverse order while sorting
    -R, --recursive            list subdirectories recursively
    -S                         sort by file size
    -t                         sort by modification time, newest first
    -x                         list entries by lines instead of by columns
    -1                         list one file per line

Othres:
        --help      display this help and exit
        --version   output version information and exit

"""

from docopt import docopt
import os

C_RED = '\033[91m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_BLUE = '\033[94m'
C_MAGENTA = '\033[95m'
C_CYAN = '\033[96m'
C_WHITE = '\033[97m'
C_END = '\033[0m'
C_BOLD = '\033[1m'


def listAllItems(path):
    items = os.listdir(path)
    items.insert(0, '.')
    items.insert(1, '..')
    return items


def listAlmostAllItems(path):
    items = os.listdir(path)
    return items


def listItems(path):
    items = listAlmostAllItems(path)
    return filter(lambda item: not item.startswith('.'), items)


def printItems(path, items, color=False, classify=False):
    length = 0
    for item in items:
        length = len(item) if len(item) > length else length

    for item in items:
        filepath = path + '/' + item
        if os.path.islink(filepath):
            if os.path.isdir(filepath) or os.path.isfile(filepath):
                print (
                    (C_CYAN if color else '') + item + C_END
                    + ('@' if classify else '')),
            else:
                print (C_RED if color else '') + item + C_END + ('@' if classify else ''),
        elif os.path.isdir(filepath):
            print (C_BLUE if color else '') + item + C_END + ('/' if classify else ''),
        elif os.access(filepath, os.X_OK):
            print (C_GREEN if color else '') + item + C_END + ('*' if classify else ''),
        else:
            print item,
        print '',
    print ''


def columnsPrint(items):
    outOfRange = True
    numberOfRows = 1
    terminalHeight, terminalWidth = os.popen('stty size').read().split()

    while outOfRange:
        numberOfColumns = -(-len(items) / numberOfRows)
        columnsWidth = []
        for column in xrange(numberOfColumns):
            maxWidth = 0
            for name in items[numberOfRows*column:numberOfRows*(column+1)]:
                maxWidth = len(name) if len(name) > maxWidth else maxWidth
            columnsWidth.append(maxWidth)
        if sum(columnsWidth, 2*len(columnsWidth)) < int(terminalWidth):
            outOfRange = False
        else:
            numberOfRows += 1
        if numberOfRows > 100:
            break

    for row in xrange(numberOfRows):
        for column in xrange(numberOfColumns):
            width = columnsWidth[column]
            formatString = '{0:%d}' % (width+1)
            try:
                string = formatString.format(items[numberOfRows*column + row])
            except:
                continue
            else:
                print string,
        print ''


def addDirectorySynbol(items):
    for item in items:
        if os.path.isdir(item):
            item = item + '/'
    return items


if __name__ == '__main__':
    args = docopt(__doc__, version='1.0.0')

    if args['<targetDir>'] is None:
        args['<targetDir>'] = './'
    path = args['<targetDir>']

    # list up items
    if args['--all']:
        items = listAllItems(path)
    elif args['--almost-all']:
        items = listAlmostAllItems(path)
    else:
        items = listItems(path)

    # sort items
    sortKey = lambda f: f.lower() if not f.startswith('.') else f[1:].lower()
    items.sort(key=sortKey)

    # print items
    # printItems(path, items, args['--color'], args['--classify'])
    columnsPrint(items)
