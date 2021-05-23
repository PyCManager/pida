from gi.repository import Gtk, GObject


class BigPaned (Gtk.Frame):
    __gtype_name__ = 'BigPaned'

    # indexed by PanePos
    paned: Gtk.Widget = [4]

    def __init__(self):
        Gtk.Frame.__init__(self)

    def add_child(self, widget: Gtk.Widget) -> None:
        """
        :param widget:
        :return:
        """
        self.add(widget)

    def remove_child(self) -> None:
        """
        :return:
        """

    def get_child(self) -> Gtk.Widget:
        """
        :return:
        """

    def set_config(self, config_string: str) -> None:
        """
        :param config_string:
        :return:
        """

    def get_config(self) -> str:
        """
        :return:
        """

    def add_panes(self, POSITION):
        """
        :param POSITION:
        :return:
        """
        print(POSITION)

    def insert_pane(self, pane_widget: Gtk.Widget, pane_id: str, pane_label, position, index: int):
        """
        :return:
        """

    def set_pane_order(self, order: int) -> None:
        """
        :param order:
        :return:
        """

    def find_pane(self, pane_widget: Gtk.Widget, child_paned):
        """
        :param pane_widget:
        :param child_paned:
        :return:
        """

    def remove_pane(self, pane_widget: Gtk.Widget) -> bool:
        """
        :param pane_widget:
        :return:
        """

    def lookup_pane(self, pane_id: str):
        """
        :param pane_id:
        :return:
        """

    def get_pane(self, position, index: int) -> Gtk.Widget:
        """
        :param position:
        :param index:
        :return:
        """

    def reorder_pane(self, pane_widget: Gtk.Widget, new_position, index: int) -> None:
        """
        :return:
        """

    def get_paned(self, position):
        """
        :param position:
        :return:
        """

    def open_pane(self, pane_widget: Gtk.Widget) -> None:
        """
        :param pane_widget:
        :return:
        """

    def hide_pane(self, pane_widget: Gtk.Widget) -> None:
        """
        :param pane_widget:
        :return:
        """

    def present_pane(self, pane_widget: Gtk.Widget) -> None:
        """
        :param pane_widget:
        :return:
        """

    def attach_pane(self, pane_widget: Gtk.Widget) -> None:
        """
        :param pane_widget:
        :return:
        """

    def detach_pane(self, pane_widget: Gtk.Widget) -> None:
        """
        :param pane_widget:
        :return:
        """
