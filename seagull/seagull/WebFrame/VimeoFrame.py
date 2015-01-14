#!/usr/bin/env python

from gi.repository import Gtk, GdkPixbuf, GooCanvas
import urllib2
from xml.dom.minidom import parseString

from AbstractFrame import AbstractFrame

from seagull.Viewers import VimeoPlayer
from seagull_lib import helpers

def getCleanTag(dom, tag):
    return dom.getElementsByTagName(tag)[0].toxml().replace("<%s>" % tag, "").replace("</%s>" % tag, "")

class VimeoFrame(AbstractFrame):
    def __init__(self, parent, width, x, y, url):
        self.url = url
        self.vid_id = url.split("/")[-1].replace("#", "")
        api_req_string = "http://vimeo.com/api/v2/video/%s.xml" % self.vid_id
        try:
            xml = urllib2.urlopen(api_req_string).read()
        except:
            xml = None
        if xml:
            self.dom = parseString(xml)
            self.title = getCleanTag(self.dom, "title")
            self.url = getCleanTag(self.dom, "url")
            self.thumbnail_url = getCleanTag(self.dom, "thumbnail_medium")
        else:
            self.thumbnail_url = "http://www.example.com"
        
        super(VimeoFrame, self).__init__(parent, width, x, y, self.thumbnail_url)
        self.set_share_url(self.url)
        
        #Add Vimeo badge
        vimeo_icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(helpers.get_media_file("vimeo.png"))
        self.vimeo_icon = Gtk.Image()
        self.vimeo_icon.set_from_pixbuf(vimeo_icon_pixbuf)
        GooCanvas.CanvasWidget(parent=self, x=5, y=5, widget=self.vimeo_icon)
        
    def on_clicked(self, target, event, data=None):
        VimeoPlayer(self.vid_id, self.title)
