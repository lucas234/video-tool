# @Time    : 2021/4/30 13:19
# @Author  : lucas
# @File    : ui_utils.py
# @Project : pyqt
# @Software: PyCharm
from PyQt5.QtGui import QIcon, QFontMetrics, QFont, QMovie, QMoveEvent
from PyQt5.QtWidgets import QStyledItemDelegate, QStyleOptionProgressBar, \
    QApplication, QStyle, QMessageBox, QWidget, QAbstractItemView, QMainWindow, QLabel, QHBoxLayout, QDesktopWidget, \
    QPushButton, QItemDelegate, QToolTip
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSize
import os
from PyQt5.QtGui import QPalette, QColor
from ui_style import header_style, table_data_style
from utils import get_icon_dir, Constant, get_download_dir
from search_download import SearchResults, DownloadM3u8

# dark mode
WHITE = QColor(255, 255, 255)
BLACK = QColor(0, 0, 0)
RED = QColor(255, 0, 0)
PRIMARY = QColor(53, 53, 53)
SECONDARY = QColor(35, 35, 35)
TERTIARY = QColor(42, 130, 218)

# light mode
LIGHT_BLACK = QColor(0, 0, 0)
LIGHT_WHITE = QColor(255, 255, 255)
LIGHT_RED = QColor(255, 0, 0)
LIGHT_PRIMARY = QColor(245, 245, 245)
LIGHT_SECONDARY = QColor(255, 252, 255)
LIGHT_TERTIARY = QColor(42, 130, 218)


def css_rgb(color, a=False):
    """Get a CSS `rgb` or `rgba` string from a `QtGui.QColor`."""
    return ("rgba({}, {}, {}, {})" if a else "rgb({}, {}, {})").format(*color.getRgb())


class QLightPalette(QPalette):
    """Dark palette for a Qt application meant to be used with the Fusion theme."""
    def __init__(self, *__args):
        super().__init__(*__args)

        # Set all the colors based on the constants in globals
        self.setColor(QPalette.Window, LIGHT_PRIMARY)
        self.setColor(QPalette.WindowText, LIGHT_BLACK)
        self.setColor(QPalette.Base, LIGHT_SECONDARY)
        self.setColor(QPalette.AlternateBase, LIGHT_PRIMARY)
        self.setColor(QPalette.ToolTipBase, LIGHT_BLACK)
        self.setColor(QPalette.ToolTipText, LIGHT_BLACK)
        self.setColor(QPalette.Text, LIGHT_BLACK)
        self.setColor(QPalette.Button, LIGHT_PRIMARY)
        self.setColor(QPalette.ButtonText, LIGHT_BLACK)
        self.setColor(QPalette.BrightText, LIGHT_RED)
        self.setColor(QPalette.Link, LIGHT_TERTIARY)
        self.setColor(QPalette.Highlight, LIGHT_TERTIARY)
        self.setColor(QPalette.HighlightedText, LIGHT_BLACK)

    @staticmethod
    def set_stylesheet(app):
        """Static method to set the tooltip stylesheet to a `QtWidgets.QApplication`."""
        app.setStyleSheet("QToolTip {{"
                          "color: {white};"
                          "background-color: {tertiary};"
                          "border: 1px solid {white};"
                          "}}".format(white=css_rgb(LIGHT_BLACK), tertiary=css_rgb(LIGHT_TERTIARY)))

    def set_app(self, app):
        """Set the Fusion theme and this palette to a `QtWidgets.QApplication`."""
        app.setStyle("Fusion")
        app.setPalette(self)
        self.set_stylesheet(app)


