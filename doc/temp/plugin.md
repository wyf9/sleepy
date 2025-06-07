# plugin temp doc

## events

`status_updated`, old_static, new_status
`device_updated`, device_id, device
`device_removed`, device_id, device
`device_cleared`, devices[device]
`private_mode_changed`, old_mode, new_mode
`data_saved`, data
`app_started`

## modifies

- plugin route return:
  - dict / list: to json (format_dict)
  - str: to html
  - others: to str

## add functions
