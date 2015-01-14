from gi.repository import Gtk

def _new_picklestore(cls, columnTypes, rows):
    instance = cls.__new__(cls)
    instance.__init__(*columnTypes)
    for row in rows:
        instance.append(row)
    return instance


class PickleStore(Gtk.ListStore):
    def __reduce__(self):
        rows = [list(row) for row in self]
        coltypes = [type(c) for c in rows[0]] if len(rows)>0 else [str] #Usage-specific hack
        return _new_picklestore, (self.__class__, coltypes, rows)

if __name__ == "__main__":
    import cPickle as pickle
    ps = PickleStore(str, int)
    ps.append(["a", 1])
    ps.append(["b", 2])
    with open("temp", 'w') as f:
        pickle.dump(ps, f)
    with open("temp", 'r') as f:
        loaded = pickle.load(f)
        for row in loaded:
            print row[:]
