#!/usr/bin/env python

import gdata.youtube
import gdata.youtube.service
import os
from gi.repository import Gtk, GdkPixbuf, GooCanvas

from AbstractFrame import AbstractFrame

from seagull.Viewers import YoutubePlayer
from seagull_lib import helpers

class YoutubeFrame(AbstractFrame):
    def __init__(self, parent, width, x, y, url):
        #url may end with &feature or &recommends
        self.url = url.split('&')[0]
        self.set_share_url(self.url)
        #Get video id
        self.vid_id = self.url.split('v=')[1]
        #Get video information
        yt = gdata.youtube.service.YouTubeService()
        try:
            self.vid = yt.GetYouTubeVideoEntry(video_id=self.vid_id)
            self.title = self.vid.media.title.text
            self.thumbnail_url = self.vid.media.thumbnail[0].url
        except:
            print self.vid_id
            self.thumbnail_url = "http://www.example.com" #Or something that fails
        
        super(YoutubeFrame, self).__init__(parent, width, x, y, self.thumbnail_url)
        self.logger.info("Created new YoutubeFrame for %s" % self.url)
        
        youtube_icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(helpers.get_media_file("youtube.jpg"))
        self.youtube_icon = Gtk.Image()
        self.youtube_icon.set_from_pixbuf(youtube_icon_pixbuf)
        GooCanvas.CanvasWidget(parent=self, x=5, y=5, widget=self.youtube_icon)
    
    def on_clicked(self, target, event, data=None):
        YoutubePlayer(self.vid_id, self.title)
