#!/usr/bin/env python
from gi.repository import Gtk, WebKit

class YoutubePlayer(Gtk.Window):
    def __init__(self, vid_id, title):
        super(YoutubePlayer, self).__init__()
        self.set_default_size(640, 480)
        self.set_title(title)
        
        web = WebKit.WebView()
        
        USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3"
        
        web.get_settings().set_property("user-agent", USER_AGENT)
        
        self.add(web)
        web.load_uri("http://www.youtube.com/watch_popup?v=%s" % vid_id)
        
        self.show_all()
