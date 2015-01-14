#!/usr/bin/env python

from AbstractFrame import AbstractFrame
from gi.repository import Gtk
import os
from seagull.Viewers import ImageViewer

class ImageFrame(AbstractFrame):
    def __init__(self, parent, width, x, y, url):
        self.set_share_url(url)
        super(ImageFrame, self).__init__(parent, width, x, y, url)
        self.logger.info("Created new ImageFrame for %s" % url)
        
    def on_clicked(self, target, event, data=None):
        ImageViewer(self.pixbuf)
