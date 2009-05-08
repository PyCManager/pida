# -*- coding: utf-8 -*- 
"""
    pida.services.languages
    ~~~~~~~~~~~~~~~~~~~~~

    Supplies support for languages

    :copyright: 2005-2008 by The PIDA Project
    :license: GPL2 or later
"""

from functools import partial

import gtk
import gobject

from kiwi.ui.objectlist import Column
from kiwi.ui.objectlist import ObjectList, COL_MODEL

from .outlinefilter import FILTERMAP

from pida.core.environment import on_windows, get_pixmap_path
from pida.core.languages import LANGUAGE_PLUGIN_TYPES
from pida.core.log import get_logger

from pida.utils.gthreads import GeneratorTask

# ui
from pida.ui.views import PidaView, PidaGladeView
from pida.ui.objectlist import AttrSortCombo
from pida.ui.prioritywindow import Category, Entry, PriorityEditorView

# locale
from pida.core.locale import Locale
locale = Locale('plugins')
_ = locale.gettext

logger = get_logger('service.language')

class LanguageEntry(Entry):

    @classmethod
    def from_plugin(cls, plugin):
        return cls(uid=plugin.func.uuid(),
                   display=plugin.func.name,
                   plugin=plugin.func.plugin,
                   description=plugin.func.description)

    def uuid(self):
        return self.uid

class LanguageSubCategory(Category):
    def __init__(self, svc, lang, type_):
        self.svc = svc
        self.lang = lang
        self.type_ = type_
        self._customized = None
    
    @property
    def display(self):
        return LANGUAGE_PLUGIN_TYPES[self.type_]['name']

    @property
    def display_info(self):
        if self.type_ == 'completer':
            return _('<i>All plugins before the Disabled entry are used</i>')
        return None
    
    def _get_customized(self):
        if self._customized is None:
            self._customized = len(self.svc.get_priority_list(self.lang, self.type_))
        return self._customized
    
    def _set_customized(self, value):
        self._customized = value
    
    customized = property(_get_customized, _set_customized)

    def get_entries(self, default=False):
        #for type_, info in LANGUAGE_PLUGIN.iteritems():
        for i in self.svc.get_plugins(self.lang, self.type_, default=default):
            yield LanguageEntry.from_plugin(i)

    def has_entries(self):
        return len(self.svc.get_plugins(self.lang, self.type_)) > 1

    def commit_list(self, lst):

        prio = [{"uuid": x.uuid(),
                 "name": x.display,
                 "plugin": x.plugin,
                 "description": x.description} 
                                for x in lst]
        self.svc.set_priority_list(self.lang, self.type_, prio, save=False)


class LanguageCategory(Category):
    def __init__(self, svc, lang):
        self.svc = svc
        self.lang = lang

    @property
    def display(self):
        return self.svc.doctypes[self.lang].human


    def get_subcategories(self):
        for type_, info in LANGUAGE_PLUGIN_TYPES.iteritems():
            #self.svc.get_plugins(self.lang, type_)
            yield LanguageSubCategory(self.svc, self.lang, type_)

    def needs_visible(self):
        """
        Returns True if it should be displayed
        """
        for type_, info in LANGUAGE_PLUGIN_TYPES.iteritems():
            #self.svc.get_plugins(self.lang, type_)
            if LanguageSubCategory(self.svc, self.lang, type_).has_entries():
                return True

class LanguageRoot(Category):
    """
    Data root for PriorityEditor
    """
    def __init__(self, svc, prioview):
        self.svc = svc
        self.prioview = prioview

    def get_subcategories(self):
        for internal in self.svc.doctypes.iterkeys():
            entry = LanguageCategory(self.svc, internal)
            if self.prioview.all_languages.get_active():
                yield entry
            elif entry.needs_visible():
                yield entry

class LanguagePriorityView(PriorityEditorView):
    """
    Window which allows the user to configure the priorities of plugins
    """
    key = 'language.prio'

    icon_name = 'gtk-library'
    label_text = _('Language Priorities')

    def create_ui(self):
        self.root = LanguageRoot(self.svc, self)
        self.set_category_root(self.root)

    def can_be_closed(self):
        self.svc.get_action('show_language_prio').set_active(False)

    def on_button_apply__clicked(self, action):
        super(LanguagePriorityView, self).on_button_apply__clicked(action)
        #self.svc.get_action('show_language_prio').set_active(False)
        # update all caches
        self.svc.options.set_extra_value(
            "plugin_priorities",
            self.svc.options.get_extra("plugin_priorities"))
        self.svc.emit('refresh')

    def on_button_close__clicked(self, action):
        super(LanguagePriorityView, self).on_button_close__clicked(action)
        self.svc.get_action('show_language_prio').set_active(False)

