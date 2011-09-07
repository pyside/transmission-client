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
                    visible: server.isOnline
                    onClicked: pageStack.push(Qt.createComponent("SearchPage.qml"));
                }

                ToolIcon {
                    id: showAllIcon
                    iconId: "toolbar-callhistory"
                    anchors.left: addIcon.right
                    visible: server.isOnline
                    onClicked: torrentModel.showTorrents(0)
                }

                ToolIcon {
                    id: showDownloadIcon
                    anchors.left: showAllIcon.right
                    iconId: "toolbar-down"
                    visible: server.isOnline
                    onClicked: torrentModel.showTorrents(2)
                }

                ToolIcon {
                    id: showSeddingIcon
                    anchors.left: showDownloadIcon.right
                    iconId: "toolbar-up"
                    visible: server.isOnline
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

    Item {
        anchors.centerIn: parent
        visible: server.isRunning
        BusyIndicator {
            id: indicator
            running: server.isRunning
        }
        Label {
            anchors.horizontalCenter: indicator.horizontalCenter
            anchors.top: indicator.bottom
            anchors.topMargin: 5
            font: UiConstants.FieldLabelFont
            text: "Connecting"
        }
    }

    Item {
        id: errorPanel
        anchors.centerIn: parent
        visible: false
        Image {
            id: errorImage
            source: "image://theme/icon-m-transfer-error"
        }
        Label {
            id: errorText
            anchors.horizontalCenter: errorImage.horizontalCenter
            anchors.top: errorImage.bottom
            anchors.topMargin: 5

            font: UiConstants.TitleFont
        }
    }

    Component.onCompleted: {
        server.error.connect(onConnectionError)
        server.connecting.connect(onServerConnecting)
        server.connectClient()
    }

    function onServerConnecting()
    {
        errorPanel.visible = false
    }

    function onConnectionError(errorMessage)
    {
        errorText.text = errorMessage
        errorPanel.visible = true
    }
}
