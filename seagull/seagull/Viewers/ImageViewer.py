from gi.repository import Gtk

class ImageViewer(Gtk.Window):
    def __init__(self, pixbuf):
        super(ImageViewer, self).__init__()
        self.set_title("Seagull")
        height = min(pixbuf.get_height(), 700)
        width = min(pixbuf.get_width(), 1000)
        self.set_size_request(width, height)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.add(sw)
        img = Gtk.Image()
        img.set_from_pixbuf(pixbuf)
        sw.add_with_viewport(img)
        self.show_all()
