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
    def __init__(self, url, root, app_name=None, project_name=None):
        self.url = url
        self.root = root
        tail = os.path.basename((urlparse.urlparse(url)[2]).rstrip('/'))
        self.project_name = project_name and project_name or tail
        self.app_name = app_name and app_name or tail
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
    
    def add_to_python_path(self, position):
        if not os.path.exists(self.path):
            raise MissingDependency('%s does not exist.  Run "./manage.py up" to retrieve this dependency' % self.app_name)
        sys.path.insert(position, self.python_path)


class HG(VersionControl):
    def checkout(self):
        logger.info('checking out %s' % self.project_name)
        os.system('hg clone %s %s' % (self.url, self.python_path))
    
    def up(self):
        logger.info('%s' % self)
        if not os.path.exists(self.path):
            self.checkout()
        os.chdir(self.python_path)
        os.system('hg pull --update')


class GIT(VersionControl):
    def checkout(self):
        logger.info('checking out %s' % self.project_name)
        os.system('git clone %s %s' % (self.url, self.python_path))

    def up(self):
        logger.info('%s' % self)
        if not os.path.exists(self.path):
            self.checkout()
        os.chdir(self.python_path)
        os.system('git pull')


class SVN(VersionControl):
    def checkout(self):
        logger.info('checking out %s' % self.project_name)
        os.system('svn co %s %s' % (self.url, self.path))
    
    def up(self):
        logger.info('%s' % self)
        if not os.path.exists(self.path):
            self.checkout()
        os.system('svn up %s' % self.path)


def add_all_to_path(settings, auto_update=False, position=1):
    for dependency in settings.DEPENDENCIES:
        try:
            dependency.add_to_python_path(position)
        except MissingDependency:
            if auto_update:
                dependency.up()
            else:
                raise
            dependency.add_to_python_path(position)
