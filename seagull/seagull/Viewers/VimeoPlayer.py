#!/usr/bin/env python
from gi.repository import Gtk, WebKit

class VimeoPlayer(Gtk.Window):
    def __init__(self, vid_id, title):
        super(VimeoPlayer, self).__init__()
        self.set_default_size(640, 480)
        self.set_title(title)
        
        web = WebKit.WebView()
        web.get_settings().set_property("enable-plugins", False)
        
        self.add(web)
        web.load_uri("http://player.vimeo.com/video/%s" % vid_id)
        
        self.show_all()


if __name__ == "__main__":
    VID_ID = "7090969"
    TITLE = "Duelity"
    
    w = VimeoPlayer(VID_ID, TITLE)
    w.connect('destroy', lambda w:Gtk.main_quit())
    Gtk.main()
