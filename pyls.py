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
    -h, --human-readable       with -l, print sizes in human readable format
                                 (e.g., 1K 234M 2G)
    -l                         use a long listing format
    -r, --reverse              reverse order while sorting
    -S                         sort by file size
    -t                         sort by modification time, newest first
    -1                         list one file per line

Othres:
        --help      display this help and exit
        --version   output version information and exit

"""

from docopt import docopt
import os
import stat

C_RED = '\033[91m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_BLUE = '\033[94m'
C_MAGENTA = '\033[95m'
C_CYAN = '\033[96m'
C_WHITE = '\033[97m'
C_END = '\033[00m'
C_BOLD = '\033[01m'


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


def appendColor(path, item, color=False, classify=False):
    filepath = os.path.join(path, item)
    colorCode = ''
    endCode = C_END if color else ''
    indicator = ''
    if color:
        if os.path.islink(filepath):
            if os.path.isdir(filepath) or os.path.isfile(filepath):
                colorCode = C_CYAN
            else:
                colorCode = C_RED
        elif os.path.isdir(filepath):
            colorCode = C_BLUE
        elif os.access(filepath, os.X_OK):
            colorCode = C_GREEN
        else:
            colorCode = C_END

    if classify:
        if os.path.islink(filepath):
            indicator = '@'
        elif os.path.isdir(filepath):
            indicator = '/'
        elif os.access(filepath, os.X_OK):
            indicator = '*'

    return colorCode + item + endCode + indicator


def printItems(path, items, color=False, classify=False):
    length = 0
    for item in items:
        length = len(item) if len(item) > length else length

    for item in items:
        print appendColor(path, item, color, classify)


def columnsPrint(path, items, color=False, classify=False):
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
        if sum(columnsWidth, 3*len(columnsWidth)) < int(terminalWidth):
            outOfRange = False
        else:
            numberOfRows += 1
        if numberOfRows > 100:
            break

    for row in xrange(numberOfRows):
        for column in xrange(numberOfColumns):
            width = columnsWidth[column]
            width += 1 if not color else 11
            width += 1 if classify else 0
            formatString = '{0:%d}' % (width)
            try:
                item = items[numberOfRows*column + row]
                string = formatString.format(appendColor(
                    path,
                    item,
                    color,
                    classify))
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


def sortItemsByTime(path, items):
    sortKey = lambda f: os.lstat(os.path.join(path, f)).st_mtime
    items.sort(key=sortKey, reverse=True)
    return items


def sortItemsBySize(path, items):
    sortKey = lambda f: os.lstat(os.path.join(path, f)).st_size
    items.sort(key=sortKey, reverse=True)
    return items


def printLongListing(path, items, color=False, classify=False):
    import pwd
    import grp
    import math
    import datetime

    lengthOfnlink = max([os.lstat(os.path.join(path, item)).st_nlink for item in items])
    formatOfnlink = '{0:%d}' % (math.log10(lengthOfnlink) + 1)
    lengthOfsize = max([os.lstat(os.path.join(path, item)).st_size for item in items])
    formatOfsize = '{0:%d}' % (math.log10(lengthOfsize) + 1)
    for item in items:
        filepath = os.path.join(path, item)
        print modString(filepath),
        print formatOfnlink.format(os.lstat(filepath).st_nlink),
        print pwd.getpwuid(os.lstat(filepath).st_uid)[0],
        print grp.getgrgid(os.lstat(filepath).st_gid)[0],
        print formatOfsize.format(os.lstat(filepath).st_size),
        st_time = os.lstat(filepath).st_mtime
        date_time = datetime.datetime.fromtimestamp(st_time)
        print date_time.strftime('%b %d %H:%M'),
        print appendColor(path, item, color, classify)


def modString(filepath):
    modCode = os.lstat(filepath)[stat.ST_MODE]
    string = ''
    if os.path.islink(filepath):
        string += 'l'
    elif os.path.isdir(filepath):
        string += 'd'
    else:
        string += '-'

    string += ('r' if modCode & 0o400 else '-')
    string += ('w' if modCode & 0o200 else '-')
    string += ('x' if modCode & 0o100 else '-')
    string += ('r' if modCode & 0o040 else '-')
    string += ('w' if modCode & 0o020 else '-')
    string += ('x' if modCode & 0o010 else '-')
    string += ('r' if modCode & 0o004 else '-')
    string += ('w' if modCode & 0o002 else '-')
    string += ('x' if modCode & 0o001 else '-')
    return string


if __name__ == '__main__':
    args = docopt(__doc__, version='1.0.0')

    # get directiory path ---------------------------
    if args['<targetDir>'] is None:
        args['<targetDir>'] = '.'
    elif args['<targetDir>'].endswith('/'):
        args['<targetDir>'] = args['<targetDir>'][:-1]
    path = args['<targetDir>']

    # list up items ---------------------------------
    if args['--all']:
        items = listAllItems(path)
    elif args['--almost-all']:
        items = listAlmostAllItems(path)
    else:
        items = listItems(path)

    # sort items -----------------------------------
    sortKey = lambda f: f.lower() if not f.startswith('.') else f[1:].lower()
    items.sort(key=sortKey)
    if args['-S']:
        items = sortItemsBySize(path, items)
    elif args['-t']:
        items = sortItemsByTime(path, items)

    if args['--reverse']:
        items.reverse()

    # print items ----------------------------------
    if args['-l']:
        if args['--human-readable']:
            pass
        printLongListing(path, items, args['--color'], args['--classify'])
    else:
        if args['-1']:
            printItems(path, items, args['--color'], args['--classify'])
        else:  # and args['-C']
            columnsPrint(path, items, args['--color'], args['--classify'])

    # ----------------------------------------------