class QDarkPalette(QPalette):
    def __init__(self, *__args):
        super().__init__(*__args)

        # Set all the colors based on the constants in globals
        self.setColor(QPalette.Window, PRIMARY)
        self.setColor(QPalette.WindowText, WHITE)
        self.setColor(QPalette.Base, SECONDARY)
        self.setColor(QPalette.AlternateBase, PRIMARY)
        self.setColor(QPalette.ToolTipBase, WHITE)
        self.setColor(QPalette.ToolTipText, WHITE)
        self.setColor(QPalette.Text, WHITE)
        self.setColor(QPalette.Button, PRIMARY)
        self.setColor(QPalette.ButtonText, WHITE)
        self.setColor(QPalette.BrightText, RED)
        self.setColor(QPalette.Link, TERTIARY)
        self.setColor(QPalette.Highlight, TERTIARY)
        self.setColor(QPalette.HighlightedText, BLACK)

    @staticmethod
    def set_stylesheet(app):
        """Static method to set the tooltip stylesheet to a `QtWidgets.QApplication`."""
        app.setStyleSheet("QToolTip {{"
                          "color: {white};"
                          "background-color: {tertiary};"
                          "border: 1px solid {white};"
                          "}}".format(white=css_rgb(WHITE), tertiary=css_rgb(TERTIARY)))

    def set_app(self, app):
        """Set the Fusion theme and this palette to a `QtWidgets.QApplication`."""
        app.setStyle("Fusion")
        app.setPalette(self)
        self.set_stylesheet(app)


class LoadingMask(QMainWindow):
    signal = QtCore.pyqtSignal()

    def __init__(self, parent, gif=None, tip=None):
        self.gif = gif
        self.tip = tip
        super(LoadingMask, self).__init__(parent)
        parent.installEventFilter(self)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        if self.tip:
            self.label.setText(self.tip)
            font = QFont('Microsoft YaHei', 10, QFont.Normal)
            font_metrics = QFontMetrics(font)
            self.label.setFont(font)
            self.label.setFixedSize(font_metrics.width(self.tip, len(self.tip)) + 10, font_metrics.height() + 5)
            self.label.setAlignment(Qt.AlignCenter)
            self.label.setStyleSheet('QLabel{border-radius: 4px; color: red; padding: 5px;}')

        if self.gif:
            self.movie = QMovie(self.gif)
            self.movie.setSpeed(30)
            self.label.setMovie(self.movie)
            self.label.setFixedSize(QSize(100, 100))
            self.label.setScaledContents(True)
            self.movie.start()

        layout = QHBoxLayout()
        widget = QWidget()
        width, height = parent.width(), parent.height()
        widget.setFixedSize(width, height)
        widget.setLayout(layout)
        layout.addWidget(self.label)
        self.setCentralWidget(widget)
        self.setWindowOpacity(0.9)
        # print(widget.palette().color(QPalette.Background).name())
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip)
        self.center()
        self.hide()
        self.move(parent.pos().x() + 1, parent.pos().y() + 30)

    def eventFilter(self, widget, event):
        if widget == self.parent() and type(event) == QMoveEvent:
            self.move_with_parent()
            return True
        return super(LoadingMask, self).eventFilter(widget, event)

    def move_with_parent(self):
        if self.isVisible():
            self.move(self.parent().geometry().x(), self.parent().geometry().y())
            self.setFixedSize(QSize(self.parent().geometry().width(), self.parent().geometry().height()))

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def show_loading(self, window):
        self.show()
        window.installEventFilter(self)


class ProgressBarDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        QStyledItemDelegate.__init__(self, parent=parent)

    def paint(self, painter, option, index):
        # QStyledItemDelegate.paint(self, painter, option, index)
        progress = index.data()
        bar_option = QStyleOptionProgressBar()
        bar_option.rect = option.rect
        bar_option.rect.setHeight(option.rect.height() - 5)
        bar_option.rect.setTop(option.rect.top() + 5)
        bar_option.minimum = 0
        bar_option.maximum = 100
        bar_option.progress = progress
        bar_option.text = f"{progress}%" if progress < 100 else "完成"
        bar_option.textVisible = True
        bar_option.textAlignment = Qt.AlignCenter
        QApplication.style().drawControl(QStyle.CE_ProgressBar, bar_option, painter)


class ButtonDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super(ButtonDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        # QToolTip.setFont(QFont('Arial', 11))

        def clicked_start_pause():
            # global image
            row = index.row()
            print(self.parent().model().index(0,1).data())
            print(index.model().index(0,1).data())
            if index.data():
                # data[row][2] = 0
                from video_tools import download_task
                download_task(self.parent(),"山海情","https://v5.szjal.cn/20210112/uEqxa53j/index.m3u8", "第1集")
                print("开始任务")
                image = QIcon(get_icon_dir("pause.svg"))
                btn_start_pause.setToolTip("暂停")
            else:
                print("暂停任务")
                # data[row][2] = 1
                image = QIcon(get_icon_dir("start.svg"))
                btn_start_pause.setToolTip("开始")
            btn_start_pause.setIcon(image)
            QApplication.processEvents()
            # print(index.row())
            print(index.data())
            # print(index.model().index(index.row(),0).data())

        if index.data():
            image = QIcon(get_icon_dir("start.svg"))
        else:
            image = QIcon(get_icon_dir("pause.svg"))

        if not self.parent().indexWidget(index):
            btn_start_pause = QPushButton(self.parent())
            btn_start_pause.setIconSize(QSize(20, 20))
            btn_start_pause.setIcon(image)
            btn_start_pause.index = [index.row(), index.column()]
            btn_start_pause.clicked.connect(clicked_start_pause)
            if index.data():
                btn_start_pause.setToolTip("开始")
            else:
                btn_start_pause.setToolTip("暂停")
            style = """QPushButton{
                                background-color: none;
                                border:none;
                                padding:1px 1px;
                            }
                            QPushButton:hover{
                                padding:1px 1px;
                                border: 1px solid;
                                border-color:#49b675;
                                border-radius:4px
                            }
                            """
            btn_start_pause.setStyleSheet(style)
            btn_folder = QPushButton(self.parent())
            btn_folder.setIconSize(QSize(20, 20))
            btn_folder.setIcon(QIcon(get_icon_dir("folder.svg")))
            btn_folder.index = [index.row(), index.column()]
            btn_folder.clicked.connect(clicked_start_pause)
            btn_folder.setToolTip("打开所在文件夹")
            # 显示图片
            # btn_folder.setToolTip('<img src="../assets/close.svg">')
            btn_folder.setStyleSheet(style)

            btn_delete = QPushButton(self.parent())
            btn_delete.setIconSize(QSize(20, 20))
            btn_delete.setIcon(QIcon(get_icon_dir("close.svg")))
            btn_delete.index = [index.row(), index.column()]
            btn_delete.clicked.connect(clicked_start_pause)
            btn_delete.setToolTip("删除")
            btn_delete.setStyleSheet(style)

            btn_done = QPushButton(self.parent())
            btn_done.setIconSize(QSize(20, 20))
            btn_done.setIcon(QIcon(get_icon_dir("checkmark.svg")))
            btn_done.index = [index.row(), index.column()]
            # btn_done.clicked.connect(clicked_start_pause)
            btn_done.setToolTip("下载完成")
            btn_done.setStyleSheet(style)
            btn_done.setDisabled(True)

            h_box_layout = QHBoxLayout()
            if index.data() == 2:
                h_box_layout.addWidget(btn_done)
            else:
                h_box_layout.addWidget(btn_start_pause)

            h_box_layout.addWidget(btn_delete)
            h_box_layout.addWidget(btn_folder)
            h_box_layout.setContentsMargins(0, 0, 0, 0)
            h_box_layout.setAlignment(Qt.AlignCenter)
            widget = QWidget()
            widget.setFixedWidth(105)
            widget.setLayout(h_box_layout)
            self.parent().setIndexWidget(index, widget)


def message_box(text):
    message_box_ = QMessageBox()
    message_box_.setText(text)
    message_box_.setWindowTitle("提示")
    message_box_.setWindowIcon(QIcon(get_icon_dir("information.png")))
    message_box_.exec_()


class Table(QWidget):
    def __init__(self, instance, row, column, header_label):
        super(Table, self).__init__()
        self.row = row
        self.column = column
        self.header_label = header_label
        self.table_widget = instance
        self.init_ui()

    def init_ui(self):
        # self.table_widget=QTableWidget(self.column, self.row)
        self.table_widget.setRowCount(self.row)
        self.table_widget.setColumnCount(self.column)
        self.table_widget.setHorizontalHeaderLabels(self.header_label)
        self.table_widget.horizontalHeader().setStyleSheet(header_style)
        # 表格禁止编辑
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 表格隐藏水平，竖直头
        self.table_widget.verticalHeader().setVisible(False)
        # 设置字体样式
        self.table_widget.setStyleSheet(table_data_style)


class TableModel(QtCore.QAbstractTableModel):
    HORIZONTAL_HEAD_DATA = ('名称', '下载进度', "操作")
    VERTICAL_HEAD_DATA = (1, 2)

    def __init__(self, data, header=HORIZONTAL_HEAD_DATA):
        super(TableModel, self).__init__()
        self._data = data
        self.header = header

    def data(self, index=QtCore.QModelIndex(), role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if self._data:
                return self._data[index.row()][index.column()]
        # 对齐方式
        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

        # # 设置字体
        # if role == QtCore.Qt.FontRole:
        #     font = QtGui.QFont()
        #     font.setPixelSize(12)
        #     font.setFamily("verdana")
        #     return QtCore.QVariant(font)

        # if role == QtCore.Qt.DecorationRole:
        #     return QtGui.QPixmap("C:\\1.jpg")

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if self._data:
            return len(self._data[0])
        else:
            return 0

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.header[section])
            if orientation == Qt.Vertical:
                # len(VERTICAL_HEAD_DATA) 一定要>=rowCount
                return str(self.VERTICAL_HEAD_DATA[section])

    def flags(self, index=QtCore.QModelIndex()):
        """
        :param index:
        :return:
        """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def setData(self, index=QtCore.QModelIndex(), value=None, role=QtCore.Qt.EditRole):
        """
        :param value:
        :param role:
        :param index:
        :return:
        """
        if value:
            self.table_data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True

    def insertRow(self, row, value=None, index=QtCore.QModelIndex()):
        """
        :param row:
        :param index:
        :param value: [v1, v2, v3, v4]
        :return:
        """
        if value:
            self.beginInsertRows(index, row, row)
            self.table_data.insert(row, value)
            self.endInsertRows()

    def removeRow(self, row, index=QtCore.QModelIndex()):
        """
        :param row:
        :param index:
        :return:
        """
        self.beginRemoveRows(index, row, row)
        self.table_data.pop(row)
        self.endRemoveRows()

    def clear(self):
        for i in reversed(range(self.rowCount())):
            self.removeRow(i)


class SearchThread(QtCore.QThread):
    finished = QtCore.pyqtSignal(object)

    def __init__(self, callback, parent=None, keyword=None):
        super(SearchThread, self).__init__(parent)
        self.finished.connect(callback)
        # 传入搜索关键字
        self.keyword = keyword

    def run(self):
        result = self._search()
        self.finished.emit(result)

    def _search(self):
        # results = [{'id': '252515', 'name': '山海情配音版', 'type': '国产剧', 'date': '2021-01-24', 'm3u8_links': ['第1集$https://v5.szjal.cn/20210112/MdGf3UO3/index.m3u8', '第2集$https://v5.szjal.cn/20210112/099hKuw8/index.m3u8', '第3集$https://v5.szjal.cn/20210113/Rlw2hQ5E/index.m3u8', '第4集$https://v5.szjal.cn/20210113/cWFhRTXy/index.m3u8', '第5集$https://v5.szjal.cn/20210114/emPJepZJ/index.m3u8', '第6集$https://v5.szjal.cn/20210114/jAZXIX21/index.m3u8', '第7集$https://v5.szjal.cn/20210115/zdUPozrf/index.m3u8', '第8集$https://v5.szjal.cn/20210115/rNYRqwoD/index.m3u8', '第9集$https://v5.szjal.cn/20210116/KLgbFubn/index.m3u8', '第10集$https://v5.szjal.cn/20210117/4kSzvX6I/index.m3u8', '第11集$https://v5.szjal.cn/20210117/MK9zsorU/index.m3u8', '第12集$https://v5.szjal.cn/20210118/wKmwDSWK/index.m3u8', '第13集$https://v5.szjal.cn/20210118/gWKIE0Ye/index.m3u8', '第14集$https://v5.szjal.cn/20210119/iLKa54cV/index.m3u8', '第15集$https://v5.szjal.cn/20210119/2LMYO8jx/index.m3u8', '第16集$https://v5.szjal.cn/20210120/dCNKZvFI/index.m3u8', '第17集$https://v5.szjal.cn/20210120/kNzsG5m8/index.m3u8', '第18集$https://v5.szjal.cn/20210121/ZoUO4ZhP/index.m3u8', '第19集$https://v5.szjal.cn/20210121/wDZ3dyR9/index.m3u8', '第20集$https://v5.szjal.cn/20210122/mO1FO0kQ/index.m3u8', '第21集$https://v5.szjal.cn/20210122/OMW26Yi2/index.m3u8', '第22集$https://n1.szjal.cn/20210124/FmeO4dSG/index.m3u8', '第23集$https://n1.szjal.cn/20210124/Ml7Vk3EQ/index.m3u8']}, {'id': '252516', 'name': '山海情原声版', 'type': '国产剧', 'date': '2021-01-24', 'm3u8_links': ['第1集$https://v5.szjal.cn/20210118/1CXj2d8g/index.m3u8', '第2集$https://v5.szjal.cn/20210118/teQJ4S6d/index.m3u8', '第3集$https://v5.szjal.cn/20210118/r5OycfOl/index.m3u8', '第4集$https://v5.szjal.cn/20210118/NRWs0HcH/index.m3u8', '第5集$https://v5.szjal.cn/20210118/wisyUcnG/index.m3u8', '第6集$https://v5.szjal.cn/20210118/4m1XGxZE/index.m3u8', '第7集$https://v5.szjal.cn/20210117/l5tPEE9U/index.m3u8', '第8集$https://v5.szjal.cn/20210117/gfdWCMOL/index.m3u8', '第9集$https://v5.szjal.cn/20210117/eXRBDB4D/index.m3u8', '第10集$https://v5.szjal.cn/20210117/4V9DK2aW/index.m3u8', '第11集$https://v5.szjal.cn/20210118/VjhBIQ7T/index.m3u8', '第12集$https://v5.szjal.cn/20210118/gori44SG/index.m3u8', '第13集$https://v5.szjal.cn/20210118/PRR8fUrV/index.m3u8', '第14集$https://v5.szjal.cn/20210119/0JJypjdV/index.m3u8', '第15集$https://v5.szjal.cn/20210119/2nMQucDs/index.m3u8', '第16集$https://v5.szjal.cn/20210120/S2oWZQl9/index.m3u8', '第17集$https://v5.szjal.cn/20210120/MJi4Y4UN/index.m3u8', '第18集$https://v5.szjal.cn/20210121/BjhA8knw/index.m3u8', '第19集$https://v5.szjal.cn/20210121/ZE0l7aHB/index.m3u8', '第20集$https://v5.szjal.cn/20210122/KAWusLab/index.m3u8', '第21集$https://v5.szjal.cn/20210122/BYBjDYro/index.m3u8', '第22集$https://n1.szjal.cn/20210124/DrVCyem2/index.m3u8', '第23集$https://n1.szjal.cn/20210124/16vX5aMv/index.m3u8']}, {'id': '250862', 'name': '山海情', 'type': '国产剧', 'date': '2021-01-24', 'm3u8_links': ['第1集$https://v5.szjal.cn/20210112/uEqxa53j/index.m3u8', '第2集$https://v5.szjal.cn/20210112/ebYB5eFk/index.m3u8', '第3集$https://v5.szjal.cn/20210113/0e9SN4Nq/index.m3u8', '第4集$https://v5.szjal.cn/20210113/GiKC8E1V/index.m3u8', '第5集$https://v5.szjal.cn/20210114/FBezqHub/index.m3u8', '第6集$https://v5.szjal.cn/20210114/UR54gOYz/index.m3u8', '第7集$https://v5.szjal.cn/20210115/DsAkjR6q/index.m3u8', '第8集$https://v5.szjal.cn/20210115/q0tJsSym/index.m3u8', '第9集$https://v5.szjal.cn/20210116/wWCkj5i4/index.m3u8', '第10集$https://v5.szjal.cn/20210117/njpC2zIy/index.m3u8', '第11集$https://v5.szjal.cn/20210117/8WiGb9ND/index.m3u8', '第12集$https://v5.szjal.cn/20210118/fw1OsSUf/index.m3u8', '第13集$https://v5.szjal.cn/20210118/o3fNMO50/index.m3u8', '第14集$https://v5.szjal.cn/20210119/XnUx06IJ/index.m3u8', '第15集$https://v5.szjal.cn/20210119/6N7xZUmR/index.m3u8', '第16集$https://v5.szjal.cn/20210120/jJVMP4Bs/index.m3u8', '第17集$https://v5.szjal.cn/20210120/7sSo2WM0/index.m3u8', '第18集$https://v5.szjal.cn/20210121/WMpupwKH/index.m3u8', '第19集$https://v5.szjal.cn/20210121/dapIhu4H/index.m3u8', '第20集$https://v5.szjal.cn/20210122/yHEDRG1y/index.m3u8', '第21集$https://v5.szjal.cn/20210122/mECt32A8/index.m3u8', '第22集$https://v5.szjal.cn/20210123/3ENVw2o0/index.m3u8', '第23集$https://v5.szjal.cn/20210124/4JPe4Snh/index.m3u8']}]
        results = SearchResults(self.keyword).results
        return results


class DownloadThread(QtCore.QThread):
    process = QtCore.pyqtSignal(object)
    finished = QtCore.pyqtSignal(object)

    def __init__(self, parent=None, url=None, name=None, episode=None, download_path = None):
        super(DownloadThread, self).__init__(parent)
        # 传入搜索关键字
        self.url = url
        self.name = name
        self.episode = episode
        self.download_path = download_path

    def run(self):
        results = self._download()
        for i in results:
            self.process.emit(i)
        self.finished.emit(True)

    def _download(self):
        results = DownloadM3u8(self.name, self.download_path).concurrent_download(8, self.url, self.episode)
        return results


class PlayerThread(QtCore.QThread):
    signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, link=None, player=None):
        super(PlayerThread, self).__init__(parent)
        self.link = link
        self.player = player

    def run(self):
        # Rewrite run Time-consuming background tasks can be run here
        if self.link:
            os.system(Constant.PLAYERS[self.player] + " " + self.link)
        else:
            os.system(Constant.PLAYERS["VLC"])
        # After the task is completed, send a signal
        self.signal.emit("start a task")


def play_task(self, link=None, player="VLC"):
    # do something after task accomplished
    def slot():
        print("task accomplished...")

    self.start_thread = PlayerThread(link=link, player=player)
    # Bind the signal of task completion to the slot function processed after the task is completed
    self.start_thread.signal.connect(slot)
    self.start_thread.start()
