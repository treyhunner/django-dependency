django-dependency
=================

Manage external dependencies hosted through any version control system.

Installation
============

    1) Download the app add it to your Python path:

    ::

        hg clone https://django-dependency.googlecode.com/hg/ django-dependency
        cd django-dependency
        python setup.py install

    2) Add to your INSTALLED_APPS:

    ::

        INSTALLED_APPS = (
            # ...
            'deps',
        )

Setup
=====
Add DEPENDENCIES to your settings file

  
    * If you're migrating from using svn:externals, there is a script you can use to automatically generate the list of dependencies.  Just run the following command, copy/paste the output into your settings file, and make sure your INSTALLED_APPS is up to date:

    ::

        create_deps.py apps/external_apps libs/external_libs

    * If you're not migrating from svn:externals you can set your DEPENDENCIES and INSTALLED_APPS manually like this:

    ::

        import os
        import deps
        # ...
        PROJECT_PATH = os.path.abspath('%s/..' % path.dirname(__file__))
        # ...
        DEPDENDENCY_ROOT = os.path.join(PROJECT_PATH, 'external')
        DEPENDENCIES = (
            # subversion
            deps.SVN(
                #Uncomment to pin to revision 22
                #rev=22,
                'http://code.djangoproject.com/svn/django/trunk/django',
                root=DEPDENDENCY_ROOT,
            ),
            # mercurial
            deps.HG(
                #Uncomment to pin to revision 8ed91139be12
                #rev='8ed91139be12',
                'http://bitbucket.org/jezdez/django-robots/',
                app_name='robots',
                
                root=DEPDENDENCY_ROOT,
            ),
            # git pinned to a SHA1 id with rev can use HEAD or other tags
            deps.GIT(
                'git://github.com/howiworkdaily/django-faq.git',
                app_name='faq',
                project_name='django-faq',
                root=DEPDENDENCY_ROOT,
                rev='85a23e71ba23d4fc5cd92d81a02c1b9073161a21',
            ),
        )
        # ...
        INSTALLED_APPS = (
            # ...
            'robots',
        )

Update manage.py
================

    * To dynamically add the dependencies to your python path, add this code to manage.py AFTER importing settings but BEFORE importing anything from Django:

    ::

        import deps
        deps.add_all_to_path(projectname.settings, auto_update=sys.argv[1] == 'up')

    
    * For example, a complete manage.py might look like this:

    ::

        #!/usr/bin/env python

        import sys
        import os.path
        import deps

        # remove '.' from the path (you should use the project package to reference 
        # anything in here)
        sys.path.pop(0)
        PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
        sys.path.insert(0, os.path.dirname(PROJECT_ROOT))

        try:
            import projectname.settings
        except ImportError:
            import sys
            sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r.\ It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
            sys.exit(1)

        if len(sys.argv) > 1 and sys.argv[1] == 'up':
            deps.add_all_to_path(projectname.settings, auto_update=True)
        else:
            deps.add_all_to_path(projectname.settings, auto_update=False)

        from django.core.management import execute_manager
        if __name__ == "__main__":
            execute_manager(projectname.settings)


    * Now you can run "./manage.py up" to grab the dependencies!


Development sponsored by `Caktus Consulting Group, LLC
<http://www.caktusgroup.com/services>`_.
