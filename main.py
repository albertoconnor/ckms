import os
import json

import click
import sentry_sdk

import schedules
import dubber


sentry_sdk.init("https://dc5cab9a48f84900a9decb152a64cfb2@sentry.io/1369605")


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
    current_schedule = schedules.download_schedule(schedule_url)
    schedule = schedules.transform_downloaded_schedule(current_schedule)
    schedules.write_schedule(schedule, schedule_path)

    schedules_dict = schedules.read_all_schedules(schedule_path)

    history = {}

    if os.path.isfile(history_path):
        with open(history_path, 'r') as f:
            history = json.loads(f.read())

    print(schedules_dict.keys())
    if len(schedules_dict.keys()) > 2:
        first_key = schedules_dict.keys()[0]
        start_key, path = first_key
        sentry_sdk.capture_message('Deleteing schedule file {}'.format(path))
        os.remove(path) # the underlying schedule file
        del schedules_dict[first_key]

    schedules_list = [schedules_dict[key] for key in schedules_dict]

    unified_schedule = schedules.join_schedules(schedules_list)

    shows_and_edits = dubber.shows_and_edits_from_schedule(
        unified_schedule,
        record_path,
    )

    shows_written = []
    for show, edits in shows_and_edits:
        if show['key'] in history:
            continue
        filename = dubber.dub_show(show, edits, record_path)
        shows_written.append(filename)
        history[show['key']] = dict(show=show, flename=filename)

    history_json = json.dumps(history)
    with open(history_path, 'w') as f:
        f.write(history_json)

    with sentry_sdk.configure_scope() as scope:
        scope.set_extra('shows_written', shows_written)
        scope.set_extra('history', history)
        sentry_sdk.capture_message('Dubber run completed')
    # Eventually tag, upload, and produce podcast feed...


if __name__ == '__main__':
    try:
        cli()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise e
