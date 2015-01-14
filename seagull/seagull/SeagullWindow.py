# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2012 Adam Gignac <gignac.adam@gmail.com>
# Copyright (c) The Regents of the University of California.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the University nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# OR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
### END LICENSE

import locale
from locale import gettext as _
locale.textdomain('seagull')

from gi.repository import Gtk, Gdk, GdkPixbuf, GooCanvas # pylint: disable=E0611
import logging
logger = logging.getLogger('seagull')
logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')
import random
import os
import cPickle as pickle
from quickly import prompts

from seagull_lib import Window, helpers
from seagull.AboutSeagullDialog import AboutSeagullDialog
from seagull.WebFrame import YoutubeFrame, ImageFrame, VimeoFrame
from seagull.PickleStore import PickleStore

# See seagull_lib.Window.py for more details about how this class works

class SeagullWindow(Window):
    __gtype_name__ = "SeagullWindow"
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(SeagullWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutSeagullDialog

        # Code for other initialization actions should be added here.
        cache_dir = os.path.expanduser("~/.config/seagull")
    
        if not os.path.exists(cache_dir):
            logger.info("Created cache directory %s" % cache_dir)
            os.mkdir(cache_dir)
        
        flags = Gtk.TargetFlags.OTHER_APP
        
        self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY|Gdk.DragAction.MOVE)
        self.drag_dest_add_text_targets()
        self.drag_dest_add_uri_targets()
        self.connect('drag_data_received', self.receive_data)
        
        #DEFINE CONSTANTS
        self.NUM_COLUMNS = 4
        self.WINDOW_WIDTH = self.get_size_request()[0]
        self.WINDOW_HEIGHT = self.get_size_request()[1]
        self.ITEM_PADDING = 10
        
        bg_f = helpers.get_media_file("background.png")
        bg_pixbuf = GdkPixbuf.Pixbuf.new_from_file(bg_f)
        self.canvas = GooCanvas.Canvas()
        self.ui.scrolledwindow.add(self.canvas)
        self.root = self.canvas.get_root_item()
        self.ui.scrolledwindow.get_vscrollbar().connect('value-changed', self.on_scroll_event)
        
        self.bg = GooCanvas.CanvasImage(parent=self.root, x=0, y=0, pixbuf=bg_pixbuf, width=self.WINDOW_WIDTH, height=self.WINDOW_HEIGHT)
        self.canvas.set_bounds(0, 0, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        
        self.column_bottoms = [self.ITEM_PADDING] * self.NUM_COLUMNS
        self.column_width = self.WINDOW_WIDTH/self.NUM_COLUMNS
        
        self.LIST_FILE = os.path.expanduser("~/Ubuntu One/.seagull")
        self.links = PickleStore(str)
        self._iters = {}
        if os.path.exists(self.LIST_FILE):
            f = open(self.LIST_FILE, 'r')
            items = pickle.load(f)
            print items
            for item in items:
                self.add_item(item[0])
            f.close()
        logger.info("%d items loaded" % len(self.links))
        
        self.connect('destroy', self.on_destroy)
        self.show_all()
        
    def shortest_column(self):
        """Returns the index of the shortest column, starting from left"""
        return self.column_bottoms.index(min(self.column_bottoms))
    
    def add_item(self, url):
        """Detect type of frame appropriate for url and add to display"""
        if url in self._iters.keys():
            print "Already saved: " + url
        else:
            self._iters[url] = self.links.append([url])
        col = self.shortest_column()
        height = self.column_bottoms[col]
        if helpers.isYoutube(url):
            #add new youtube frame
            _ = YoutubeFrame(parent=self.root, x=col * self.column_width + self.ITEM_PADDING, y=height, url=url, width=self.column_width - self.ITEM_PADDING)
            _.add_tags('youtube')
        elif helpers.isVimeo(url):
            _ = VimeoFrame(parent=self.root, x=col * self.column_width + self.ITEM_PADDING, y=height, url=url, width=self.column_width - self.ITEM_PADDING)
            _.add_tags('vimeo')
        elif helpers.isPicture(url):
            #add new image frame
            _ = ImageFrame(parent=self.root, x=col*self.column_width + self.ITEM_PADDING, y=height, url=url, width=self.column_width - self.ITEM_PADDING)
        else:
            print("Invalid url: %s" % url)
            self.links.remove(url)
            _ = None
        if _:
            self.column_bottoms[col] += _.get_property('height') + self.ITEM_PADDING
            _.remove_button.connect('clicked', self.remove_item, _)
            _.add_tags(url.split("/")[2]) #URL base
        self.canvas.set_bounds(0, 0, self.WINDOW_WIDTH, max(self.WINDOW_HEIGHT, max(self.column_bottoms)))
        self.canvas.scroll_to(0, height)
    
    def remove_item(self, widget, item):
        #TODO: Remove from PickleStore
        print self._iters[item.share_url]
        self.links.remove(self._iters[item.share_url])
        self._iters.pop(item.share_url)
        item.remove()
    
    def receive_data(self, wid, context, x, y, data, info, time):
        """Receive drag-and-drop data"""
        url = data.get_text()
        print url
        url = url.splitlines()[0].replace("\x00", "") #Clean up
        self.add_item(url)
        context.finish(True, False, time)
    
    def on_destroy(self, *args):
        #Save file list
        with open(self.LIST_FILE, 'w') as f:
            pickle.dump(self.links, f)
        Gtk.main_quit()
    
    def on_mnu_add_activate(self, widget, data=None):
        response, url = prompts.string("Add item", "Enter URL:")
        if response == -5:
            self.add_item(url)
    
    def on_scroll_event(self, widget, data=None):
        #Used to keep the background stationary
        if isinstance(widget, Gtk.Scrollbar):
            self.bg.set_property('y', int(widget.get_value()))
    
    def on_filterBox_activate(self, widget, data=None):
        #Called when user types in filter box
        filter = self.links.filter_new()
        filter.set_visible_func(lambda m, i, d: d in i[0], data=widget.get_text())
        for row in filter:
            print row[:]
