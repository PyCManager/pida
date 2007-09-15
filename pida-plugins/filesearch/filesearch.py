# -*- coding: utf-8 -*- 
"""
    filesearch.filesearch
    ~~~~~~~~~~~~~~~~~~~~~

    This file contains the UI- and service-related functions of the file
    search plugin.

    The search functions itself are inside ``search.py``, the search filters
    inside ``filters.py``.

    :copyright: 2007 by Benjamin Wiegand.
    :license: GNU GPL, see LICENSE for more details.
"""

import gtk

from os import path
from kiwi.ui.objectlist import Column

from pida.core.locale import Locale
from pida.ui.views import PidaGladeView
from pida.core.service import Service
from pida.core.events import EventsConfig
from pida.core.features import FeaturesConfig
from pida.core.actions import ActionsConfig
from pida.core.actions import TYPE_TOGGLE
from pida.core.options import OptionsConfig, OTypeBoolean, OTypeString
from pida.utils.gthreads import GeneratorTask

from filters import ValidationError, FileNameMatchesFilter
from search import get_filters, do_search, SearchMatch


locale = Locale('filesearch')
_ = locale.gettext


class SearchView(PidaGladeView):

    gladefile = 'search'
    locale = locale
    label_text = _('File Search')
    icon_name = 'search'
    filters = []
    running = False
    entries = {}

    def create_ui(self):
        # filter select
        self.filter_select.prefill(get_filters())

        self.match_list.set_columns([
            Column('icon_stock_id', use_stock=True, title=' '),
            Column('state_markup', use_markup=True, title=' '),
            Column('markup', use_markup=True, title=_('Name')),
            Column('path', title=_('Path'))
        ])

        # add standard filter
        self.new_filter(FileNameMatchesFilter)

        # task for asynchrounus searching
        # ``append_to_match_list`` is called if a match was found
        # ``search_finished`` is called at the end of search
        self.task = GeneratorTask(do_search, self.append_to_match_list,
                                  self.search_finished)


    def on_add_button__clicked(self, btn):
        # get selected filter
        f = self.filter_select.read()
        self.new_filter(f)

    def on_search_button__clicked(self, btn):
        if not self.running:
            if self.validate():
                self.start()
        else:
            self.stop()

    def on_match_list__row_activated(self, rowitem, search_match):
        self.svc.boss.cmd('buffer', 'open_file',
                          file_name=path.join(search_match.path,
                                              search_match.name))
        self.svc.boss.editor.cmd('grab_focus')

    def can_be_closed(self):
        self.stop()
        return True

    def start(self):
        """
        Start the asynchrounus search task.
        """
        self.running = True
        self.match_list.clear()
        self.entries = {}
        self.update_match_count(0)
        self.search_button.set_label(gtk.STOCK_STOP)
        # Don't do this inside search loop due to performance reasons
        self.file_listers = list(self.svc.boss.get_service('filemanager').
                                                features('file_lister'))
        self.task.start(self.get_search_folder(), self.filters)

    def stop(self):
        """
        Stop the abort task.
        """
        self.task.stop()
        self.search_finished()

    def new_filter(self, f):
        """
        This function adds a new filter to the GUI and registers it in
        `self.filters``.
        """
        entries = f.get_entries()
        box = gtk.HBox(False, 5)
        box.pack_start(gtk.Label(f.description), expand=False)

        for name, entry in entries.iteritems():
            box.pack_start(entry)

        self.filter_box.pack_start(box)
        box.show_all()
        self.filters.append(f(**entries))

    def set_search_folder(self, folder):
        self.select_folder.set_current_folder(folder)

    def get_search_folder(self):
        """
        Returns the last folder opened in the filemanager.
        If it's not available, it returns the path to the project root instead.
        """
        folder = self.select_folder.get_current_folder()
        # XXX: Windows?
        if folder == '/':
            folder = self.svc.current_project.source_directory
        return folder

    def validate(self):
        """
        Tell all filters to validate their input fields. If a filter raises a
        ``ValidationError`` the user is shown an error message.
        """
        for f in self.filters:
            try:
                f.validate()
            except ValidationError, e:
                # XXX
                return False

        return True

    def update_match_count(self, count=None):
        if count is None:
            self.match_count += 1
        else:
            self.match_count = 0
        self.count_label.set_text('%s files' % self.match_count)

    def append_to_match_list(self, dirpath, filename):
        for lister in self.file_listers:
            # XXX: this loads all files inside the directory and filters the
            #      file later --> dirty hack
            #      find a better way only to load the needed file
            def _f(*args, **kwargs):
                self.add_or_update_file(
                    path.join(dirpath, filename),
                    *args,
                    **kwargs
                )
            GeneratorTask(lister, _f).start(dirpath)

    def add_or_update_file(self, search_file, name, basepath, state):
        if search_file == path.join(basepath, name):
            entry = self.entries.setdefault(search_file,
                                            SearchMatch(basepath, name))
            entry.state = state

            if entry.visible:
                # update file
                self.match_list.update(entry)
            else:
                # add file
                self.match_list.append(entry)
                entry.visible = True
                self.update_match_count()

    def search_finished(self):
        self.running = False
        self.search_button.set_label(gtk.STOCK_FIND)


class SearchEvents(EventsConfig):

    def create_events(self):
        # XXX: add events
        pass

    def subscribe_foreign_events(self):
        self.subscribe_foreign_event('filemanager', 'browsed_path_changed',
                                     self.svc.change_search_folder)
        self.subscribe_foreign_event('project', 'project_switched',
                                     self.svc.on_project_switched)


class SearchFeatures(FeaturesConfig):

    def create_features(self):
        # XXX: add features
        pass

    def subscribe_foreign_features(self):
        pass


class SearchActions(ActionsConfig):

    def create_actions(self):
        self.create_action(
            'show_search',
            TYPE_TOGGLE,
            _('File Search'),
            _('Show the File Search'),
            gtk.STOCK_INFO,
            self.on_show_search,
            '<Shift><Control>f',
        )

    def on_show_search(self, action):
        if action.get_active():
            self.svc.show_search()
        else:
            self.svc.hide_search()


class FileManagerOptionsConfig(OptionsConfig):
    def create_options(self):
        self.create_option(
            'exclude_hidden',
            _('Don\'t search in hidden directories'),
            OTypeBoolean,
            True,
            _('Excludes hidden directories from search')
        )

        self.create_option(
            'exclude_vcs',
            _('Don\'t search in data directories of version control systems'),
            OTypeBoolean,
            True,
            _('Excludes the data directories of version control systems '
              'from search')
        )


class Search(Service):
    """Search service"""

    actions_config = SearchActions
    events_config = SearchEvents
    features_config = SearchFeatures
    options_config = FileManagerOptionsConfig

    def pre_start(self):
        self._view = SearchView(self)

    def change_search_folder(self, path):
        self._view.set_search_folder(path)

    def show_search(self):
        self.boss.cmd('window', 'add_view', paned='Plugin', view=self._view)

    def hide_search(self):
        self.boss.cmd('window', 'remove_view', view=self._view)

    def ensure_view_visible(self):
        action = self.get_action('show_search')
        if not action.get_active():
            action.set_active(True)
        self.boss.cmd('window', 'presnet_view', view=self._view)

    def stop(self):
        if self.get_action('show_search').get_active():
            self.hide_search()

    def on_project_switched(self, project):
        self.current_project = project


# Required Service attribute for service loading
Service = Search
