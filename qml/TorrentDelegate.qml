import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.1

Item {
    height: UiConstants.ListItemHeightDefault
    width: parent.width

    function getPorcentageAsText(total, parcial, ratio)
    {
        return (parcial + " of " + total + " (Ratio " + ratio + ")")
    }

    Column {
        anchors.fill: parent
        Label {
            font: UiConstants.SmallTitleFont
            text: TORRENT_NAME
        }

        ProgressBar {
            anchors.left: parent.left
            anchors.right: parent.right
            maximumValue: 100
            value: TORRENT_PROGRESS
        }

        Label {
            font: UiConstants.SubtitleFont
            text: TORRENT_STATUS + " - " + getPorcentageAsText(TORRENT_SIZE, TORRENT_COMPLETED, TORRENT_RATIO)
        }
    }
}
