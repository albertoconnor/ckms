import os
import datetime
import shutil
import subprocess

from pydub import AudioSegment

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
        edits = edits_from_show(item, audio_index)
        ret.append((item, edits))

    return ret


# pydubber implementation
def simple_loader(filename):
    return AudioSegment.from_mp3(filename)


def minutes_to_microseconds(minute):
    return minute * 60 * 1000


def dub_edits(edits, segments_loader):
    output_seg = None
    for edit in edits:
        source_seg = segments_loader(edit['filename'])
        start, end = edit.get('start'), edit.get('end')

        if start is None and end is None:
            cut_seg = source_seg
        elif end is None:
            cut_seg = source_seg[start:]
        elif start is None:
            cut_seg = source_seg[:end]
        else:
            cut_seg = source_seg[start:end]

        if output_seg is None:
            output_seg = cut_seg
        else:
            output_seg += cut_seg

    return output_seg


def dub_show(show, edits):
    output = dub_edits(edits, simple_loader)
    output.export(f'output/{show.name}.mp3')


# mp3split implementation
def edit_to_split(edit):
    filename, start, end = edit
    return(
        filename,
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
    dirname = '{name}-{instace_id}'.format(**show)
    output_path = os.path.join('output', dirname)
    os.makedirs(output_path)

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
