# -*- coding: utf-8 -*-
#
# xmltextnorm.py
#
# Copyright (c) Nicholas J. Radcliffe 2012

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
    Usage: python xmltextnorm.py [infile.xml [outfile]]

    Writes a normalized version of the textual content of elements
    in the input XML file to the specified outfile as UTF-8 text.
    This is intended to make it easier compare text-based XML
    documents (such as docbook sources, XHTML files or other HTML
    that is valid XML) with a line-based diff tool such as diff,
    opendiff, xdiff etc.

    If outfile is not specified, infile is used with extension changed
    to .txt.

    If neither infile nor outfile are specified, stdin and stdout are used.

    Requires Python 2.7 or an older python with a modern version of
    ElementTree.
"""

import os
import sys
import types
from xml.etree.ElementTree import ElementTree, XMLParser

ENTITIES = {
    u'mdash': u'—',
    u'hellip': u'...',
}


def makeparser():
    """
        Returns an XML parser that knows about a few non-standard XML
        entities.   If your XML source uses other non-standard XML
        entities, add these to ENTITIES above.
    """
    parser = XMLParser()
    parser.parser.UseForeignDTD(True)
    for k in ENTITIES:
        parser.entity[k] = ENTITIES[k]
    return parser


def splitline(line):
    """
        Breaks a single line into a list of shorter lines of
        reasonable length (where possible)..
    """
    out = []
    L = line[:]
    while L:
        if len(L) < 72:
            out.append(L)
            L = u''
        else:
            words = L.split(u' ')
            sPos = L[60:].find(u' ')
            if sPos >= 0:
                out.append(L[:60+sPos])
                L = L[60+sPos + 1:]
            else:
                out.append(L)
                L = u''
    return out


def xmltextnorm(inf, outf):
    """
        Write a normalized version of the text form the data from stream inf
        to the stream at outf, as UTF-8.
    """
    tree = ElementTree()
    parser = makeparser()
    tree.parse(inf, parser=parser)
    paras = tree.getiterator(u"*")
    text = u' '.join([((p.text or u'') + (p.tail or u'')) for p in paras])
    text = text.replace(u'\n', u' ')
    text = text.replace(u'\t', u' ')
    while u'  ' in text:
        text = text.replace(u'  ', u' ')
    for p in u'.,;:!?':
        text = text.replace(u'%s ' % p, u'%s\n' % p)
    lines = text.split(u'\n')
    outlines = []
    for line in lines:
        outlines.extend(splitline(line))
    if type(outf) in types.StringTypes:
        with open(outf, 'w') as f:
            f.write(u'\n'.join(outlines).encode('UTF-8'))
    else:
        outf.write(u'\n'.join(outlines + ['']).encode('UTF-8'))


if __name__ == '__main__':
    if len(sys.argv) == 1:
        xmltextnorm(sys.stdin, sys.stdout)
    elif len(sys.argv) > 3 or (sys.argv == 2
                             and sys.argv[1] in ('-h', '--help', 'help')):
        print __doc__
    else:
        infile = sys.argv[1]
        outfile = (sys.argv[2] if len(sys.argv) == 3
                               else os.path.splitext(infile)[0] + '.txt')
        xmltextnorm(infile, outfile)
