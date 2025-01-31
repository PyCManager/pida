# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
"""
Language Support Superclasses

:license: GPL2 or later
:copyright: 2008 the Pida Project
"""
from functools import partial
from weakref import WeakKeyDictionary
import abc
import string
import gobject

from pida.core.document import Document

from pida.core.projects import Project
from pida.core.service import Service
from pida.core.features import FeaturesConfig
from pida.utils.languages import (
    COMPLETER, LANG_PRIO,
    Suggestion, Definition, ValidationError, Documentation)
from pida.utils.path import get_relative_path
# locale
from pida.core.locale import Locale
locale = Locale('core')
_ = locale.gettext

from pida.core.log import Log

import multiprocessing
from multiprocessing.managers import (
    BaseManager, BaseProxy,
    SyncManager, RemoteError,
)


# priorities for running language plugins

PRIO_DEFAULT = gobject.PRIORITY_DEFAULT_IDLE + 100
PRIO_FOREGROUND = PRIO_DEFAULT - 40

PRIO_FOREGROUND_HIGH = PRIO_FOREGROUND - 40

PRIO_LOW = PRIO_DEFAULT + 40


class BaseDocumentHandler(object):
    """
    Base class for all language plugins
    """
    __metaclass__ = abc.ABCMeta
    #__metaclass__ = LanguageMetaclass
    priority = LANG_PRIO.DEFAULT
    name = "NAME MISSING"
    plugin = "PLUGIN MISSING"
    description = "DESCRIPTION MISSING"

    def __init__(self, svc, document=None):
        self.svc = svc
        self.set_document(document)


    @classmethod
    def uuid(cls):
        """
        Returns a unique id for this class as a string to identify it again
        """
        return "%s.%s" % (cls.__module__, cls.__name__)

    @property
    def uid(self):
        """
        property for uuid()
        """
        return self.__class__.uuid()

    def set_document(self, document):
        """
        sets the document this instance is assigned to
        """
        self.document = document

    def __cmp__(self, other):
        # We do a reverse default ordering. Higher the number lower the item
        if isinstance(other, BaseDocumentHandler):
            return -1 * self.priority.__cmp__(other.priority)

        # what to do, what to do...
        return -1 * super(BaseDocumentHandler).__cmp__(other)

    def sync(self):
        """
        Called once in a while to write file cache if the plugin supports it
        """
        pass

    def close(self):
        """
        Called before this instance is deleted
        """
        pass

    @classmethod
    def priorty_for_document(cls, document):
        """Returns the priority this plugin will have for this document"""
        return cls.priority

    @abc.abstractmethod
    def run(self, document=None, offset=None):
        """
        run this handler, iterate over its items
        may optionally take document/offset
        """
        pass


class BaseCachedDocumentHandler(BaseDocumentHandler):
    """
    Default cache implementation for Languge Plugins.

    The cache is valid until the file is changed on disk
    """

    def run_cached(self):
        """
        Returns a cached iterator of this handler
        """
        return self._default_cache(self.run)

    def _default_cache(self, fnc):
        """
        Default implementation of outline cache.
        We cache as long as the file on disk does not change
        """
        if not hasattr(self, '_cache'):
            self._cache = []
            self._lastmtime = 0
        if not self.document.is_new:
            if self.document.modified_time != self._lastmtime:
                self._cache = []
                iterf = fnc()
                if iterf is None:
                    return
                for x in fnc():
                    self._cache.append(x)
                    yield x
                self._lastmtime = self.document.modified_time
            else:
                for x in self._cache:
                    yield x
        else:
            iterf = fnc()
            if iterf is None:
                return
            for x in iterf:
                yield x


class Outliner(BaseCachedDocumentHandler):
    """
    The Outliner class is used to return a list of interessting code points
    like classes, function, methods, etc.
    It is usually shown by the Outliner window.
    """

    filter_type = ()


class Validator(BaseCachedDocumentHandler):
    pass


class Definer(BaseDocumentHandler):
    """
    The definer class is used to allow the user to the definition of a
    word.
    """


class Documentator(BaseDocumentHandler):
    """
    Documentation receiver returns a Documentation object
    """


