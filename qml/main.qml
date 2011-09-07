import QtQuick 1.1
import com.nokia.meego 1.0

PageStackWindow {
    platformStyle: defaultStyle;
    PageStackWindowStyle { id: defaultStyle }
    initialPage: TorrentList { }
    Component.onCompleted: {
        //theme.inverted = true
        //screen.allowedOrientations = Screen.Portrait
    }
}
