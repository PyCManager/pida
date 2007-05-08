import gtk
from moo_stub import BigPaned, PaneLabel, PaneParams
from pida.utils.gthreads import gcall

PANE_TERMINAL = 'Terminal'
PANE_EDITOR = 'Editor'
PANE_BUFFER = 'Buffer'
PANE_PLUGIN = 'Plugin'

POS_MAP = {
    PANE_TERMINAL: gtk.POS_BOTTOM,
    PANE_BUFFER: gtk.POS_LEFT,
    PANE_PLUGIN: gtk.POS_RIGHT,
}

class PidaPaned(BigPaned):

    def __init__(self):
        BigPaned.__init__(self)
        self.set_property('enable-detaching', True)
        for pane in self.get_all_paneds():
            pane.set_pane_size(200)
            #pane.set_sticky_pane(True)

    def get_all_pos(self):
        return [gtk.POS_BOTTOM, gtk.POS_LEFT, gtk.POS_RIGHT]
        
    def get_all_paneds(self):
        for pos in self.get_all_pos():
            yield self.get_paned(pos)

    def add_view(self, name, view, removable=True, present=True):
        if name == PANE_EDITOR:
            self.add_child(view.get_toplevel())
        else:
            POS = POS_MAP[name]
            lab = PaneLabel(view.icon_name, None, view.label_text)
            pane = self.insert_pane(view.get_toplevel(), lab, POS, POS)
            if not removable:
                pane.set_property('removable', False)
            pane.connect('remove', view.on_remove_attempt)
            if present:
                gcall(self.present_pane, view.get_toplevel())
            self.show_all()

    def remove_view(self, view):
        self.remove_pane(view.get_toplevel())

    def detach_view(self, view, size=(400,300)):
        paned, pos = self.find_pane(view.get_toplevel())
        paned.detach_pane(pos)
        self._center_on_parent(view, size)

    def present_view(self, view):
        pane, pos = self.find_pane(view.get_toplevel())
        pane.present()

    def get_open_pane(self, name):
        POS = POS_MAP[name]
        paned = self.get_paned(POS)
        pane = paned.get_open_pane()
        return paned, pane

    def switch_next_pane(self, name):
        paned, pane = self.get_open_pane(name)
        if pane is None:
            return
        num = pane.get_index()
        newnum = num + 1
        if newnum == paned.n_panes():
            newnum = 0
        newpane = paned.get_nth_pane(newnum)
        newpane.present()

    def switch_prev_pane(self, name):
        paned, pane = self.get_open_pane(name)
        if pane is None:
            return
        num = pane.get_index()
        newnum = num - 1
        if newnum == -1:
            newnum = paned.n_panes() - 1
        newpane = paned.get_nth_pane(newnum)
        newpane.present()

    def _center_on_parent(self, view, size):
        gdkwindow = view.get_parent_window()
        px, py, pw, ph, pbd = view.svc.boss.get_window().window.get_geometry()
        w, h = size
        cx = (pw - w) / 2
        cy = (ph - h) / 2
        gdkwindow.move_resize(cx, cy, w, h)
        #gdkwindow.resize(w, h)

