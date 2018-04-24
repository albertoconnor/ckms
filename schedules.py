import os
import json
import datetime

from dateutil.parser import parse


class Show:
    def __init__(self, name, show_id, start_time, end_time):
        self.name = name
        self.show_id = show_id
        self.start_time = start_time
        self.end_time = end_time


def time_to_key(time):
    return time.strftime('%Y-%m-%dT%H-%M')


def key_to_datetime(key):
    return datetime.datetime.strptime(key, '%Y-%m-%dT%H-%M')


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
    key = time_to_key(start)
    return {
        'key': key,
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


def write_schedule(schedule):
    filename = "{}.json".format(schedule[0]['key'])
    path = os.path.join('schedules', filename)
    content = json.dumps(schedule)
    with open(path, 'w') as f:
        f.write(content)

    return filename


def read_schedule(filename):
    with open(os.path.join('schedules', filename), 'r') as f:
        schedule = json.loads(f.read())

    return schedule


if __name__ == '__main__':
    with open('schedule_apr_2018.json', 'r') as f:
        test_schedule = f.read()

    schedule = transform_downloaded_schedule(test_schedule)

    path = write_schedule(schedule)

    read_schedule = read_schedule(path)

    assert read_schedule == schedule
