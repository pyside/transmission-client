import QtQuick 1.1
import com.nokia.meego 1.0

Page {
    anchors.margins: UiConstants.DefaultMargin
    tools:
        ToolBarLayout {
            ToolIcon {
                id: backIcon
                iconId: "toolbar-back"
                onClicked: {
                    server.setInfo(hostField.text, portField.text, userField.text, passwordField.text);
                    pageStack.pop();
                }
                anchors.left: parent.left
            }
        }

    Flickable {
        contentWidth: childrenRect.width
        contentHeight: childrenRect.height
        flickableDirection: Flickable.VerticalFlick
        anchors.fill: parent

        Column {
            spacing: UiConstants.ButtonSpacing
            SectionScrollerStyle {
                id: platformStyle
            }
            Label {
                text: "Server information"
                font: UiConstants.TitleFont
            }

            Image {
                source: platformStyle.dividerImage
                width: parent.width
                height: 1
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Label {
                text: "Host";
                font: UiConstants.FieldLabelFont
                color: UiConstants.FieldLabelColor
            }
            TextField {
                id: hostField
                width: parent.width
            }
            Label {
                 text: "Port"; 
                 font: UiConstants.FieldLabelFont
                 color: UiConstants.FieldLabelColor
            }
            TextField {
                id: portField
            }

            Item {
                height: 16
            }

            Label {
                text: "User information"
                font: UiConstants.TitleFont
            }
            Image {
                source: platformStyle.dividerImage
                width: parent.width
                height: 1
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Label {
                text: "User";
                font: UiConstants.FieldLabelFont
                color: UiConstants.FieldLabelColor
            }
            TextField {
                id: userField
            }
            Label {
                text: "Password";
                font: UiConstants.FieldLabelFont
                color: UiConstants.FieldLabelColor
            }
            TextField {
                id: passwordField
                echoMode: TextInput.Password
            }
        }
    }

    Component.onCompleted: {
        var info = server.getInfo();
        hostField.text = info['host'];
        portField.text = info['port'];
        userField.text = info['user'];
        passwordField.text = info['password'];
    }
}

