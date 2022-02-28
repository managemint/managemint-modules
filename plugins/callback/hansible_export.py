from ansible.plugins.callback import CallbackBase

import json
import os
import socket

# Refernce for all callbacks
# https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/callback/__init__.py#L508

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "stdout"
    CALLBACK_NAME = "hansible-export"

    SOCKET_VAR = 'HANSIBLE_OUTPUT_SOCKET'

    def __init__(self):
        super(CallbackModule, self).__init__()

        self._current_playbook = ''
        self._current_play = ''

        self._playbook_cnt = 0
        self._play_cnt = 0
        self._task_cnt = 0

        self._stdout = self.SOCKET_VAR not in os.environ

        if not self._stdout:
            self._sockpath = os.environ[self.SOCKET_VAR]
            self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    def _out(self, **kwargs):
        if self._stdout:
            print(json.dumps(kwargs, indent = 4))
            print('--------------------------')
        else:
            self._sock.sendto(bytes(json.dumps(kwargs), 'utf-8'), self._sockpath)

    def _on_runner(self, result, is_item = False, ignore_errors = False):
        delegate = False
        delegate_host = ''
        item = ''

        if is_item:
            item = result._result.get('_ansible_item_label', result._result.get('item'))

        if result._task.delegate_to and result._task.delegate_to != result._host.get_name():
            delegate = True
            delegate_host = result._task.delegate_to

        #from ansible.vars.clean import strip_internal_keys, module_response_deepcopy
        #data = strip_internal_keys(module_response_deepcopy(result._result))

        self._out(
                event = 'task_runner',
                playbook = self._current_playbook,
                playbook_id = self._playbook_cnt,
                play = self._current_play,
                play_id = self._play_cnt,
                name = result.task_name,
                task_id = self._task_cnt,
                host = result._host.get_name(),
                is_changed = result.is_changed(),
                is_skipped = result.is_skipped(),
                is_failed = result.is_failed(),
                is_unreachable = result.is_unreachable(),
                ignore_errors = ignore_errors,
                delegate = delegate,
                delegate_host = delegate_host,
                is_item = is_item,
                item = item
                #result = data
                )

    def v2_on_any(self, *args, **kwargs):
        pass

    def v2_playbook_on_start(self, playbook):
        # ansible.playbook.Playbook
        name = playbook._file_name
        self._current_playbook = name
        self._playbook_cnt += 1

        self._out(event = 'pb_start', name = name, playbook_id = self._playbook_cnt)

    def v2_playbook_on_play_start(self, play):
        # ansible.playbook.play.Play
        name = play.name
        self._current_play = name

        self._play_cnt += 1

        self._out(event = 'play_start', name = name, play_id = self._play_cnt)

    def v2_playbook_on_task_start(self, task, is_conditional):
        # ansible.playbook.task.Task

        self._task_cnt += 1

        self._out(event = 'task_start', name = task.get_name(), task_id = self._task_cnt, is_conditional=is_conditional)

    def v2_playbook_on_no_hosts_remaining(self):
        self._out(event = 'no_hosts_remain')

    def v2_playbook_on_no_hosts_matched(self):
        self._out(event = 'no_hosts_matched')

    def v2_playbook_on_stats(self, stats):
        # ansible.executor.stats.AggregateStats
        # TODO?
        pass

    def v2_runner_on_ok(self, result):
        self._on_runner(result)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self._on_runner(result, ignore_errors = ignore_errors)

    def v2_runner_on_skipped(self, result):
        self._on_runner(result)

    def v2_runner_on_unreachable(self, result):
        self._on_runner(result)

    def v2_runner_item_on_ok(self, result):
        self._on_runner(result, is_item = True)

    def v2_runner_item_on_failed(self, result):
        self._on_runner(result, is_item = True)

    def v2_runner_item_on_skipped(self, result):
        self._on_runner(result, is_item = True)
