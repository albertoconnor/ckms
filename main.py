import datetime
import os
import json

import click
import sentry_sdk
from dotenv import load_dotenv

import schedules
import dubber


load_dotenv(dotenv_path='.env', verbose=True)


sentry_dns = os.getenv('SENTRY_DNS', '')
if sentry_dns == '':
    print(
        'No sentry_dns found, no logging available.'
        ' Define a .env file here with a SENTRY_DNS entry.'
    )
sentry_sdk.init(sentry_dns)


def trim_history(history):
    '''
    We don't want the history file growing indefinitately, so if we exclude
    show older than eight weeks, we should be ok.
    '''
    eight_weeks_ago = datetime.datetime.now() - datetime.timedelta(days=56)
    new_history = dict([
        (key, history[key]) for key in history
        if schedules.key_to_datetime(key) > eight_weeks_ago
    ])
    return new_history


@click.command()
@click.argument(
    'record_path',
    type=click.Path(
        exists=True,
        file_okay=False,
        readable=True,
    )
)
@click.option('--schedule-url', default='https://radiowaterloo.ca/wp-content/uploads/week-info.json')
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

    if len(schedules_dict.keys()) > 2:
        first_key = sorted(schedules_dict.keys())[0]
        start_key, path = first_key
        sentry_sdk.capture_message('Deleteing schedule file {}'.format(path))
        os.remove(path)  # the underlying schedule file
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

    history = trim_history(history)

    history_json = json.dumps(history)
    with open(history_path, 'w') as f:
        f.write(history_json)

    with sentry_sdk.configure_scope() as scope:
        scope.set_extra('shows_written', shows_written)
        scope.set_extra('history', history)
        sentry_sdk.capture_message('Dubber run completed')


if __name__ == '__main__':
    try:
        cli()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise e