class ValidatorView(PidaView):

    key = 'language.validator'

    icon_name = 'python-icon'
    label_text = _('Validator')

    def set_validator(self, validator, document):
        # this is quite an act we have to do here because of the many cornercases
        # 1. Jobs once started run through. This is for caching purpuses as a validator
        # is supposed to cache results, somehow.
        # 2. buffers can switch quite often and n background jobs are still 
        # running

        # set the old task job to default priorty again
        old = self.tasks.get(self.document, None)
        if old:
            old.priority = gobject.PRIORITY_DEFAULT_IDLE

        self.document = document
        self.clear_nodes()

        if self.tasks.has_key(document):
            # set the priority of the current validator higher, so it feels 
            # faster on the current view
            self.tasks[document].priorty = gobject.PRIORITY_HIGH_IDLE
            # when restart is set, the set_validator is run again so the 
            # list gets updated from the validator cache. this happens when
            # the buffer switched to another file and back again
            self.restart = True
            self.svc.log.debug(_('Validator task for %s already running'), document)
            return

        self.restart = False

        if validator:

            def wrap_add_node(document, *args):
                # we need this proxy function as a task may be still running in 
                # background and the document already switched
                # this way we still can fill up the cache by letting the task run
                # sometimes args have a lengh of 0 so we have to catch this
                if self.document == document and len(args):
                    self.add_node(args[0])

            def on_complete(document, validator):
                del self.tasks[document]
                # refire the task and hope the cache will just display stuff,
                # elsewise the task is run again
                validator.sync()
                if document == self.document and self.restart:
                    self.set_validator(validator, document)

            radd = partial(wrap_add_node, document)
            rcomp = partial(on_complete, document, validator)


            task = GeneratorTask(validator.get_validations_cached, 
                                 radd,
                                 complete_callback=rcomp,
                                 priority=gobject.PRIORITY_HIGH_IDLE)
            self.tasks[document] = task
            task.start()

    def add_node(self, node):
        if node:
            node.lookup_color = self.errors_ol.style.lookup_color
            self.errors_ol.append(node)

    def create_ui(self):
        self.document = None
        self.tasks = {}
        self.restart = False
        self.errors_ol = ObjectList(
            Column('markup', use_markup=True)
        )
        self.errors_ol.set_headers_visible(False)
        self.errors_ol.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add_main_widget(self.errors_ol)
        self.errors_ol.connect('double-click', self._on_errors_double_clicked)
        self.errors_ol.show_all()
        self.sort_combo = AttrSortCombo(
            self.errors_ol,
            [
                ('lineno', _('Line Number')),
                ('message', _('Message')),
                ('type_', _('Type')),
            ],
            'lineno',
        )
        self.sort_combo.show()
        self.add_main_widget(self.sort_combo, expand=False)

    def clear_nodes(self):
        self.errors_ol.clear()

    def _on_errors_double_clicked(self, ol, item):
        self.svc.boss.editor.cmd('goto_line', line=item.lineno)

    def can_be_closed(self):
        self.svc.get_action('show_validator').set_active(False)


class BrowserView(PidaGladeView):
    """
    Window with the outliner
    """

    key = 'language.browser'


    gladefile = 'outline-browser'
    locale = locale
    icon_name = 'python-icon'
    label_text = _('Outliner')

    def create_ui(self):
        self.document = None
        self.tasks = {}
        self.restart = False
        self.source_tree.set_columns(
            [
                Column('icon_name', use_stock=True),
                Column('markup', use_markup=True, expand=True),
                Column('type_markup', use_markup=True),
                Column('sort_hack', visible=False),
                Column('line_sort_hack', visible=False),
            ]
        )
        self.source_tree.set_headers_visible(False)
        self.sort_box = AttrSortCombo(
            self.source_tree,
            [
                ('sort_hack', _('Alphabetical by type')),
                ('line_sort_hack', _('Line Number')),
                ('name', _('Name')),
            ],
            'sort_hack'
        )
        self.sort_box.show()
        self.sort_vbox.pack_start(self.sort_box, expand=False)
        self.filter_model = self.source_tree.get_model().filter_new()
        #FIXME this causes a total crash on win32
        if not on_windows:
            self.source_tree.get_treeview().set_model(self.filter_model)
        self.filter_model.set_visible_func(self._visible_func)
        self.source_tree.get_treeview().connect('key-press-event',
            self.on_treeview_key_pressed)
        self.source_tree.get_treeview().connect('row-activated',
                                     self.do_treeview__row_activated)

        self._last_expanded = None

    def _visible_func(self, model, iter_):
        node = model[iter_][0]
        # FIXME: None objects shouldn't be here, but why ????
        if not node:
            return False
        ftext = self.filter_name.get_text().lower()
        #riter = model.convert_child_iter_to_iter(iter)
        # name filter
        def if_type(inode):
            # type filter
            if inode.filter_type in self.filter_map:
                if self.filter_map[inode.filter_type]:
                    return True
                else:
                    return False
            else:
                return True


        if ftext:
            # we have to test if any children of the current node may match
            def any_child(parent):
                if not parent:
                    return False
                for i in xrange(model.iter_n_children(parent)):
                    child = model.iter_nth_child(parent, i)
                    cnode = model[child][0]
                    if cnode and cnode.name.lower().find(ftext) != -1 and if_type(cnode):
                        return True
                    if model.iter_has_child(child) and any_child(child):
                        return True
                return False

            if (node.name and node.name.lower().find(ftext) != -1) or \
                (model.iter_has_child(iter_) and any_child(iter_)):
                return if_type(node)
            
            return False
        
        return if_type(node)

    def set_outliner(self, outliner, document):
        # see comments on set_validator

        old = self.tasks.get(self.document, None)
        if old:
            old.priority = gobject.PRIORITY_DEFAULT_IDLE

        self.document = document
        self.clear_items()

        if self.tasks.has_key(document):
            # set the priority of the current validator higher, so it feels 
            # faster on the current view
            self.tasks[document].priorty = gobject.PRIORITY_HIGH_IDLE
            # when restart is set, the set_validator is run again so the 
            # list gets updated from the validator cache. this happens when
            # the buffer switched to another file and back again
            self.restart = True
            self.svc.log.debug(_('Outliner task for %s already running'), document)
            return

        self.restart = False

        if outliner:
