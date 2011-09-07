from PySide.QtCore import QSettings

class ServerConfig(object):
    CONFIG_HOST_KEY = "server/host"
    CONFIG_PORT_KEY = "server/port"
    CONFIG_USER_KEY = "server/user"
    CONFGI_PASSWORD_KEY = "server/password"

    def __init__(self):
        self._config = QSettings()
        self._host = self._config.value(ServerConfig.CONFIG_HOST_KEY, '')
        self._port = self._config.value(ServerConfig.CONFIG_PORT_KEY, 0)
        self._user = self._config.value(ServerConfig.CONFIG_USER_KEY, '')
        self._password = self._config.value(ServerConfig.CONFGI_PASSWORD_KEY, '')

    def commit(self):
        self._config.setValue(ServerConfig.CONFIG_HOST_KEY, self._host)
        self._config.setValue(ServerConfig.CONFIG_PORT_KEY, self._port)
        self._config.setValue(ServerConfig.CONFIG_USER_KEY, self._user)
        self._config.setValue(ServerConfig.CONFGI_PASSWORD_KEY, self._password)
        self._config.sync()

    def isValid(self):
        return len(self._host) > 0

    def getHost(self):
        return self._host

    def setHost(self, host):
        self._host = host

    def getPort(self):
        return self._port

    def setPort(self, port):
        self._port = port

    def getUser(self):
        return self._user

    def setUser(self, user):
        self._user = user

    def getPassword(self):
        return self._password

    def setPassword(self, password):
        self._password = password

    host = property(getHost, setHost)
    port = property(getPort, setPort)
    user = property(getUser, setUser)
    password = property(getPassword, setPassword)