class LanguageInfo(object):
    """
    LanguageInfo class stores and transports general informations.

    @varchars - list of characters which can be used in a variable
    @word - characters not in word let the editor detect on of suggestions
    @attributrefs - characters used to show char to access attributes of objects
    """
    # variable have usually only chars a-zA-Z0-9_
    # the first character of variables have an own list
    varchars_first = string.ascii_letters + '_'
    varchars = varchars_first + string.digits

    word = varchars
    word_first = varchars_first

    open_backets = '[({'
    close_backets = '])}'

    # . in python; -> in c, ...
    attributerefs = ''

    completer_open = '[({'
    completer_close = '])}'

    keywords = []
    operators = []

    comment_line = []
    comment_start = []
    comment_end = []

    # i think most languages are
    case_sensitive = True

    def __init__(self, document):
        self.document = document

    def to_dbus(self):
        return {'varchars':      self.varchars,
                'word':          self.word,
                'attributerefs': self.attributerefs,
               }

class TooManyResults(Exception):
    """
    Indicates that the Outliner had to many suggestions returned.

    This will cause the cache to be cleared and will cause a rerun of the
    get_outliner on the next character entered

    @base: base string used
    @expect_length: integer of additional characters needed so the Exception
                    won't happen again
    """
    def __init__(self, base, expected_length=None):
        super(TooManyResults, self).__init__()
        self.base = base
        if expected_length is None:
            self.expected_length = len(base) + 1
        else:
            self.expected_length = expected_length


class Completer(BaseDocumentHandler):
    """
    Completer returns suggestions for autocompleter features
    """

    def get_completions(self, base, buffer_, offset):
        """
        Gets a list of completitions.

        @base - string which starts completions
        @buffer - document to parse
        @offset - cursor position
        """
        raise NotImplementedError('Completer must define get_completions')


def make_iterable(inp):
    if not isinstance(inp, (tuple, list)) and not hasattr(inp, '__iter__'):
        return (inp,)
    return inp


class LanguageServiceFeaturesConfig(FeaturesConfig):
    """
    An advanced version of FeaturesConfig used for language plugins.

    Please remember to call the overloaded function
    """

    def subscribe_all_foreign(self):
        all_langs = make_iterable(self.svc.language_name)
        mapping = {
            'outliner_factory': 'outliner',
            'definer_factory': 'definer',
            'validator_factory': 'validator',
            'completer_factory': 'completer',
            'documentator_factory': 'documentator'
        }
        # register all language info classes
        for lname in all_langs:
            if self.svc.language_info is not None:
                self.subscribe_foreign('language', 'info', lname,
                                       self.svc.language_info)

        for factory_name, feature in mapping.iteritems():
            factory = getattr(self.svc, factory_name)
            if factory is not None:
                # a language_name of a factory overrides the service
                # language_name
                if hasattr(factory, 'language_name'):
                    cur_langs = make_iterable(factory.language_name)
                else:
                    cur_langs = all_langs
                for lname in cur_langs:
                    self.subscribe_foreign(
                            'language', feature, lname,
                            partial(factory, self.svc))


class SnippetsProvider(object):

    def get_snippets(self, document):
        raise NotImplemented

class SnippetTemplate(object):
    text = ""

    def get_template(self):
        """
        Return text for inclusion.
        This may need expanding the template.
        """
        return self.text

    def get_tokens(self):
        """
        Returns a list of Text and Template Tokens
        """
        return []


# Proxy type for generator objects
class GeneratorProxy(BaseProxy):
    """
    Proxies iterators over multiprocessing
    """
    _exposed_ = ('next', '__next__')
    def __iter__(self):
        return self
    def next(self):
        try:
            return self._callmethod('next')
        except (RemoteError, EOFError):
            if getattr(self._manager, 'is_shutdown', False):
                raise StopIteration
            else:
                raise

    def __next__(self):
        try:
            return self._callmethod('__next__')
        except (RemoteError, EOFError):
            if getattr(self._manager, 'is_shutdown', False):
                raise StopIteration
            else:
                raise

def run(x, *k, **kw):
    return x.run(*k, **kw)


