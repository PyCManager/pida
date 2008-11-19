# -*- coding: utf-8 -*-
"""
    :copyright: 2005-2008 by The PIDA Project
    :license: GPL 2 or later (see README/COPYING/LICENSE)
"""
from cgi import escape

import gtk
import gobject


# PIDA Imports
from pida import PIDA_VERSION

from pida.core.service import Service
from pida.core.features import FeaturesConfig
from pida.core.commands import CommandsConfig
from pida.core.events import EventsConfig
from pida.core.actions import ActionsConfig
from pida.core.actions import TYPE_NORMAL, TYPE_MENUTOOL, TYPE_RADIO, TYPE_TOGGLE

from pida.ui.views import PidaGladeView

from pida.utils.launchpadder.gtkgui import PasswordDialog
from pida.utils.launchpadder.lplib import save_local_config, get_local_config,\
                                          report
from pida.utils.gthreads import AsyncTask, gcall

# locale
from pida.core.locale import Locale
locale = Locale('bugreport')
_ = locale.gettext

class BugreportView(PidaGladeView):

    key = 'bugreport.form'
    
    gladefile = 'bugreport'
    locale = locale

    icon_name = 'error'
    label_text = _('Bug Report')

    def on_ok_button__clicked(self, button):
        self.email, self.password = get_local_config()
        if self.email is None:
            self.get_pass()
        if self.email is None:
            return
        self.progress_bar.set_text('')
        task = AsyncTask(self.report, self.report_complete)
        task.start()
        self._pulsing = True
        self.progress_bar.show()
        gobject.timeout_add(100, self._pulse)

    def on_close_button__clicked(self, button):
        self.svc.get_action('show_bugreport').set_active(False)

    def report(self):
        title = self.title_entry.get_text()
        buf = self.description_text.get_buffer()
        description = buf.get_text(buf.get_start_iter(), buf.get_end_iter())
        description = 'PIDA %s\n--\n%s' % (PIDA_VERSION, description)
        return report(None, self.email, self.password, 'pida', title, description)

    def report_complete(self, success, data):
        if success:
            self.svc.boss.cmd('notify', 'notify', title=_('Bug Reported'), data=data)
            self.title_entry.set_text('')
            self.description_text.get_buffer().set_text('')
            self.svc.boss.cmd('browseweb', 'browse', url=data.strip())
        else:
            self.svc.boss.cmd('notify', 'notify', title=_('Bug Report Failed'), data=data)
        self.progress_bar.hide()
        self._pulsing = False

    def _pulse(self):
        self.progress_bar.pulse()
        return self._pulsing

    def get_pass(self):
        pass_dlg = PasswordDialog()
        def pass_response(dlg, resp):
            dlg.hide()
            if resp == gtk.RESPONSE_ACCEPT:
                self.email, self.password, save = dlg.get_user_details()
                if save:
                    save_local_config(self.email, self.password)
            dlg.destroy()
        pass_dlg.connect('response', pass_response)
        pass_dlg.run()

    def can_be_closed(self):
        self.svc.get_action('show_bugreport').set_active(False)


class BugreportActions(ActionsConfig):
    
    def create_actions(self):
        self.create_action(
            'show_bugreport',
            TYPE_TOGGLE,
            _('Bug report'),
            _('Make a bug report'),
            'error',
            self.on_report
        )

    def on_report(self, action):
        if action.get_active():
            self.svc.show_report()
        else:
            self.svc.hide_report()


# Service class
class Bugreport(Service):
    """Describe your Service Here""" 

    actions_config = BugreportActions

    def pre_start(self):
        self._view = BugreportView(self)
    
    def show_report(self):
        self.boss.cmd('window', 'add_view', paned='Terminal', view=self._view)

    def hide_report(self):
        self.boss.cmd('window', 'remove_view', view=self._view)

# Required Service attribute for service loading
Service = Bugreport



# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
