import os
import datetime

from dateutil.parser import parse

from pydub import AudioSegment

from schedules import Show, time_to_key, read_schedule


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


def index_from_filelist(filelist):
    index = []  # (start_key, end_key, filename)
    for filename in filelist:
        if filename.startswith('.'):
            continue

        name, ext = filename.rsplit('.', 1)
        timestamp = name.replace('dump_end_', '')

        # Apr03_2018_20_00
        end_time = datetime.datetime.strptime(timestamp, '%b%d_%Y_%H_%M')
        start_time = end_time - datetime.timedelta(0,120)  # 2 hours

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
    start = item['key']
    end = item['details']
    end = parse(item['details']['end_timestamp'])
    end = time_to_key(end)

    return start, end


def shows_and_edit_from_schedule(schedule):
    '''
    Given the schedule output what edits would be need to edit out every
    show
    '''
    audio_files = os.listdir('test_data')
    audio_index = index_from_filelist(audio_files)
    extent_start, extent_end = extent_from_index(audio_index)

    schedule_overlap = []
    for item in schedule:
        item_start, item_end = extent_from_schedule_item(item)
        if not (item_end < extent_start or item_start > extent_end):
            schedule_overlap.append(item)

    # WIP
    # import pdb; pdb.set_trace()


if __name__ == '__main__':
    schedule = read_schedule('2018-04-02T00-00.json')
    shows_and_edit_from_schedule(schedule)
