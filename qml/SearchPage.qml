import QtQuick 1.0
import com.nokia.meego 1.0
import com.nokia.extras 1.1

Page {
    id: torrentList
    anchors.margins: UiConstants.DefaultMargin

    tools:
        ToolBarLayout {
            ToolIcon {
                id: backIcon
                iconId: "toolbar-back"
                onClicked: {
                    pageStack.pop();
                }
                anchors.left: parent.left
            }
        }

    anchors.fill: parent
    TextField {
       id: searchText
       anchors.left: parent.left
       anchors.right: parent.right

       placeholderText: "Search term"
       platformStyle: TextFieldStyle { paddingRight: clearButton.width }
       Image {
            id: clearButton
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            source: "image://theme/icon-m-common-search"
            MouseArea {
            anchors.fill: parent
                onClicked: {
                    inputContext.reset();
                    searchModel.search(searchText.text)
                }
            }
        }
    }

    ListView {
        clip: true
        id: torrentView
        model: searchModel
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: searchText.bottom
        anchors.bottom: parent.bottom


        delegate: 
            ListDelegate {
                onClicked: {
                    torrentModel.addTorrent(model.ITEM_URL)
                    pageStack.pop();
                }
            }
    }

    BusyIndicator {
        anchors.centerIn: parent
        visible: searchModel.isLoading
        running: searchModel.isLoading
    }
}
