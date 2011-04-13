import os
import re
import sys
import shutil
import logging
import urlparse
import ConfigParser
from subprocess import Popen, PIPE, call

logger = logging.getLogger('deps')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class MissingDependency(Exception):
    pass


class VersionControl(object):
    def __init__(self, url, root, app_name=None, project_name=None, rev='', app_dir=None):
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
        self.app_dir=app_dir
            
        self.path = os.path.join(
            self.root,
            self.project_name,
            self.app_name,
        )
    
    def __repr__(self):
        return "<VersionControl: %s>" % self.app_name
    
    def add_to_python_path(self, position):
        path=self.path
        if self.app_dir:
            path = os.path.join(
                self.root,
                self.project_name,
                self.app_dir,
                self.app_name,
            )
            self.python_path = os.path.join(
                self.root,
                self.project_name,
                self.app_dir,
            )
        if not os.path.exists(path):
            raise MissingDependency('%s does not exist.  Run "./manage.py up" to retrieve this dependency' % self.app_name)
        sys.path.insert(position, self.python_path)


class HG(VersionControl):
    def __init__(self, *args, **kwargs):
        super(HG, self).__init__(*args, **kwargs)
        if self.rev:
            self.rev = '-r%s' % self.rev
        
    def checkout(self):
        logger.info('checking out %s' % self.project_name)
        call('hg clone %s %s %s' % (self.rev, self.url, self.python_path), shell=True)

    def up(self):
        logger.info('%s' % self)
        if not os.path.exists(self.path):
            self.checkout()
        config = ConfigParser.ConfigParser()
        config.read('%s/.hg/hgrc' % self.python_path)
        hgrc = config.get("paths","default")
        if hgrc != self.url:
            call('rm --interactive=never -r %s' % self.python_path, shell=True)
            self.checkout()
        os.chdir(self.python_path)
        call('hg pull %s --update -f %s' % (self.rev, self.url), shell=True)


class GIT(VersionControl):
    def checkout(self):
        logger.info('checking out %s' % self.project_name)
        call('git clone %s %s' % (self.url, self.python_path), shell=True)

    def up(self):
        logger.info('%s' % self)
        if not os.path.exists(self.path):
            self.checkout()
        config = open('%s/.git/config' % self.python_path, 'r').read()
        config = re.search('(?<=url = )\S+', config).group(0)
        if config != self.url:
            call('rm --interactive=never -r %s' % self.python_path, shell=True)
            self.checkout()
        os.chdir(self.python_path)
        if call('git show-ref --verify --quiet refs/heads/%s' % self.rev, shell=True):
        # rev is not a branch
            call('git fetch %s' % self.url, shell=True)
            call('git checkout %s' % self.rev, shell=True)
        else:
        # rev is a branch
            call('git checkout %s' % self.rev, shell=True)
            call('git pull -q %s %s' % (self.url, self.rev), shell=True)

class SVN(VersionControl):
    def __init__(self, *args, **kwargs):
        super(SVN, self).__init__(*args, **kwargs)
        if self.rev:
            self.rev = '-r%s' % self.rev
            
    def checkout(self):
        logger.info('checking out %s' % self.project_name)
        call('svn %s co %s %s' % (self.rev, self.url, self.path), shell=True)
        
    def up(self):
        logger.info('%s' % self)
        if not os.path.exists(self.path):
            self.checkout()
        process = Popen('svn info %s' % self.path, 
            shell=True, stdout=PIPE,
        )
        url = process.communicate()[0].split('\n',2)[1].\
            replace('URL: ','').strip()
        if self.url != url:
            call('svn switch %s %s' % (self.url, self.path), shell=True)
        call('svn %s up %s' % (self.rev, self.path), shell=True)


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
