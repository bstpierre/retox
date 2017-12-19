# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import asciimatics.widgets as widgets
from asciimatics.screen import Screen
from retox.log import retox_log

TASK_NAMES = {
    'runtests': u"Run Tests",
    'command': u"Custom Command",
    'installdeps': u"Install Dependencies",
    'installpkg': u"Install Package",
    'inst': u"Install",
    'inst-nodeps': u"Install no-deps",
    'sdist-make': u"Make sdist",
    'create': u"Create",
    'recreate': u"Recreate",
    'getenv': u"Get environment"
}

RESULT_MESSAGES = {
    0: u'✓',
    'commands failed': u'✗'
}

class VirtualEnvironmentFrame(widgets.Frame):
    def __init__(self, screen, venv_name, venv_count, count):
        super(VirtualEnvironmentFrame, self).__init__(
            screen,
            screen.height // 2,
            screen.width // venv_count,
            x=count * (screen.width // venv_count) + 1,
            has_border=True,
            hover_focus=True,
            title=venv_name)
        self.name = venv_name
        self._screen = screen

        # Draw a box for the environment
        task_layout = widgets.Layout([10], fill_frame=False)
        self.add_layout(task_layout)
        completed_layout = widgets.Layout([10], fill_frame=False)
        self.add_layout(completed_layout)
        self._task_view = widgets.ListBox(
            10,
            [],
            name=u"Tasks",
            label=u"Running")
        self._completed_view = widgets.ListBox(
            10,
            [],
            name=u"Completed",
            label=u"Completed")
        task_layout.add_widget(self._task_view)
        completed_layout.add_widget(self._completed_view)
        self.fix()

    def start(self, activity, action):
        '''
        Mark an action as started
        '''
        try:
            self._start_action(activity, action)
        except ValueError:
            retox_log.debug("Could not find action %s in env %s" % (activity, self.name))
        self.refresh()

    def stop(self, activity, action):
        '''
        Mark a task as completed
        '''
        try:
            self._remove_running_action(activity, action)
        except ValueError:
            retox_log.debug("Could not find action %s in env %s" % (activity, self.name))
        self._mark_action_completed(activity, action)
        self.refresh()

    def finish(self, status):
        '''
        Move laggard tasks over
        '''
        retox_log.info("Completing %s with status %s" % (self.name, status))
        result = Screen.COLOUR_GREEN if not status else Screen.COLOUR_RED
        self.palette['title'] = (Screen.COLOUR_WHITE, Screen.A_BOLD, result)
        for item in list(self._task_view.options):
            self._task_view.options.remove(item)
            self._completed_view.options.append(item)
        self.refresh()

    def reset(self):
        '''
        Reset the frame between jobs
        '''
        self.palette['title'] = (Screen.COLOUR_WHITE, Screen.A_BOLD, Screen.COLOUR_BLUE)
        self._completed_view.options = []
        self._task_view.options = []
        self.refresh()

    def refresh(self):
        self._screen.force_update()
        self._screen.refresh()
        self._update(1)

    def _start_action(self, activity, action):
        self._task_view.options.append(self._make_list_item_from_action(activity, action))

    def _remove_running_action(self, activity, action):
        self._task_view.options.remove(self._make_list_item_from_action(activity, action))

    def _mark_action_completed(self, activity, action):
        name, value = self._make_list_item_from_action(activity, action)
        name = RESULT_MESSAGES.get(action.venv.status, str(action.venv.status)) + ' ' + name
        self._completed_view.options.append((name, value))

    def _make_list_item_from_action(self, activity, action):
        return TASK_NAMES.get(activity, activity), self.name