class ExternalMeta(type):
    """
    MetaClass for Extern classes. registers the functions for beeing extern
    callable
    """
    LANG_MAP = {
        'validator': ['get_validations'],
        'outliner': ['get_outline'],
        'completer': ['get_completions'],
        'documentator': ['get_documentation'],
        'definer': ['get_definition'],
      }
    def __new__(cls, name, bases, dct):
        return type.__new__(cls, name, bases, dct)
    def __init__(cls, name, bases, dct):
        super(ExternalMeta, cls).__init__(name, bases, dct)
        if not hasattr(cls, 'register'):
            return
        for type_, funcs in cls.LANG_MAP.iteritems():
            if not type_ in dct or not dct[type_]:
                continue
            cls.register(type_, dct[type_])
        cls.register('run', run, proxytype=GeneratorProxy)


class External(SyncManager):
    """
    The External superclass is used to configure and control the external
    processes.

    Create a new class inhereting from External and define the class
    variables of the types you want to externalize. This class must be the
    'extern' class variable of your LanguageService

    @validator: validator class
    @outliner
    @definer
    @documentator

    You can define additional static functions here that can be run on the
    external process.
    """

    __metaclass__ = ExternalMeta

    validator = None
    outliner = None
    definer = None
    documentator = None
    definer = None
    completer = None

    @staticmethod
    def run(instance):
        for i in instance.run():
            yield i


class ExternalDocument(Document):
    """
    Emulates a document that resides in a different python process
    """
    _unique_id = 0
    _project_path = None
    _project = None

    @property
    def uniqueid(self):
        return self._unique_id

    def get_project_relative_path(self):
        """
        Returns the relative path to Project's root
        """
        if self.filename is None or not self._project_path:
            return None, None
        return get_relative_path(self._project_path, self.filename)

    def _get_project(self):
        # test if the path changed and forget the old project
        if self._project and self._project.source_directory != self._project_path:
            self._project = None
        if self._project:
            return self._project
        if self._project_path:
            self._project = Project(self._project_path)
            return self._project

    def _set_project(self, value):
        pass
    project = property(_get_project, _set_project)


class ExternalProxy(BaseCachedDocumentHandler):
    """
    Base Class for all proxy objects.
    """
    _external_document = None

    def set_document(self, document):
        self.document = document
        self._external_document = None

    def get_external_document(self):
        if not self._external_document:
            self._external_document = ExternalDocument(None, self.document.filename)
            self._external_document._unique_id = self.document.unique_id
            if self.document.project:
                self._external_document._project_path = self.document.project.source_directory
        return self._external_document

    @classmethod
    def uuid(cls):
        return cls._uuid

    @property
    def uid(self):
        """
        property for uuid()
        """
        return self._uuid

    def run(self, *k, **kw):
        return self.svc.jobserver.run(self, *k, **kw)


class Merger(BaseDocumentHandler):
    """
    Merges different sources of providers into one stream
    """
    def __init__(self, svc, document=None, sources=()):
        self.set_sources(sources)
        super(Merger, self).__init__(svc, document)

    def set_sources(self, sources):
        """
        Set all sources that will be used to build the results.

        The order of the sources will define the order which create the results
        """
        self.sources = sources
        self.instances = None

    def create_instances(self):
        """
        Create all instances that are an the sources list
        """
        self.instances = []
        for factory in self.sources:
            handler = factory(self.document)
            if handler:
                self.instances.append(handler)


class MergeCompleter(Completer, Merger):
    def run(self, base, buffer_, offset):
        if not self.instances:
            self.create_instances()
        results = set()
        for prov in self.instances:
            for res in prov.run(base, buffer_, offset):
                if res in results:
                    continue
                results.add(res)
                yield res

def safe_remote(func):
    import functools
    @functools.wraps(func)
    def safe(self, *args, **kwargs):
        try:
            for i in func(self, *args, **kwargs):
                yield i
        except RuntimeError as e:
            self.log.warning(_("problems running external plugin: {err}"),
                             err=e)
            self.restart()
            return
        except:
            if self.stopped:
                return
            raise
    return safe


