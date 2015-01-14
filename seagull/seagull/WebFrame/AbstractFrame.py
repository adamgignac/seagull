#!/usr/bin/env python

from gi.repository import Gtk, GdkPixbuf, GooCanvas, GwibberGtk
import urllib2
import os
import base64
import logging

FRAME_WIDTH = 10

class Dummy(object):
    def close(self):
        pass

def make_hash(url):
    return base64.urlsafe_b64encode(url)[:128]

class AbstractFrame(GooCanvas.CanvasGroup):
    def __init__(self, parent, width, x, y, pic_url):
        self.logger = logging.getLogger('seagull')
        width = width
        #Create pixbuf for thumbnail
        
        cache_dir = os.path.expanduser("~/.config/seagull/")
        #Check if cached
        cache_file = cache_dir + make_hash(pic_url) + ".png"
        if os.path.exists(cache_file):
            #Found cached file
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(cache_file)
        else:
            #Download file
            f = Dummy()
            try:
                f = urllib2.urlopen(pic_url)
                data = f.read()
                f.close()
            except urllib2.HTTPError, e:
                print e.code
            except urllib2.URLError, e:
                print e.reason
            except:
                print "Something has gone horribly wrong"
            finally:
                f.close()
            #Create pixbuf
            loader = GdkPixbuf.PixbufLoader()
            try:
                loader.write(data)
            except:
                print "Error making pixbuf"
            else:
                loader.close()
            self.pixbuf = loader.get_pixbuf()
            #Save the pixbuf
            if self.pixbuf:
                self.pixbuf.savev(cache_file, "png", [], []) #Not sure what the last two options are for, thank you Gdk devs for not porting the save function as well as savev.
        
        self.image = Gtk.Image()
        
        if self.pixbuf:
            #Calculate height based on width
            orig_width = self.pixbuf.get_width()
            orig_height = self.pixbuf.get_height()
            factor = float(width)/orig_width
            height = factor * orig_height
            self.scaled_pixbuf = self.pixbuf.scale_simple(width - 2 * FRAME_WIDTH, height - 2 * FRAME_WIDTH, GdkPixbuf.InterpType.BILINEAR)
            self.image.set_from_pixbuf(self.scaled_pixbuf)
        else:
            #If no pixbuf, set height and move on
            height = 60
        
        #Make group
        super(AbstractFrame, self).__init__(parent=parent, x=x, y=y, width=width, height=height)
        
        #Add components
        self.shadow = GooCanvas.CanvasRect(parent=self, x=10, y=10, width=width, height=height, fill_color_rgba=0x0000BB)
        self.frame = GooCanvas.CanvasRect(parent=self, x=0, y=0, width=width-FRAME_WIDTH, height=height-FRAME_WIDTH, fill_color="white")
        self.pic = GooCanvas.CanvasWidget(parent=self, x=0, y=0, width=width-FRAME_WIDTH, height=height-FRAME_WIDTH, widget=self.image)
        
        #Add buttons
        if self.pixbuf:
            self.connect('button-press-event', self.on_clicked)
        if "file:/" not in pic_url:
            self.share_button = Gtk.Button("S")
            self.share_button.connect('clicked', self.on_share_clicked)
            GooCanvas.CanvasWidget(parent=self, x=width-60, y=height-40, width=20, height=20, widget=self.share_button)
        self.remove_button = Gtk.Button("X")
        GooCanvas.CanvasWidget(parent=self, x=width-40, y=height-40, width=20, height=20, widget=self.remove_button)
        
        self.tags = []
        
    def on_clicked(self, target, event, data=None):
        raise NotImplemented("Action function undefined")
    
    def on_share_clicked(self, widget, data=None):
        win = Gtk.Window()
        win.set_title("Share")
        win.set_size_request(300, 100)
        gwib = GwibberGtk.Entry()
        gwib.text_view.get_buffer().set_text(self.share_url)
        win.add(gwib)
        win.show_all()
        
    def set_share_url(self, url):
        self.share_url = url
    
    def add_tags(self, *tags):
        for tag in tags:
            if tag not in self.tags:
                self.tags.append(tag)
