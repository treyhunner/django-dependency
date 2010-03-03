#!/usr/bin/env python
import sys
import getopt
import commands

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def get_externals(dirs):
    externals = []
    for dir in dirs:
        command = 'svn propget svn:externals %s' % dir
        for external in commands.getoutput(command).split('\n'):
            if external and ' ' in external:
                name, url = external.split(' ', 1)
                externals.append((name, url, dir))
    return externals


def main(argv=None):
    if argv is None:
        argv = sys.argv
    dirs = argv[1:]
    try:
        if len(dirs) == 0:
            raise Usage('Usage: %s <dir1> [<dir2> <dir3> ...]' % argv[0])
    except Usage, err:
        print >>sys.stderr, err.msg
        return 2

    externals = get_externals(dirs)
    print """DEPDENDENCY_ROOT = os.path.join(PROJECT_PATH, 'external')
DEPENDENCIES = (
    # automatically generated subversion dependency list"""
    for name, url, dir in externals:
        if name != url.rstrip('/')[-len(name):]:
            raise Exception('Changing the name of an app is not (yet) supported.')
        url = url.split(' ', 1)
        if len(url) == 2:
            print """    deps.SVN(
        '%s',
        rev='%s',
        root=DEPDENDENCY_ROOT,
    ),""" % (url[1], url[0].replace('-r',''))
        else:
            print """    deps.SVN(
        '%s',
        root=DEPDENDENCY_ROOT,
    ),""" % url[0]
    print """)
"""


if __name__ == "__main__":
    sys.exit(main())