class JobServer(Log):
    """
    The Jobserver dispatches language plugin jobs to external processes it
    manages.
    """
    def __init__(self, svc, external, max_processes=2):
        self.svc = svc
        self.max_processes = max_processes
        self.stopped = False
        # we have to map the proxy objects to
        self._external = external
        self._processes = []
        self._proxy_map = WeakKeyDictionary()
        self._instances = {}

    def get_process(self, proxy=None):
        """
        Returns a Extern instance.
        It tries to use the same instance for proxy so it does not need to
        be recreated and can make best use of caching
        """
        # FIXME needs some better management of processes and dispatching
        if not self._processes:
            np = self._external()
            np.start()
            self._instances[np] = {} #np.dict()
            self._processes.append(np)
        return self._processes[0]

    def get_instance(self, proxy):
        """
        Returns the manager and the real instance of language plugin type of
        the proxy.

        Everything called on this objects are done in the external process
        """
        manager = self._proxy_map.get(proxy, None)
        if not manager:
            manager = self.get_process(proxy)
            self._proxy_map[proxy] = manager
        instances = self._instances[manager]
        if id(proxy.document) not in instances:
            instances[id(proxy.document)] = manager.dict()
        if proxy.mytype not in instances[id(proxy.document)]:
            #no = getattr(manager, type_)(manager)(None, proxy.document)
            instances[id(proxy.document)][proxy.mytype] = getattr(manager, proxy.mytype)(None, proxy.get_external_document())
        return manager, instances[id(proxy.document)][proxy.mytype]

    @safe_remote
    def run(self, proxy, *k, **kw):
        """Forwards to the external process"""
        manager, instance = self.get_instance(proxy)
        return manager.run(instance, *k, **kw)


    def stop(self):
        self.stopped = True
        for i in self._processes:
            i.is_shutdown = True
            i.shutdown()

    def restart(self):
        self.log.info(_("restart jobserver"))
        self.stop()
        self.stopped = False
        self._processes = []
        self._proxy_map = WeakKeyDictionary()
        self._instances = {}


class LanguageService(Service):
    """
    Base class for easily implementing a language service
    """

    language_name = None
    language_info = None
    completer_factory = None
    definer_factory = None
    outliner_factory = None
    validator_factory = None
    documentator_factory = None

    external = None
    jobserver_factory = JobServer

    features_config = LanguageServiceFeaturesConfig

    def __init__(self, boss):
        if self.external is not None and multiprocessing:
            # if we have multiprocessing support we exchange the
            # language factories to the proxy objects
            def newproxy(old, mytype_):
                if not old:
                    return type(
                        'External%sProxy'%mytype_,
                        (ExternalProxy,),
                        {'mytype': mytype_},
                    )
                class NewProxy(ExternalProxy):
                    mytype = mytype_
                    _uuid = old.uuid() if old else None
                    priority = old.priority
                    name = old.name
                    plugin = old.plugin
                    description = old.description
                    __name__ = 'External%sProxy' % mytype.capitalize()
                    try:
                        filter_type = old.filter_type
                    except AttributeError:
                        pass
                return NewProxy

            for name in 'validator outliner documentator definer completer'.split():
                if getattr(self.external, name):
                    attr = name + '_factory'
                    old = getattr(self, attr)
                    proxy = newproxy(old, name)
                    setattr(self, attr, proxy)

        super(LanguageService, self).__init__(boss)

        self.boss = boss
        if self.external is not None and multiprocessing:
            self.jobserver = self.jobserver_factory(self, self.external)
        else:
            self.jobserver = None

    def stop(self):
        if self.jobserver:
            self.jobserver.stop()
        super(LanguageService, self).stop()

LANGUAGE_PLUGIN_TYPES = {
'completer': {
    'name': _('Completer'),
    'description': _('Provides suggestions for autocompletion'),
    'class': Completer},
'definer': {
    'name': _('Definer'),
    'description': _(
        'Jumps to the code position where the current symbol is defined'),
    'class': Definer},
'documentator': {
    'name': _('Documentator'),
    'description': _('Provides the signature of the current symbol'),
    'class': Documentator},
'outliner': {
    'name': _('Outliner'),
    'description': _('Provides informations where symbols are defined'),
    'class': Outliner},
'validator': {
    'name': _('Validator'),
    'description': _('Shows problems and style errors in the code'),
    'class': Validator}
}

