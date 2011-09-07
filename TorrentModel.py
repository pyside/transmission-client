from PySide.QtCore import QAbstractListModel, QModelIndex, Slot

class TorrentModel(QAbstractListModel):
    #Enum SHOW
    SHOW_ALL = 0
    SHOW_ACTIVE_ONLY = 1
    SHOW_DOWNLOADING_ONLY = 2
    SHOW_SEEDING_ONLY = 3
    SHOW_PAUSED_ONLY = 4
    SHOW_FINISHED_ONLY = 5

    #Role Name
    NAME = 0
    STATUS = 1
    RATIO = 2
    PRIORITY = 3
    HASH = 4
    ETA = 5
    SIZE = 6
    COMPLETED = 7
    PROGRESS = 8
    ID = 9
    TITLE = 100

    def __init__(self, server, timeout=5000):
        QAbstractListModel.__init__(self)

        self._loading = False
        self._show = TorrentModel.SHOW_ALL
        self._torrents = []
        self._visibles = []
        self.setRoleNames({self.ID       : 'TORRENT_ID',
                           self.NAME     : 'TORRENT_NAME',
                           self.STATUS   : 'TORRENT_STATUS',
                           self.RATIO    : 'TORRENT_RATIO',
                           self.PRIORITY : 'TORRENT_PRIORITY',
                           self.ETA      : 'TORRENT_ETA',
                           self.SIZE     : 'TORRENT_SIZE',
                           self.COMPLETED: 'TORRENT_COMPLETED',
                           self.PROGRESS : 'TORRENT_PROGRESS',
                           self.TITLE    : 'title'})

        self._server = server
        self._server.clientConnected.connect(self.reset)
        self._server.clientDisconnected.connect(self.reset)
        self._server.torrentAdded.connect(self._onTorrentAdded)
        self._server.torrentRemoved.connect(self._onTorrentRemoved)
        self._server.torrentUpdated.connect(self._onTorrentUpdate)

    @Slot(int)
    def showTorrents(self, flag):
        if self._show != flag:
            self._show = flag
            visibles = []
            for t in self._torrents:
                if self._torrentIsVisible(t):
                    visibles.append(t)

            self.modelAboutToBeReset.emit()
            self._visibles = visibles
            self.modelReset.emit()

    def _onTorrentAdded(self, torrent):
        self._torrents.append(torrent)

        if self._torrentIsVisible(torrent):
            parent = QModelIndex()
            index = len(self._visibles)
            self.rowsAboutToBeInserted.emit(parent, index, index)
            self._visibles.append(torrent)
            self.rowsInserted.emit(parent, index, index)

    def _onTorrentRemoved(self, torrent):
        try:
            row = self._visbiles.index(torrent)
        except ValueError:
            return

        parent = QModelIndex()
        self.rowsAboutToBeRemoved.emit(parent, row, row)
        self._visibles.remove(torrent)
        self.rowsRemoved.emit(parent, row, row)
        self._torrents.remove(torrent)

    def _onTorrentUpdate(self, torrent):
        try:
            row = self._visibles.index(torrent)
        except ValueError:
            return

        index = self.index(row, 0)
        self.dataChanged.emit(index, index)

    def _torrentIsVisible(self, t):
        if self._show == TorrentModel.SHOW_ALL:
            return True
        elif self._show == TorrentModel.SHOW_ACTIVE_ONLY:
            return (t._obj.status != 'stopped')
        elif self._show == TorrentModel.SHOW_DOWNLOADING_ONLY:
            return (t._obj.status == 'downloading')
        elif self._show == TorrentModel.SHOW_SEEDING_ONLY:
            return (t._obj.status == 'seeding')
        elif self._show == TorrentModel.SHOW_PAUSED_ONLY:
            return False
        elif self._show == TorrentModel.SHOW_FINISHED_ONLY:
            return t._obj.finished()
        else:
            return True

    def reset(self):
        self._torrents = []
        self.modelReset.emit()

    def rowCount(self, index):
        return len(self._visibles)

    def data(self, index, role):
        t = self._visibles[index.row()]

        if role == TorrentModel.ID:
            return t._id
        elif role == TorrentModel.NAME:
            return t._obj.name
        elif role == TorrentModel.STATUS:
            return t._obj.status
        elif role == TorrentModel.RATIO:
            return "%.2f" % t._obj.ratio
        elif role == TorrentModel.PRIORITY:
            return t._obj.priority
        elif role == TorrentModel.ETA:
            return t._obj.format_eta()
        elif role == TorrentModel.PROGRESS:
            return t._obj.progress
        elif role == TorrentModel.SIZE:
            return t.size()
        elif role == TorrentModel.COMPLETED:
            return t.completed()
        elif role == TorrentModel.TITLE:
            return t._obj.name
        else:
            return ''

