from gi.repository import Gtk, Gdk, GObject, GdkPixbuf
from crm.helpers.utils.gsignal import gsignal, gproperty

from enum import Enum

(
    PANE_POS_RIGHT,
    PANE_POS_LEFT,
    PANE_POS_TOP,
    PANE_POS_BOTTOM
) = range(4)


class SmallIcon(Enum):
    """
    """
    SMALL_ICON_HIDE = 0
    SMALL_ICON_STICKY = 1
    SMALL_ICON_CLOSE = 2
    SMALL_ICON_DETACH = 3
    SMALL_ICON_ATTACH = 4
    SMALL_ICON_KEEP_ON_TOP = 5


class Icon:
    """
    """
    def _create_small_icon(self, icon: SmallIcon) -> Gtk.Widget:
        """
        :param icon:
        :return:
        """

    def _create_arrow_icon(self, arrow_type: Gtk.ArrowType):
        """
        :param arrow_type:
        :return:
        """


class PaneParams:
    """
    """
    window_position: Gdk.Rectangle
    detached: int = 1
    maximized: int = 1
    keep_on_top: int = 1

    def copy(self):
        """
        :return:
        """

    def free(self):
        """
        :return:
        """


class PaneLabel:
    __gtype_name__ = 'PaneLabel'

    icon_stock_id: str
    icon_pixbuf: GdkPixbuf
    label: str
    window_title: str

    def __init__(
            self,
            icon_stock_id: str = None,
            icon_pixbuf: GdkPixbuf = None,
            icon_widget=None,
            label_text: str = None,
            window_title: str = None
    ):
        """
        """


class Pane:
    """
    """

    def __init__(self):
        """
        """

    @staticmethod
    def new(child: Gtk.Widget, label: PaneLabel):
        """
        :param child:
        :param label:
        :return
        """

    def get_id(self) -> str:
        """
        :return:
        """
    def _set_id(self, pane_id: str) -> None:
        """
        :param pane_id:
        :return:
        """

    def get_label(self) -> PaneLabel:
        """
        :return:
        """

    def set_label(self, label: PaneLabel) -> None:
        """
        :param label:
        :return:
        """

    def set_frame_markup(self, markup: str) -> None:
        """
        :param markup:
        :return:
        """

    def set_frame_text(self, text: str) -> None:
        """
        :param text:
        :return:
        """

    def get_params(self) -> PaneParams:
        """
        :return:
        """

    def set_params(self, params: PaneParams) -> None:
        """
        :param params:
        :return:
        """

    def get_detachable(self) -> bool:
        """
        :return:
        """

    def set_detachable(self, detachable: bool) -> None:
        """
        :param detachable:
        :return:
        """

    def get_removable(self) -> bool:
        """
        :return:
        """

    def set_removable(self, removable: bool) -> None:
        """
        :param removable:
        :return:
        """

    def get_child(self) -> Gtk.Widget:
        """
        :return:
        """

    def get_index(self) -> int:
        """
        :return:
        """

    def open(self) -> None:
        """
        :return:
        """

    def present(self) -> None:
        """
        :return:
        """

    def attach(self) -> None:
        """
        :return:
        """

    def detach(self) -> None:
        """
        :return:
        """

    def set_drag_dest(self) -> None:
        """
        :return:
        """

    def unset_drag_dest(self) -> None:
        """
        :return:
        """

    def _get_parent(self):
        """
        :return:
        """

    def _get_frame(self) -> Gtk.Widget:
        """
        :return:
        """

    def _update_focus_child(self) -> None:
        """
        :return:
        """

    def _focus_child(self) -> Gtk.Widget:
        """
        :return:
        """

    def _get_button(self) -> Gtk.Widget:
        """
        :return:
        """

    def _get_handle(self, big: Gtk.Widget, small: Gtk.Widget):
        """
        :param big:
        :param small:
        :return:
        """

    def _get_window(self) -> Gtk.Widget:
        """
        :return:
        """

    def _params_changed(self) -> None:
        """
        :return:
        """

    def _freeze_params(self) -> None:
        """
        :return:
        """

    def _thaw_params(self) -> None:
        """
        :return:
        """

    def _size_request(self, req: Gtk.Requisition) -> None:
        """
        :param req:
        :return:
        """

    def _get_size_request(self, req: Gtk.Requisition) -> None:
        """
        :param req:
        :return:
        """

    def _size_allocate(self, allocation: Gdk.Rectangle) -> None:
        """
        :param allocation:
        :return:
        """

    def get_detached(self) -> bool:
        """
        :return:
        """

    def _attach(self) -> None:
        """
        :return:
        """

    def _detach(self) -> None:
        """
        :return:
        """

    def _set_parent(self, parent, window: Gtk.Window):
        """
        :return:
        """

    def _unparent(self) -> None:
        """
        :return:
        """

    def _try_remove(self) -> None:
        """
        :return:
        """
