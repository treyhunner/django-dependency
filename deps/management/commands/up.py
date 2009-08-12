from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import os
import sys


from django.conf import settings


class Command(BaseCommand):
    help = 'Django Dependency'
    args = ''

    def handle(self, app_name=None, **kwargs):
        for dependency in settings.DEPENDENCIES:
            if app_name:
                if app_name == dependency.app_name:
                    dependency.up()
                    return
            else:
                dependency.up()
