import transmissionrpc

from PySide.QtCore import QObject, QThread, Signal, Slot, Property

class ConnectionThread(QThread):
    def __init__(self, host, port, user, password, parent):
        QThread.__init__(self, parent)

        self._tc = None
        self.setInfo(host, port, user, password)

    def setInfo(self, host, port, user, password):
        self._host = host
        self._port = port
        self._user = user
        self._password = password

    def getInfo(self):
        return (self.host, self.port, self.user, self.password)

    def run(self):
        try:
            self._tc = transmissionrpc.Client(self._host, port=self._port, user=self._user, password=self._password)
        except:
            self._tc = None

    def stop(self):
        self.wait()
        self._tc = None

    def connection(self):
        self.wait()
        return self._tc

class UpdateThread(QThread):
    def __init__(self, server):
        QThread.__init__(self, server)

    def run(self):
        _server = self.parent()
        for t in _server._torrents:
            #try:
            if True:
                _info = _server.connection.info(t._id)[t._id]
                t.updateInfo(_info)
                self.updated.emit(t)
            else: #except:
                print "Erro atualizando informacoes do torrent: ", t._id

    updated = Signal(object)


class TorrentItem(object):
    def __init__(self, tId, tObject):
        self._id = tId
        self._obj = tObject
        self._size = None
        self._completed = None
        self._info = None

    def finished(self):
        return self._size and (self._size == self._completed)

    def size(self):
        if not self._size:
            return "unknow"
        else:
            return self._size

    def completed(self):
        if not self._completed:
            return "unknow"
        else:
            return self._completed

    def updateInfo(self, info):
        self._obj = info
        self._updateSize()
        self._updateCompleted()

    def _updateSize(self):
        _size = 0
        for k, f in self._obj.files().items():
            _size += int(f['size'])
        self._size = self._sizeAsString(_size)

    def _updateCompleted(self):
        _size = 0
        for k, f in self._obj.files().items():
            _size += int(f['completed'])
        self._completed = self._sizeAsString(_size)

    def _sizeAsString(self, size):
        if size == 0:
            return 'None'
        elif size < 1024:
            return '%.2f Bytes' % (size)
        elif size < (1024 * 1024):
            return '%.2f KiB' % (size / 1024.0)
        elif size < (1024 * 1024 * 1024):
            return '%.2f MiB' % (size / 1024.0 / 1024.0)
        else:
            return '%.2f GiB' % (size / 1024.0 / 1024.0 / 1024.0)

    def __eq__(self, other):
        return self._obj.hashString == other._obj.hashString

    def __hash__(self):
        return self._obj.hashString

    def __repr__(self):
        return "[%d] %s" % (self._id, self._obj.name)



class Server(QObject):
    def __init__(self, host, port, user=None, password=None, parent=None):
        QObject.__init__(self, parent)

        self._items = []
        self._updateTimer = -1
        self._process = ConnectionThread(host, port, user, password, self)
        self._updateProcess = UpdateThread(self)
        self._updateProcess.updated.connect(self._onItemUpdated)

        mo = self.metaObject()
        for i in range(mo.propertyCount()):
            mp = mo.property(i)
            print "NAME: %s NOTIFY: %d" % (mp.name(), mp.hasNotifySignal())

        self.clientConnected.connect(self.stateChanged)
        self.clientDisconnected.connect(self.stateChanged)

    def setInfo(self, host, port, user, password):
        (_host, _port, _user, _password) = self._process.getInfo()
        if (_host != host) or (_port != port) or (_user != user) or (_password != password):
            self.disconnect()
            self._process.setInfo(host, port, user, password)

    @Slot()
    def disconnectClient(self):
        if self._process.connection():
            self._process.stop()
            self.clientDisconnected.emit()
            if self._updateTimer != -1:
                self.killTimer(self._updateTimer)
                self._updateTimer = -1

    @Slot()
    def connectClient(self):
        if self._process.connection():
            return
        self.connecting.emit()
        self._process.finished.connect(self._onConnect)
        self._process.start()

    def itens(self):
        return self._torrents

    # virtual
    def timerEvent(self, e):
        if not self._isOnLine() or self._updateProcess.isRunning():
            return
        self._updateProcess.start()

    def _onConnect(self):
        if self._process.connection():
            self.clientConnected.emit()
            self._loadItens()
            self._updateTimer = self.startTimer(3000)
        else:
            print 'Fail to connect with server'
            self.error.emit('Fail to connect with server.')

    def _onItemUpdated(self, torrent):
        if torrent in self._torrents:
            self.torrentUpdated.emit(torrent)

    def _loadItens(self):
        if not self.isOnline:
            return

        torrents = self._connection().list()
        _torrents = []
        for k,v in torrents.items():
            t = TorrentItem(k, v)
            self.torrentAdded.emit(t)
            _torrents.append(t)

        self._torrents = _torrents

    def _isOnLine(self):
        return not self._process.isRunning() and (self._process.connection() != None)

    def _isRunning(self):
        return self._process.isRunning()

    def _connection(self):
        return self._process.connection()

    connecting = Signal()
    clientConnected = Signal()
    clientDisconnected = Signal()
    stateChanged = Signal()
    error = Signal(str)

    torrentAdded   = Signal(object)
    torrentRemoved = Signal(object)
    torrentUpdated = Signal(object)

    isRunning  = Property(bool, _isRunning, notify=stateChanged)
    isOnline   = Property(bool, _isOnLine, notify=stateChanged)
    connection = property(_connection)