#            if self.task:
#                self.task.stop()
#            self.task = GeneratorTask(outliner.get_outline_cached, self.add_node)
#            self.task.start()


            def wrap_add_node(document, *args):
                # we need this proxy function as a task may be still running in 
                # background and the document already switched
                # this way we still can fill up the cache by letting the task run
                # sometimes args have a lengh of 0 so we have to catch this
                if self.document == document and len(args):
                    self.add_node(*args)

            def on_complete(document, outliner):
                del self.tasks[document]
                outliner.sync()
                # refire the task and hope the cache will just display stuff,
                # elsewise the task is run again
                if document == self.document and self.restart:
                    self.set_outliner(outliner, document)


            radd = partial(wrap_add_node, document)
            rcomp = partial(on_complete, document, outliner)

            task = GeneratorTask(outliner.get_outline_cached, 
                                 radd,
                                 complete_callback=rcomp,
                                 priority=gobject.PRIORITY_HIGH_IDLE)
            self.tasks[document] = task
            task.start()


    def clear_items(self):
        self.source_tree.clear()

    def add_node(self, node):
        if not node:
            return
        parent = node.parent
        try:
            self.source_tree.append(parent, node)
        except Exception, e:
            import traceback
            traceback.print_exc()
            print "exc", e
            print "add", parent, node

    def can_be_closed(self):
        self.svc.get_action('show_outliner').set_active(False)

    def do_treeview__row_activated(self, treeview, path, view_column):
        "After activated (double clicked or pressed enter) on a row"
        # we have to use this hand connected version as the kiwi one
        # used the wrong model and not our filtered one :(
        try:
            row = self.filter_model[path]
        except IndexError:
            print 'path %s was not found in model: %s' % (
                path, map(list, self._model))
            return
        item = row[COL_MODEL]
        if item.filename is not None:
            self.svc.boss.cmd('buffer', 'open_file', file_name=item.filename,
                                                     line=item.linenumber)
            self.svc.boss.editor.cmd('grab_focus')
        elif item.linenumber:
            self.svc.boss.editor.cmd('goto_line', line=item.linenumber)
            self.svc.boss.editor.cmd('grab_focus')
        return True

    def update_filterview(self, outliner):
        if outliner:
            def rmchild(widget):
                self.filter_toolbar.remove(widget)
            self.filter_toolbar.foreach(rmchild)

            self.filter_map = dict(
                [(f, FILTERMAP[f]['default']) for f in outliner.filter_type]
                )
            for f in self.filter_map:
                tool_button = gtk.ToggleToolButton()
                tool_button.set_name(str(f))
                tool_button.set_active(self.filter_map[f])
                #FIXME no tooltip on win32
                if not on_windows:
                    tool_button.set_tooltip_text(FILTERMAP[f]['display'])
                tool_button.connect("toggled", self.on_filter_toggled,outliner)
                im = gtk.Image()
                im.set_from_file(get_pixmap_path(FILTERMAP[f]['icon']))
                tool_button.set_icon_widget(im)
                self.filter_toolbar.insert(tool_button, 0)
        #self.options_vbox.add(self.filter_toolbar)
        self.options_vbox.show_all()

    def on_filter_toggled(self, but, outliner):
        self.filter_map[int(but.get_name())] = not self.filter_map[int(but.get_name())]
        #self.set_outliner(outliner, self.document)
        self.filter_model.refilter()

    def on_filter_name_clear__clicked(self, widget):
        self.filter_name.set_text('')

    def on_filter_name__changed(self, widget):
        if len(widget.get_text()) >= self.svc.opt('outline_expand_vars'):
            for i in self.source_tree:
                self.source_tree.expand(
                    i,
                    open_all=True)
        else:
            for i in self.source_tree:
                self.source_tree.collapse(i)

        self.filter_model.refilter()

    def on_treeview_key_pressed(self, tree, event):
        if event.keyval == gtk.keysyms.space:
            # FIXME: who to do this right ??
            cur = self.source_tree.get_selected()
            if self._last_expanded == cur:
                self._last_expanded = None
                self.source_tree.collapse(
                    cur)
            else:
                self.source_tree.expand(
                    cur, 
                    open_all=False)
                self._last_expanded = cur
            return True

    def on_type_changed(self):
        pass
        
#    def read_options(self):
#        return {}