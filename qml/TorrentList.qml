import QtQuick 1.1
import com.nokia.meego 1.0


Page {
    id: torrentList
    anchors.margins: UiConstants.DefaultMargin

    tools: 
        ToolBarLayout {
                ToolIcon {
                    id: addIcon
                    iconId: "toolbar-add"
                    anchors.left: parent.left
                    onClicked: pageStack.push(Qt.createComponent("SearchPage.qml"));
                }

                ToolIcon {
                    id: showAllIcon
                    iconId: "toolbar-callhistory"
                    anchors.left: addIcon.right
                    onClicked: torrentModel.showTorrents(0)
                }

                ToolIcon {
                    id: showDownloadIcon
                    anchors.left: showAllIcon.right
                    iconId: "toolbar-down"
                    onClicked: torrentModel.showTorrents(2)
                }

                ToolIcon {
                    id: showSeddingIcon
                    anchors.left: showDownloadIcon.right
                    iconId: "toolbar-up"
                    onClicked: torrentModel.showTorrents(3)
                }

                ToolIcon {
                    anchors.right: parent.right
                    iconId: "toolbar-settings"
                    onClicked: pageStack.push(Qt.createComponent("SettingsPage.qml"));
                }
        }

    ListView {
        id: torrentView
        model: torrentModel
        anchors.fill: parent

        delegate: TorrentDelegate { }
    }

    ScrollDecorator {
        flickableItem: torrentView
    }

    BusyIndicator {
        anchors.centerIn: parent
        visible: server.isRunning
        running: server.isRunning
    }

    Component.onCompleted: server.connectClient()
}
