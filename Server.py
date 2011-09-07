import transmissionrpc

from PySide.QtCore import QObject, QThread, Signal, Slot, Property

class ConnectionThread(QThread):
    def __init__(self, config, parent):
        QThread.__init__(self, parent)

        self._tc = None
        self._info = config

    def updateInfo(self, host, port, user, password):
        self._info.host = host
        self._info.port = port
        self._info.user = user
        self._info.password = password
        self._info.commit()

    def getInfo(self):
        return self._info

    def run(self):
        try:
            self._tc = transmissionrpc.Client(self._info.host, port=self._info.port, user=self._info.user, password=self._info.password)
        except:
            self._tc = None

    def stop(self):
        self.wait()
        self._tc = None

    def _getConnection(self):
        self.wait()
        return self._tc

    connection = property(_getConnection)

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
    removed = Signal(object)


class TorrentItem(object):
    def __init__(self, tId, tObject):
        self._id = tId
        self._obj = tObject
        self._size = None
        self._completed = None
        self._info = None
        self._updated = True


    def finished(self):
        if self._updated:
            return self._obj.percentDone == 1.0
        else:
            return False

    def size(self):
        if not self._size:
            self._size = self._sizeAsString(self._obj.sizeWhenDone)
        return self._size

    def completed(self):
        if not self._completed:
            return "unknow"
        else:
            return self._completed

    def updateInfo(self, info):
        self._obj = info
        self._updated = True
        self._updateData()

    def _updateData(self):
        self._completed =  self._sizeAsString(self._obj.percentDone * self._obj.totalSize)

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
    def __init__(self, _config, parent=None):
        QObject.__init__(self, parent)

        self._items = []
        self._updateTimer = -1
        self._process = ConnectionThread(_config, self)
        self._updateProcess = UpdateThread(self)
        self._updateProcess.updated.connect(self._onItemUpdated)

        self.connecting.connect(self.stateChanged)
        self.error.connect(self.stateChanged)
        self.clientConnected.connect(self.stateChanged)
        self.clientDisconnected.connect(self.stateChanged)

    @Slot(str, str, str, str)
    def setInfo(self, host, port, user, password):
        _info = self._process.getInfo()
        if (_info.host != host) or (_info.port != port) or (_info.user != user) or (_info.password != password):
            self.disconnectClient()
            self._process.updateInfo(host, port, user, password)

    @Slot(result='QVariantMap')
    def getInfo(self):
        _info = self._process.getInfo()
        return {'host': _info.host,
                'port': _info.port,
                'user': _info.user,
                'password': _info.password}

    @Slot()
    def disconnectClient(self):
        if self._process.connection:
            self._process.stop()
            self.clientDisconnected.emit()
            if self._updateTimer != -1:
                self.killTimer(self._updateTimer)
                self._updateTimer = -1

    @Slot()
    def connectClient(self):
        if self._process.connection:
            return
        self._process.finished.connect(self._onConnect)
        self._process.start()
        self.connecting.emit()

    @Slot(str)
    def addTorrent(self, url):
        if not self.isOnline:
            return
        _result = self._process.connection.add_uri(url)
        for k,v in _result.items():
            _torrent = TorrentItem(k, v)
            self._torrents.append(_torrent)
            self.torrentAdded.emit(_torrent)


    def itens(self):
        return self._torrents

    # virtual
    def timerEvent(self, e):
        if not self._isOnLine() or self._updateProcess.isRunning():
            return
        self._updateProcess.start()

    def _onConnect(self):
        if self._process.connection:
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

        torrents = self._process.connection.list()
        _torrents = []
        for k,v in torrents.items():
            t = TorrentItem(k, v)
            _torrents.append(t)
            self.torrentAdded.emit(t)

        self._torrents = _torrents

    def _isOnLine(self):
        return not self._process.isRunning() and (self._process.connection != None)

    def _isRunning(self):
        return self._process.isRunning()

    def _connection(self):
        return self._process.connection

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
