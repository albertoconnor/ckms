import os
import json

import click
from raven import Client

from . import schedules
from . import dubber


sentry_client = Client('https://<key>:<secret>@sentry.io/<project>')


@click.command()
@click.argument(
    'record_path',
    type=click.Path(
        exists=True,
        file_okay=False,
        readable=True,
    )
)
@click.option('--schedule-url', default='http://192.168.2.151/api/week-info/')
@click.option('--schedule-path', default='schedules')
@click.option('--history_path', default='history.json')
def cli(record_path, schedule_url, schedule_path, history_path):
    global sentry_client
    current_schedule = schedules.downloaded_schedule(schedule_url)
    schedule = schedules.transform_downloaded_schedule(current_schedule)
    schedules.write_schedule(schedule, schedule_path)

    schedules_dict = schedules.read_all_schedules(schedule_path)

    history = {}

    if os.is_file(history_path):
        with open(history_path, 'r') as f:
            history = json.loads(f.read())

    if len(schedules_dict) > 2:
        sentry_client.context.merge(dict(
            schedules_dict=schedules_dict,
        ))
        sentry_client.captureMessage('More than 3 schedules found')
        sentry_client.context.clear()
        # delete on of them, but which one? logging will tell us

    schedules_list = [schedules_dict[key] for key in schedules_dict]

    unified_schedule = schedules.join_schedules(schedules_list)

    shows_and_edits = dubber.shows_and_edits_from_schedule(
        unified_schedule,
        record_path,
    )

    shows_written = []
    for show, edits in shows_and_edits:
        if show in history:
            continue
        filename = dubber.dub_show(show, edits)
        shows_written.append(filename)
        history[show] = dict(filename=filename)

    history_json = json.dumps(history)
    with open(history_path, 'w') as f:
        f.write(history_json)

    sentry_client.context.merge(dict(
        shows_written=shows_written,
        history=history,
    ))
    sentry_client.captureMessage('Dubber run completed')
    sentry_client.context.clear()

    # Eventually tag, upload, and produce podcast feed...


if __name__ == '__main__':
    global sentry_client
    try:
        cli()
    except Exception:
        sentry_client.captureException()
