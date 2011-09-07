from PySide.QtCore import QAbstractListModel, Slot, Property, Signal, QThread

from piratebay.internet import search_main

class LoadThread(QThread):
    def __init__(self, term, pageNumber, parent=None):
        QThread.__init__(self, parent)

        self._term = term
        self._pageNumber = pageNumber
        self._torrents = None

    def run(self):
        self._torrents = None
        self._page = None
        try:
            self._page = search_main(self._term, self._pageNumber)
        except:
            print "ERROR: falha ao buscar por %s." % self._term
            return

        self._torrents = []
        for row in self._page.all():
            self._torrents.append(row)

    def data(self):
        return (self._page, self._torrents)


class SearchModel(QAbstractListModel):
    #Role Name
    NAME = 1
    SEEDERS = 2
    LEECHERS = 3
    USER = 4
    SIZE = 5
    URL = 10
    TITLE = 100
    SUBTITLE = 101

    def __init__(self, term=None):
        QAbstractListModel.__init__(self)
        self._page = None
        self._term = term
        self._torrents = []
        self._isLoading = False
        self._thread = None
        self.refresh()
        self.setRoleNames({self.NAME     : 'ITEM_NAME',
                           self.SEEDERS  : 'ITEM_SEEDERS',
                           self.LEECHERS : 'ITEM_LEECHERS',
                           self.USER     : 'ITEM_USER',
                           self.SIZE     : 'ITEM_SIZE',
                           self.URL      : 'ITEM_URL',
                           self.TITLE    : 'title',
                           self.SUBTITLE : 'subtitle'})

    @Slot(str)
    def search(self, term):
        self._term = term
        self.refresh()

    @Slot(result=int)
    def numPages(self):
        if not self._page:
            return 0
        return self._page.get_number_of_pages()

    @Slot(int)
    def goToPage(self, page):
        self.refresh(page)

    def refresh(self, page=0):
        if not self._term or self._thread:
            return

        self._setLoading(True)
        self._thread = LoadThread(self._term, page, self)
        self._thread.finished.connect(self._dataLoaded)
        self._thread.start()


    def _dataLoaded(self):
        (page, results) = self._thread.data()

        if not results:
            self._setLoading(False)
            self._thread = None
            return

        self.modelAboutToBeReset.emit()

        self._page = page
        self._torrents = results

        self.modelReset.emit()

        self._setLoading(False)
        self._thread = None

    def rowCount(self, index):
        return len(self._torrents)

    def data(self, index, role):
        if index.row() > len(self._torrents):
            return ''

        t = self._torrents[index.row()]

        if role == SearchModel.NAME:
            return t.name
        elif role == SearchModel.SEEDERS:
            return t.seeders
        elif role == SearchModel.LEECHERS:
            return t.leechers
        elif role == SearchModel.USER:
            return t.user
        elif role == SearchModel.SIZE:
            return t.size_of
        elif role == SearchModel.URL:
            return t.magnet_url
        elif role == SearchModel.TITLE:
            return t.name
        elif role == SearchModel.SUBTITLE:
            return "Size %s ULead by %s SE/LE %s/%s" % (t.size_of, t.user, t.seeders, t.leechers)
        else:
            return ''

    def _setLoading(self, flag):
        self._isLoading = flag
        self._loadingChanged.emit()

    def _isLoading(self):
        return self._isLoading


    _loadingChanged = Signal()
    isLoading = Property(bool, _isLoading, notify=_loadingChanged)
