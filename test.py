from pydub import AudioSegment


foo = AudioSegment.from_mp3('test_data/dump_end_Apr03_2018_18_00.mp3')

first_mintue = foo[:60*1000]

first_mintue.export("output/test.mp3", format="mp3")
