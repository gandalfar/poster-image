#!/usr/bin/env python
#
# Author: Jure Cuhalev
# License: GPL2 or greater
#
# Very rough but gets the work done.
#

import sys, os
import StringIO 

import urllib2
import urlparse
import json

from PIL import Image, ImageOps, ImageChops

import gdata.youtube
import gdata.youtube.service

def autocrop(im, bgcolor):
    if im.mode != "RGB":
        im = im.convert("RGB")
    bg = Image.new("RGB", im.size, bgcolor)
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return None

def save_thumbnail(video, title, url):
    new_filename = '%s - %s.jpg' % (video, title)
    img = urllib2.urlopen(url).read()
    im = Image.open(StringIO.StringIO(img))
    new_im = autocrop(im, 'black')
    new_im.save(new_filename, 'JPEG')

    print 'Written', new_filename

def grab_poster_image(url):
    if 'youtu' in url:
        url_data = urlparse.urlparse(url)
        query = urlparse.parse_qs(url_data.query)

        if 'youtu.be' in url:
            video = url.split('/')[3]
        else:
            video = query["v"][0]

        yt_service = gdata.youtube.service.YouTubeService()
        entry = yt_service.GetYouTubeVideoEntry(video_id=video)

        title = entry.media.title.text
        for thumb in entry.media.thumbnail:
            if thumb.width == '480':
                url = thumb.url

                save_thumbnail(video, title, url)

    elif 'vimeo' in url:
        video = url.split('/')[3]

        json_data = urllib2.urlopen('http://vimeo.com/api/v2/video/%s.json' % video).read()
        data = json.loads(json_data)[0]

        title = data['title']
        url = data['thumbnail_large']

        save_thumbnail(video, title, url)

    else:
        print 'Failed to recognize', url

if __name__ == '__main__':
    url = sys.argv[1]

    grab_poster_image(url)
