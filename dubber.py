from pydub import AudioSegment

from schedules import Show


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


def shows_and_edit_from_schedule(schedule):
    '''
    Given the schedule output what edits would be need to edit out every
    show
    '''
    # ..:if expand("%") == ""|browse confirm w|else|confirm w|endif
    .


if __name__ == '__main__':
    test_show = Show(
        'Mazaj Show',
        1010,
        None,
        None,
    )

    test_edits = [
        dict(
            filename='test_data/dump_end_Apr03_2018_18_00.mp3',
        ),
        dict(
            filename='test_data/dump_end_Apr03_2018_20_00.mp3',
            end=minutes_to_microseconds(90),
        ),
    ]

    dub_show(test_show, test_edits)
