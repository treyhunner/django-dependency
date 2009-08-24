import os
import sys
import shutil
import logging
import urlparse


logger = logging.getLogger('deps')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class MissingDependency(Exception):
    pass


class VersionControl(object):
    def __init__(self, url, root, app_name='', project_name=''):
        self.url = url
        self.root = root
        tail = os.path.basename((urlparse.urlparse(url)[2]).rstrip('/'))
        if not app_name:
            self.app_name = tail
            self.project_name = tail
        else:
            self.app_name = app_name
            self.project_name = tail
        self.python_path = os.path.join(
            self.root,
            self.project_name,
        )
        self.path = os.path.join(
            self.root,
            self.project_name,
            self.app_name,
        )
    
    def __repr__(self):
        return "<VersionControl: %s>" % self.app_name
    
    def add_to_python_path(self):
        if not os.path.exists(self.path):
            raise MissingDependency('%s does not exist.  Run "./manage.py up" to retrieve this dependency' % self.app_name)
        sys.path.insert(0, self.python_path)


class HG(VersionControl):
    def checkout(self):
        logger.info('checking out %s' % self.project_name)
        os.system('hg clone %s %s' % (self.url, self.python_path))
    
    def up(self):
        logger.info('%s' % self)
        if not os.path.exists(self.path):
            self.checkout()
        os.chdir(self.python_path)
        os.system('hg update')


class SVN(VersionControl):
    def checkout(self):
        logger.info('checking out %s' % self.project_name)
        os.system('svn co %s %s' % (self.url, self.path))
    
    def up(self):
        logger.info('%s' % self)
        if not os.path.exists(self.path):
            self.checkout()
        os.system('svn up %s' % self.path)

def add_all_to_path(settings, auto_update=False):
    for dependency in settings.DEPENDENCIES:
        try:
            dependency.add_to_python_path()
        except MissingDependency:
            if auto_update:
                dependency.up()
            else:
                raise
            dependency.add_to_python_path()
