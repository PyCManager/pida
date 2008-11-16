# -*- coding: utf-8 -*- 
"""
    Dbus integration
    ~~~~~~~~~~~~~~~~

    Base classes for integrating services/plugins with DBUS.

    :copyright: 2005-2008 by The PIDA Project
    :license: GPL 2 or later (see README/COPYING/LICENSE)
"""


import os
from pango import Font
from pida.utils.gthreads import gcall

try:
    import dbus

    from dbus.mainloop.glib import DBusGMainLoop
    DBusMainloop = DBusGMainLoop(set_as_default=True)
    
    from dbus.service import (Object, INTROSPECTABLE_IFACE, _method_reply_error,
        _method_reply_return)
    from dbus.service import method
    from dbus import Signature
    import _dbus_bindings

    has_dbus = True
    
except ImportError:
    method = lambda x: x
    INTROSPECTABLE_IFACE = ""
    has_dbus = False
    Object = object

class DbusConfigReal(Object):

    def __init__(self, service):
        self.svc = service
        if hasattr(self, 'export_name'):
            path = DBUS_PATH(self.export_name)
            ns = DBUS_NS(self.export_name)
        else:
            path = DBUS_PATH(service.get_name())
            ns = DBUS_NS(service.get_name())
        self.dbus_ns = ns
        Object.__init__(self, BUS_NAME, path)

class DbusConfigNoop(object):

    def __init__(self, service):
        pass

class DbusOptionsManagerReal(Object):
    __dbus_mapping = {
        bool: 'b',
        str: 's',
        unicode: 's',
        int: 'i',
        long: 'x',
        float: 'd',
        list: 'as',
        file: 's',
        Font: 's',
    }

    dbus_no_export = ()
    dbus_no_fire = ()

    def __init__(self, service):
        self.svc = service
        if hasattr(self, 'export_name'):
            path = DBUS_PATH(self.export_name, self.dbus_path)
            ns = DBUS_NS(self.export_name, self.dbus_path)
        else:
            path = DBUS_PATH(service.get_name(), self.dbus_path)
            ns = DBUS_NS(service.get_name(),self.dbus_path)
        self.dbus_ns = ns
        self.exports = {}
        Object.__init__(self, BUS_NAME, path)

    def object_to_dbus(self, type_):
        try:
            return self.__dbus_mapping[type_]
        except:
            from pida.core.options import BaseChoice, Color
            if issubclass(type_, (BaseChoice, Color)):
                return 's'
            raise ValueError, "No object type found for %s" %type_
            
    def dbus_custom_introspect(self):
        rv = '  <interface name="%s">\n' %(self.dbus_ns)
        for option in self._options.itervalues():
            if option.name in self.dbus_no_export:
                continue
            try:
                typ = self.object_to_dbus(option.type)
            except ValueError, e:
                print "Can't find conversation dbus conversation for ", option
                continue
            rv += '    <property name="%s" type="%s" access="readwrite"/>\n' %(option.name, typ)

        if hasattr(self, '_actions'):
            for action in self._actions.list_actions():
                if action.get_name() not in self.dbus_no_fire:
                    rv += '    <method name="fire_%s" />\n' %(action.get_name())

        rv += '  </interface>\n'
        return rv

    def _message_cb(self, connection, message):
        method_name = message.get_member()
        interface_name = message.get_interface()

        # should we move this stuff into the OptionsConfig and ActionConfig 
        # classes ?
        args = message.get_args_list()

        if interface_name == 'org.freedesktop.DBus.Properties' and \
           len(args) > 1 and args[0] == self.dbus_ns:
            if method_name == "Get":
                opt = self._options[args[1]]
                typ = self.object_to_dbus(opt.type)
                _method_reply_return(connection, 
                                     message, 
                                     method_name, 
                                     Signature(typ), 
                                     opt.value)
                return
            elif method_name == "Set":
                self._options[args[1]] = args[2]
                return
            elif method_name == "GetAll":
                rv = {}
                for name, opt in self._options.iteritems():
                    rv[name] = opt.value
                _method_reply_return(connection, 
                                     message, 
                                     method_name, 
                                     Signature('{sv}'), 
                                     rv)
                return

        if interface_name == self.dbus_ns:
            if method_name[0:5] == "fire_":
                act = self._actions.get_action(method_name[5:])
                try:
                    #_method_reply_error(connection, message, exception)
                    gcall(act.emit, 'activate')
                    _method_reply_return(connection, 
                                         message, 
                                         method_name, 
                                         Signature(''))
                except Exception, exception:
                    _method_reply_error(connection, message, exception)
                return
        # do a normal lookup
        return super(DbusOptionsManagerReal, self)._message_cb(connection, message)
        
    @method(INTROSPECTABLE_IFACE, in_signature='', out_signature='s',
            path_keyword='object_path', connection_keyword='connection')
    def Introspect(self, object_path, connection):
        """Return a string of XML encoding this object's supported interfaces,
        methods and signals.
        """
        reflection_data = _dbus_bindings.DBUS_INTROSPECT_1_0_XML_DOCTYPE_DECL_NODE
        reflection_data += '<node name="%s">\n' % object_path

        interfaces = self._dbus_class_table[self.__class__.__module__ + '.' + self.__class__.__name__]
        for (name, funcs) in interfaces.iteritems():
            reflection_data += '  <interface name="%s">\n' % (name)

            for func in funcs.values():
                if getattr(func, '_dbus_is_method', False):
                    reflection_data += self.__class__._reflect_on_method(func)
                elif getattr(func, '_dbus_is_signal', False):
                    reflection_data += self.__class__._reflect_on_signal(func)

            reflection_data += '  </interface>\n'

        reflection_data += self.dbus_custom_introspect()

        for name in connection.list_exported_child_objects(object_path):
            reflection_data += '  <node name="%s"/>\n' % name

        reflection_data += '</node>\n'

        return reflection_data


class DbusOptionsManagerNoop(object):
    def export_option(self, option):
        pass

    def export_action(self, action):
        pass

if has_dbus:

    from pida.utils.pdbus import (UUID, DBUS_PATH, DBUS_NS, EXPORT, 
        SIGNAL, BUS_NAME, BUS)
    from dbus.mainloop.glib import DBusGMainLoop

    DBusMainloop = DBusGMainLoop(set_as_default=True)


    # export the PIDA UUID to the environment for 

    os.environ['PIDA_DBUS_UUID'] = UUID

    DbusConfig = DbusConfigReal
    DbusOptionsManager = DbusOptionsManagerReal
else:
    # noop DbusConfig
    def noop(*args, **kwargs):
        return []

    def nowrapper(*args, **kwargs):
        def wrapper(*args, **kwargs):
            pass
        return wrapper
    
    UUID = None
    DBUS_PATH = noop
    DBUS_NS = noop
    EXPORT = nowrapper
    SIGNAL = nowrapper
    BUS_NAME = None
    BUS = None
    DbusConfig = DbusConfigNoop
    DbusOptionsManager = DbusOptionsManagerNoop
