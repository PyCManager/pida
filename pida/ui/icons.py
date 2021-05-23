# -*- coding: utf-8 -*-
"""
    :copyright: 2005-2008 by The PIDA Project
    :license: GPL 2 or later (see README/COPYING/LICENSE)
"""
import os
import gtk


class IconRegister(object):

    def __init__(self):
        self._factory = gtk.IconFactory()
        self._factory.add_default()
        self._register_theme_icons()

    def register_file_icons_for_directory(self, directory):
        for filename in os.listdir(directory):
            name, ext = os.path.splitext(filename)
            if ext in ['.png', '.gif', '.svg', '.jpg']:
                path = os.path.join(directory, filename)
                self._stock_add(name)
                self._register_file_icon(name, path)

    def _register_theme_icons(self):
        stock_ids = gtk.stock_list_ids()
        for name in gtk.icon_theme_get_default().list_icons():
            if name not in stock_ids:
                self._stock_add(name)
                self._register_theme_icon(name)

    def _stock_add(self, name, label=None):
        if label is None:
            label = name.capitalize()
        gtk.stock_add([(name, label, 0, 0, None)])

    def _register_theme_icon(self, name):
        icon_set = gtk.IconSet()
        self._register_icon_set(icon_set, name)

    def _register_file_icon(self, name, filename):
        #im = gtk.Image()
        #im.set_from_file(filename)
        #pb = im.get_pixbuf()
        try:
            pb = gtk.gdk.pixbuf_new_from_file_at_size(filename, 32, 32)
            icon_set = gtk.IconSet(pb)
            self._register_icon_set(icon_set, name)
        except:
            #XXX: there is a image loader missing
            #     for *.svg its librsvg + its gtk pixmap loader
            print(filename)
        # this is broken for some reason
        #gtk.icon_theme_add_builtin_icon(name, gtk.ICON_SIZE_SMALL_TOOLBAR, pb)

    def _register_icon_set(self, icon_set, name):
        source = gtk.IconSource()
        source.set_icon_name(name)
        icon_set.add_source(source)
        self._factory.add(name, icon_set)




"""
I'm trying to create icons in python and GTK3 for AppIndicator3 , which is using stock items.
When using existing stock icons (like indicator-messages everything is fine.
But when I create my own stock icon it is not displayed (I used both svg and png image). What can be wrong?

I have this code to add icon factory:

from gi.repository import Gtk
from gi.repository import AppIndicator3 as appindicator
import os

_curr_dir=os.path.split(__file__)[0]

if __name__ == "__main__":

    icon_factory=Gtk.IconFactory()
    icon_source=Gtk.IconSource()
    f=os.path.join(_curr_dir, 'pics', 'test.svg')
    if not os.path.exists(f):
        raise Exception('Image %s missing'%f)
    icon_source.set_filename(f)
    icon_source.set_size_wildcarded(True)
    icon_set=Gtk.IconSet()
    icon_set.add_source(icon_source)
    icon_factory.add('myapp-icon', icon_set)
    icon_factory.add_default()

    ind = appindicator.Indicator.new (
                          "example-simple-client",
                          "myapp-icon",
                          appindicator.IndicatorCategory.APPLICATION_STATUS)
    ind.set_status (appindicator.IndicatorStatus.ACTIVE)
    ind.set_attention_icon ("indicator-messages-new")
    ind.set_label("test", "test")
"""

#w = gtk.Window()
#i = gtk.Image()
#i.set_from_stock("foo", gtk.ICON_SIZE_DIALOG)
#w.add(i)
#w.show_all()
#w.connect('destroy', gtk.main_quit)
#gtk.main()
