from PySide.QtCore import QUrl
from PySide.QtGui import QApplication
from PySide.QtDeclarative import QDeclarativeView

from Server import Server
from TorrentModel import TorrentModel
from SearchModel import SearchModel

from Config import ServerConfig

def main():
    QApplication.setOrganizationName('OpenBossa')
    QApplication.setApplicationName('mobtrans')
    QApplication.setGraphicsSystem('raster')
    app = QApplication([])
    serverConfig = ServerConfig()
    server = Server(serverConfig)
    model = TorrentModel(server)
    searchModel = SearchModel()

    view = QDeclarativeView()
    #view.setMinimumSize(800, 600)
    view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
    view.rootContext().setContextProperty('server', server)
    view.rootContext().setContextProperty('torrentModel', model)
    view.rootContext().setContextProperty('searchModel', searchModel)
    view.setSource(QUrl.fromLocalFile('./qml/main.qml'))
    view.show()
    app.exec_()


if __name__ == '__main__':
    main()
