CKMS Project

Automatic podcast for those who want it.
Delay of 2 hour ok while files get written

Copy files from studio server -> VPS machine
Python script which run periodically
Slices mp3 into shows + Write ID3 tags-> S3, cleanup files when it is done with them....
Write postcast feed 3 h
Other data pushing

Initial Python Script work
(Open Source)
Schedule
6ish files

Map from files to time, see how they overlap with the schedule, and then splice... (the filename could store the times, use seconds since the epoch after splitting)

Input
Dark ice file
schedule http://airtime.soundfm.ca/api/week-info/
Meta data from other sources (wordpress/civ crm)

Process
https://github.com/jiaaro/pydub/

Output
Mp3 files with idtags to S3
Podcast xml

Could hours a week for a few weeks... 5 week, 2 hours a week, but then there the qsoft... about 10 hours to start with.



