import os
import datetime
import shutil
import subprocess

from schedules import time_to_key, key_to_datetime, read_schedule


def index_from_filelist(filelist):
    index = []  # (start_key, end_key, filename)
    for filename in filelist:
        if filename.startswith('.'):
            continue

        name, ext = filename.rsplit('.', 1)
        timestamp = name.replace('dump_end_', '')

        # Apr03_2018_20_00
        end_time = datetime.datetime.strptime(timestamp, '%b%d_%Y_%H_%M')
        start_time = end_time - datetime.timedelta(0, 60 * 60 * 2)  # 2 hours

        start_key = time_to_key(start_time)
        end_key = time_to_key(end_time)
        index.append((
            start_key,
            end_key,
            filename
        ))

    return sorted(index)


def extent_from_index(index):
    return index[0][0], index[-1][1]


def extent_from_schedule_item(item):
    start = item['details']['start_key']
    end = item['details']['end_key']

    return start, end


def overlap_from_schedule_and_extents(schedule, start, end):
    '''
    Given a start and end extents, filter out show from the schedule
    which aren't contained by the extents.

    Partial overlaps are excluded
    '''
    overlap = []
    for item in schedule:
        item_start, item_end = extent_from_schedule_item(item)
        if not (item_end <= start or item_start >= end):
            overlap.append(item)

    return overlap


def calculate_offset(a, b):
    delta = key_to_datetime(b) - key_to_datetime(a)
    return delta.seconds // 60


def edits_from_show(show, audio_index):
    show_start, show_end = extent_from_schedule_item(show)
    edits = []

    end_flag = False

    for audio_start, audio_end, filename in audio_index:
        edit_start = 0
        if end_flag is False:
            if audio_end <= show_start:
                continue
            if audio_start == show_start:
                edit_start = 0
                end_flag = True
            else:
                offset = calculate_offset(audio_start, show_start)
                edit_start = offset
                end_flag = True

        if audio_end < show_end:
            edits.append((filename, edit_start, 120))
            continue
        if audio_end == show_end:
            edit_end = 120
        else:
            offset = calculate_offset(audio_start, show_end)
            edit_end = offset

        edits.append((filename, edit_start, edit_end))
        break

    return edits


def exclude_show(show):
    if show['details']['name'].endswith('*'):
        return True
    return False


def shows_and_edits_from_schedule(schedule):
    '''
    Given the schedule output what edits would be need to edit out every
    show
    '''
    audio_files = os.listdir('test_data')
    audio_index = index_from_filelist(audio_files)
    extent_start, extent_end = extent_from_index(audio_index)

    overlap = overlap_from_schedule_and_extents(
        schedule,
        extent_start,
        extent_end,
    )

    ret = []  # (show, edits)

    for item in overlap:
        if exclude_show(item):
            continue
        edits = edits_from_show(item, audio_index)
        ret.append((item, edits))

    return ret


# mp3split implementation
def edit_to_split(edit):
    filename, start, end = edit
    return(
        os.path.join('test_data', filename),
        '{}.0'.format(start),
        '{}.0'.format(end),
    )


def mp3split(split, output_path):
    filename, start, end = split

    ret = subprocess.call(
        'mp3splt -d {} {} {} {}'.format(
            output_path,
            filename,
            start,
            end,
        ),
        shell=True
    )

    if ret != 0:
        print('Unexpected error while spliting.')


def do_split(show, edits):
    name = show['details']['name'].replace(' ', '_')
    instance_id = show['details']['instance_id']
    dirname = '{name}-{instance_id}'.format(
        name=name,
        instance_id=instance_id
    )

    output_path = os.path.join('output', dirname)
    try:
        os.makedirs(output_path)
    except FileExistsError:
        pass

    for edit in edits:
        filename, start, end = edit
        if start == 0 and end == 120:
            shutil.copy(
                os.path.join('test_data', filename),
                os.path.join(output_path, filename)
            )
        else:
            split = edit_to_split(edit)
            mp3split(split, output_path)

    return output_path


def mp3cat(directory_path, output_filename):
    '''
    Requires mp3cat to be installed on the local path
    https://github.com/dmulholland/mp3cat
    '''
    ret = subprocess.call(
        'mp3cat -d {} -o {}'.format(
            directory_path,
            output_filename,
        ),
        shell=True
    )

    if ret != 0:
        print('Unexpected error while joining.')


def do_join(show, split_directory):
    name = show['details']['name'].replace(' ', '_')
    instance_id = show['details']['instance_id']
    output_filename = '{name}-{instance_id}.mp3'.format(
        name=name,
        instance_id=instance_id
    )
    output_filename = os.path.join('output', output_filename)

    filenames = os.listdir(split_directory)
    if len(filenames) == 1:
        shutil.copy(
            os.path.join(split_directory, filenames[0]),
            output_filename,
        )
    else:
        mp3cat(split_directory, output_filename)

    return output_filename


if __name__ == '__main__':
    schedule = read_schedule('2018-04-02T00-00.json')
    shows_and_edits = shows_and_edits_from_schedule(schedule)
    print(shows_and_edits)

    test_show_and_edits = [(
        {'key': '2018-04-03T16-00', 'details': {'instance_id': 28511, 'name': 'Mazaj Show', 'start_key': '2018-04-03T16-00', 'end_key': '2018-04-03T19-30'}},
        [
            ('dump_end_Apr03_2018_18_00.mp3', 0, 120),
            ('dump_end_Apr03_2018_20_00.mp3', 0, 90),
        ]
    )]

    #for show, edits in test_show_and_edits:
    #    split_directory = do_split(show, edits)
    #    print(do_join(show, split_directory))
