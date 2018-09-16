import os
import json
import datetime

from dateutil.parser import parse

import requests


def time_to_key(time):
    return time.strftime('%Y-%m-%dT%H-%M')


def key_to_datetime(key):
    return datetime.datetime.strptime(key, '%Y-%m-%dT%H-%M')


def download_schedule(url):
    return requests.get(url).json()


def transform_downloaded_blob(downloaded_blob):
    '''
    blob example:
    {
        "start_timestamp": "2018-03-19 00:00:00",
        "end_timestamp": "2018-03-19 07:50:00",
        "name": "folk all night anutpilot*",
        "id": 611,
        "instance_id": 48481,
        "record": 0,
        "url": "",
        "starts": "2018-03-19 00:00:00",
        "ends": "2018-03-19 07:50:00"
    }
    '''
    start = parse(downloaded_blob['start_timestamp'])
    start_key = time_to_key(start)
    end = parse(downloaded_blob['end_timestamp'])
    end_key = time_to_key(end)
    downloaded_blob['start_key'] = start_key
    downloaded_blob['end_key'] = end_key
    return {
        'key': start_key,
        'details': downloaded_blob,
    }


def transform_downloaded_schedule(downloaded_schedule_text):
    downloaded_schedule = json.loads(downloaded_schedule_text)

    # {"key": "2018-04-01T22:30", "details": {...}} sorted by key
    new_schedule = []
    for key, day_list in downloaded_schedule.items():
        if key in ('AIRTIME_API_VERSION'):
            continue
        for blob in day_list:
            new_schedule.append(
                transform_downloaded_blob(blob)
            )

    return sorted(new_schedule, key=lambda d: d['key'])


def write_schedule(schedule, schedule_path='schedules'):
    filename = "{}.json".format(schedule[0]['key'])
    path = os.path.join(schedule_path, filename)
    content = json.dumps(schedule)
    with open(path, 'w') as f:
        f.write(content)

    return filename


def earliest_start(schedule):
    ret = None
    for item in schedule:
        start = item['details']['start_key']
        if ret is None or start < ret:
            ret = start
    return ret


def read_schedule(filename):
    with open(os.path.join('schedules', filename), 'r') as f:
        schedule = json.loads(f.read())

    return schedule


def read_all_schedules(schedule_path=None):
    if schedule_path is None:
        schedule_path = 'schedules'

    schedules = {}

    for filename in os.listdir(schedule_path):
        if not filename.endswith('.json'):
            continue

        path = os.path.join(schedule_path, filename)
        if not os.isfile(path):  # is dir
            continue

        with open(path, 'r') as f:
            schedule = json.loads(f.read())

        start = earliest_start(schedule)

        schedules[(start, path)] = schedule

    return sorted(schedules)


def join_schedules(schedule_list):
    ret = []
    for schedule in schedule_list:
        ret += schedule
    return ret


if __name__ == '__main__':
    with open('schedule_apr_2018.json', 'r') as f:
        test_schedule = f.read()

    schedule = transform_downloaded_schedule(test_schedule)

    path = write_schedule(schedule)

    read_schedule = read_schedule(path)

    assert read_schedule == schedule
