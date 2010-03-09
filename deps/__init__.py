import os
import re
import sys
import shutil
import subprocess
import logging
import urlparse
import ConfigParser

logger = logging.getLogger('deps')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class MissingDependency(Exception):
    pass


class VersionControl(object):
    def __init__(self, url, root, app_name=None, project_name=None, rev=''):
        self.url = url
        self.root = root
        self.rev = rev
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
    def __init__(self, *args, **kwargs):
        super(HG, self).__init__(*args, **kwargs)
        if self.rev:
            self.rev = '-r%s' % self.rev
        
    def checkout(self):
        logger.info('checking out %s' % self.project_name)
        os.system('hg clone %s %s %s' % (self.rev, self.url, self.python_path))

    def up(self):
        logger.info('%s' % self)
        if not os.path.exists(self.path):
            self.checkout()
        config = ConfigParser.ConfigParser()
        config.read('%s/.hg/hgrc' % self.python_path)
        hgrc = config.get("paths","default")
        if hgrc != self.url:
            os.system('rm --interactive=never -r %s' % self.python_path)
            self.checkout()
        os.chdir(self.python_path)
        os.system('hg pull %s --update -f %s' % (self.rev, self.url))


class GIT(VersionControl):
    def checkout(self):
        logger.info('checking out %s' % self.project_name)
        os.system('git clone %s %s' % (self.url, self.python_path))

    def up(self):
        logger.info('%s' % self)
        if not os.path.exists(self.path):
            self.checkout()
        config = open('%s/.git/config' % self.python_path, 'r').read()
        config = re.search('(?<=url = )\S+', config).group(0)
        if config != self.url:
            os.system('rm --interactive=never -r %s' % self.python_path)
            self.checkout()
        os.chdir(self.python_path)
        os.system('git pull -q %s' % self.url)
        os.system('git checkout %s' % self.rev)


class SVN(VersionControl):
    def __init__(self, *args, **kwargs):
        super(SVN, self).__init__(*args, **kwargs)
        if self.rev:
            self.rev = '-r%s' % self.rev
            
    def checkout(self):
        logger.info('checking out %s' % self.project_name)
        os.system('svn %s co %s %s' % (self.rev, self.url, self.path))
        
    def up(self):
        logger.info('%s' % self)
        if not os.path.exists(self.path):
            self.checkout()
        process = subprocess.Popen('svn info %s' % self.path, 
            shell=True, stdout=subprocess.PIPE,
        )
        url = process.communicate()[0].split('\n',2)[1].\
            replace('URL: ','').strip()
        if self.url != url:
            os.system('svn switch %s %s' % (self.url, self.path))
        os.system('svn %s up %s' % (self.rev, self.path))


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
