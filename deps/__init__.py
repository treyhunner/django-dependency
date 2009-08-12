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
    def __init__(self, app_name, url, root, project_name=None):
        self.app_name = app_name
        self.url = url
        self.root = root
        if not project_name:
            path = urlparse.urlparse(self.url)[2]
            if not path.endswith('/'):
                path = path + '/'
            head, tail = os.path.split(path)
            self.project_name = os.path.basename(head)
        else:
            self.project_name = project_name
        self.path = os.path.join(self.root, self.project_name)
    
    def __repr__(self):
        return self.app_name
    
    def add_to_python_path(self):
        if not os.path.exists(self.path):
            raise MissingDependency('%s does not exist.  Run "./manage.py up" to retrieve this dependency' % self.app_name)
        sys.path.insert(0, self.path)


class HG(VersionControl):
    def checkout(self):
        logger.info('checking out %s' % self.project_name)
        os.system('hg clone %s %s' % (self.url, self.path))
    
    def up(self):
        if not os.path.exists(self.path):
            self.checkout()
        logger.info('updating %s' % self.project_name)
        os.chdir(self.path)
        os.system('hg update')


class SVN(VersionControl):
    def checkout(self):
        logger.info('checking out %s' % self.project_name)
        os.system('svn co %s %s' % (self.url, self.path))
    
    def up(self):
        if not os.path.exists(self.path):
            self.checkout()
        logger.info('updating %s' % self.project_name)
        os.system('svn up %s' % self.path)
