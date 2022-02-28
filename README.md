# hansible-modules

Ansible modules needed for hansible

## stdout callback

`ffpp.hansible_modules.hansible_export`

Set UNIX-Socket in envvar `HANSIBLE_OUTPUT_SOCKET`, if not set, data is sent to `stdout`.

### Output

#### Events

* `pb_start`
* `play_start`
* `task_start`
* `task_runner_start`
* `task_runner_result`
* `no_hosts_matched`
* `no_hosts_remain`
* `end`

#### Data

The `task_runner_result` event sets all available variables, thus serves as a good example.

Since ansible does not require unique names for playbooks, plays and tasks, a run-unique ID is assigned by the respective `_start` event.

```json
{
    "event": "task_runner_result",
    "playbook": "pb.yml",
    "playbook_id": 1,
    "play": "Test",
    "play_id": 1,
    "task": "Print username",
    "task_id": 4,
    "host": "localhost",
    "is_changed": false,
    "is_skipped": false,
    "is_failed": false,
    "is_unreachable": false,
    "ignore_errors": false,
    "delegate": false,
    "delegate_host": "",
    "is_item": false,
    "item": ""
}
```
