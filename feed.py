

header_template = '''
<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" version="2.0">
<channel>
<title>{title}</title>
<link>{comment}<link>
<language>en-ca</language>
<itunes:author>{artist}</itunes:author>
<itunes:owner>
    <itunes:name>{artist}</itunes:name>
</itunes:owner>
<itunes:explicit>yes</itunes:explicit>
<itunes:image href="http://www.example.com/podcast-icon.jpg" />
<itunes:category text="Category Name"/></itunes:category>
'''


episode_template = '''
<item>
    <title>{show_title}</title>
    <itunes:summary>{show_description}</itunes:summary>
    <description>{show_description}</description>
    <link>{comment}</link>
    <enclosure url="{show_url}" type="audio/mpeg" length="{show_size_in_bytes}"></enclosure>
    <pubDate>{start_date} ...Thu, 21 Dec 2016 16:01:07 +0000</pubDate>
    <itunes:author>{artist}</itunes:author>
    <itunes:duration>{show_duration}</itunes:duration>
    <itunes:explicit>yes</itunes:explicit>
    <guid>{show_url}</guid>
</item>
'''

footer_template = '''</channel>
</rss>
'''
