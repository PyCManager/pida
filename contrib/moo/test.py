import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from contrib.moo.moobigpaned import BigPaned
from contrib.moo.moopane import (
    PANE_POS_RIGHT,
    PANE_POS_LEFT,
    PANE_POS_TOP,
    PANE_POS_BOTTOM
)


class Window(Gtk.Window):
    """
    """
    paned: Gtk.Widget
    textview: Gtk.TextView
    swin: Gtk.Widget
    buffer: Gtk.TextBuffer

    def __init__(self):
        """
        """
        Gtk.Window.__init__(self, title="Test de GtkLed")
        self.set_default_size(800, 600)
        self.connect("destroy", Gtk.main_quit, None)
        paned = BigPaned()
        paned.set_property('enable-detaching', True)
        paned.show_all()
        textview = Gtk.TextView()
        textview.set_wrap_mode(Gtk.WrapMode.WORD)
        buffer = textview.get_buffer()
        buffer.insert_at_cursor("Click a button. Click a button. "
                                "Click a button. Click a button. Click a button. Click a button. "
                                "Click a button. Click a button. Click a button. Click a button. "
                                "Click a button. Click a button. Click a button. Click a button. "
                                "Click a button. Click a button. Click a button. Click a button. "
                                "Click a button. Click a button. Click a button. Click a button. "
                                "Click a button. Click a button. Click a button. Click a button. "
                                "Click a button. Click a button. Click a button. Click a button. "
                                "Click a button. Click a button. Click a button. Click a button. "
                                "Click a button. Click a button. Click a button. Click a button. "
                                "Click a button. Click a button. Click a button. Click a button. "
                                "Click a button. Click a button. Click a button. Click a button. ", -1)
        swin = Gtk.ScrolledWindow()
        swin.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC,
        )
        paned.add_child(swin)
        swin.add(textview)
        swin.show_all()
        paned.add_panes(PANE_POS_RIGHT)
        paned.add_panes(PANE_POS_LEFT)
        paned.add_panes(PANE_POS_TOP)
        paned.add_panes(PANE_POS_BOTTOM)
        self.add(paned)


if __name__ == "__main__":
    w = Window()
    w.show_all()
    Gtk.main()
