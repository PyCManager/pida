"""
    pida.core.project
    ~~~~~~~~~~~~~~~~~~~~

    Project features for PIDA

    :copyright:
        2007 Ali Afshar
        2008 Ronny Pfannschmidt
    :license: GPL2 or later
"""
from __future__ import with_statement
import os
from string import Template
from weakref import proxy

from pida.core.log import Log
from pida.utils.path import get_relative_path

# locale
from pida.core.locale import Locale
locale = Locale('pida')
_ = locale.gettext


#FIXME: win32 fixup
DATA_DIR = ".pida-metadata"

class Project(Log):
    """
    A PIDA project.

    Functions:
     * wrap vellum
     * dict-alike api (but it is NOT a dict

    """

    def __init__(self, source_dir):
        self.source_directory = source_dir
        self.name = os.path.basename(source_dir)
        self.__data = {}
        self.reload()

    def __getitem__(self, key):
        return self.__data[key]

    def get(self, key, default=None):
        return self.__data.get(key)

    def __setitem__(self, key, value):
        self.__data[key] = value

    def __contains__(self, key):
        return key in self.__data

    def reload(self):
        """Loads the project file"""
        from vellum.script import Script
        self.script = Script(
                os.path.join(self.source_directory, 'build')
                )

        # every project has a cache directory, we ensure it exists
        if not os.path.isdir(self.data_dir):
            try:
                os.mkdir(self.data_dir)
            except OSError, e:
                self.log.exception(e)
                
        #XXX: this might need wrappers for reload
        for m in self.__data.values():
            if hasattr(m, 'reload'):
                m.reload()

    @property
    def options(self): 
        return self.script.options

    @property
    def targets(self):
        return self.script.targets

    @property
    def markup(self):
        return '<b>%s</b>\n%s' % (self.display_name, self.source_directory)

    def get_meta_dir(self, mkdir=True, *args, **kwargs):
        path = os.path.join(self.source_directory, DATA_DIR, *args)
        if mkdir:
            self._mkdir(path)
        return path

    data_dir = property(get_meta_dir)

    @property
    def display_name(self):
        return self.options.get('name', self.name)

    def get_relative_path_for(self, filename):
        return get_relative_path(self.source_directory, filename)


    def _mkdir(self, path):
        pe = path.split(os.sep)
        last = os.sep
        for x in pe:
            last = os.path.join(last, x)
            if last and not os.path.isdir(last):
                os.mkdir(last)
