# coding=utf-8
# @Time    : 2021/3/26 10:43
# @Author  : lucas
# @File    : video_tools2.0.py
# @Project : pyqt
# @Software: PyCharm
from PyQt5.QtWidgets import QVBoxLayout, QAction, QTableView, QTabWidget, \
    QFormLayout, QComboBox, QCheckBox, QDialog, QDialogButtonBox, QSpinBox, \
    QStyleFactory, QLineEdit, QPushButton, QTableWidget, QMenu, QFileDialog, \
    QTableWidgetItem, QHeaderView
from PyQt5.QtCore import QDir, QUrl, QTimer, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QBrush, QColor
import sys
from ui_style import *
from utils import *
from ui_utils import *


init_db()
global download_list_data
download_list_data = get_download_list()
DOWNLOAD_DIR = get_download_dir()


def download_task(self, name, url, episode):
    progress = get_progress(url)
    if progress:
        if progress[2] == 2:
            message_box(f"{episode} 已经下载完成，不要重复下载!")
            return

    def store(value):
        global download_list_data
        origin = download_list_data.get(url, None)
        if origin:
            status = 2 if origin[2]>=origin[3] else 0
            download_list_data.update({url: [origin[0], origin[1], origin[2]+value, origin[3], status]})
        else:
            data_ = get_progress(url)
            download_list_data[url] = [data_[3], data_[4], data_[0], data_[1], data_[2]]
        print(f"更新数据 {download_list_data}")
        # store_data(url=url, downloaded=value)

    def after_download_complete():
        # status 为2表示下载完成、1表示暂停、0表示正在下载
        get_db().execute(f"update downloadList set status=2 where url='{url}'")
        download_list_data = get_download_list()
        # todo 将下载的片段合并并删除掉片段
        # merge_file()

    self.task_thread = DownloadThread(url=url, name=name, episode=episode, download_path=DOWNLOAD_DIR)
    self.task_thread.process.connect(store)
    self.task_thread.finished.connect(after_download_complete)
    self.task_thread.start()


@singleton
class DownloadList(QDialog):
    signal = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("下载列表")
        self.setFixedSize(414, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(QIcon(get_icon_dir("logo.gif")))
        self.vbox = QVBoxLayout()
        self.download_manage = QTableView()
        self.download_manage.verticalHeader().setVisible(False)
        self.download_manage.setShowGrid(False)
        self.download_manage.setSelectionMode(QAbstractItemView.NoSelection)
        self.download_manage.horizontalHeader().setVisible(False)
        self.table_header = QTableWidget(11, 2)
        self.table_header.horizontalHeader().setVisible(False)
        self.table_header.verticalHeader().setVisible(False)
        self.table_header.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.table_header.setHorizontalHeaderLabels(('名称', '下载进度'))
        self.download_manage.horizontalHeader().setStyleSheet(download_header_style)
        self.download_manage.verticalHeader().setVisible(False)
        self.download_manage.setEditTriggers(QAbstractItemView.NoEditTriggers)
        download_all = QPushButton("全部下载")
        self.vbox.addWidget(download_all)
        # self.vbox.addWidget(self.download_manage)
        self.download_list_ui()
        self.setLayout(self.vbox)
        self.signal.connect(self.realtime_refresh_ui)

    def _format_data(self, dict_data):
        all_data = {}
        for key, value in dict_data.items():
            all_data[key] = [value[0], value[1], value[2] * 100 // value[3], value[4]]
        return all_data

    def realtime_refresh_ui(self):
        if not download_list_data:
            return
        all_data = self._format_data(download_list_data)
        data_ = list(all_data.values())
        print(f"####repaint {download_list_data}")
        print(f"####repaint {data_}")
        if len(self.data) == len(data_):
            self.model._data = data_
            self.download_manage.viewport().repaint()
        else:
            self.data = data_
            self.model = TableModel(self.data, ('名称', '日期', '下载进度', "操作"))
            self.download_manage.setModel(self.model)
            # self.download_list_ui()
            # self.download_manage.show()
        QApplication.processEvents()

    def download_list_ui(self):
        all_data = self._format_data(download_list_data)
        self.data = list(all_data.values())
        if self.data:
            button_delegate = ButtonDelegate(self.download_manage)
            progress_delegate = ProgressBarDelegate(self.download_manage)
            self.download_manage.setItemDelegateForColumn(2, progress_delegate)
            self.download_manage.setItemDelegateForColumn(3, button_delegate)
            self.model = TableModel(self.data, ('名称', '日期', '下载进度', "操作"))
            self.download_manage.setModel(self.model)
            self.download_manage.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.download_manage.setColumnWidth(0, 80)
            self.download_manage.setColumnWidth(1, 70)
            self.download_manage.setColumnWidth(2, 120)
            self.download_manage.setColumnWidth(3, 110)
            self.vbox.addWidget(self.download_manage)
            # self.table_header.hide()
        else:
            # self.download_manage.hide()
            self.vbox.addWidget(self.table_header)
            no_data = QTableWidgetItem("暂无下载内容")
            no_data.setFont(QFont('verdana', 10, QFont.Black))
            no_data.setForeground(QBrush(QColor("#4d7d57")))
            no_data.setTextAlignment(Qt.AlignCenter)
            self.table_header.setItem(0, 0, no_data)
            self.table_header.setSpan(0, 0, 15, 3)
            self.table_header.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table_header.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table_header.horizontalHeader().setStyleSheet(download_header_style)

        def context_menu(pos):
            table_view = self.download_manage
            row_num = table_view.currentIndex().row()
            # column_num = table_view.currentIndex().column()
            menu = QMenu()
            download_all = menu.addAction(QIcon(get_icon_dir("download_all.png")), u'全部下载')
            download = menu.addAction(QIcon(get_icon_dir("download.png")), u'下载')
            play = menu.addAction(QIcon(get_icon_dir("play.png")), u'播放')
            delete = menu.addAction(QIcon(get_icon_dir("trash.png")), "删除")
            action = menu.exec_(table_view.mapToGlobal(pos))
            # 显示选中行的数据文本
            url = table_view.model().index(row_num, 0).data()
            episode = table_view.model().index(row_num, 1).data()

            if action == download_all:
                print('你选了{全部下载}：', url)
            if action == download:
                print('你选了{下载}：', episode, url)
                # download_task(self, url, episode)
            if action == play:
                print('你选了{播放}：', url)
                # play_task(self, link=url)
            if action == delete:
                print('你选了{删除}：', url)

        self.download_manage.setContextMenuPolicy(Qt.CustomContextMenu)
        self.download_manage.customContextMenuRequested.connect(context_menu)

@singleton
class M3U8(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("M3U8 小助手")
        self.setFixedSize(350, 350)
        # 去掉dialog右上角的 ？
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(QIcon(get_icon_dir("m3u8.png")))
        # self.setStyleSheet('background-color:grey;color:red;')
        main_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.player = QWidget()
        self.downloader = QWidget()
        self.tab_widget.addTab(self.player, "播放")
        self.tab_widget.addTab(self.downloader, "下载")
        self.tab_widget.setStyleSheet(label_style)
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
        self.player_ui()
        self.downloader_ui()
        self.play_btn.clicked.connect(self._play)
        self.downloader_btn.clicked.connect(self._download)

    def player_ui(self):
        layout = QFormLayout()
        self.player_combobox = QComboBox(parent=self)
        self.player_combobox.addItems(Constant.PLAYERS.keys())
        self.player_combobox.setMinimumHeight(24)
        self.player_combobox.setMaximumWidth(90)
        self.player_combobox.setMinimumWidth(80)
        self.player_combobox.setStyleSheet(combobox_style)
        self.play_input = QLineEdit(parent=self)
        self.play_input.setPlaceholderText("请输入M3U8链接地址")
        # just for debug
        # self.play_input.setText("http://chyd-sn.wasu.tv/tbvideo/20141108/a5715565-44de-43ff-864d-2e8c5011e361.m3u8")
        self.play_input.setStyleSheet(play_input_style)
        self.play_btn = QPushButton()
        self.play_btn.setFixedSize(40, 38)
        self.play_btn.setStyleSheet(play_btn_style)
        play_layout = QHBoxLayout()
        play_layout.addWidget(self.play_input)
        play_layout.addWidget(self.play_btn)
        layout.addRow(self.player_combobox)
        layout.addRow(play_layout)
        self.player.setLayout(layout)

    def downloader_ui(self):
        layout = QFormLayout()
        self.downloader_input = QLineEdit(parent=self)
        self.downloader_input.setPlaceholderText("请输入M3U8链接地址")
        self.downloader_input.setStyleSheet(play_input_style)
        self.downloader_btn = QPushButton()
        self.downloader_btn.setFixedSize(28, 28)
        self.downloader_btn.setStyleSheet(download_btn_style)
        downloader_layout = QHBoxLayout()
        downloader_layout.addWidget(self.downloader_input)
        downloader_layout.addWidget(self.downloader_btn)
        layout.addRow(downloader_layout)
        self.downloader.setLayout(layout)

    def _download(self):
        url = self.downloader_input.text()
        if is_m3u8_url(url):
            print(f"downloading the film: {url}")
            name = datetime.now().strftime("%Y%m%d%H%M%S")
            download_task(self, url, name)
            self.downloader_input.clear()
        else:
            message_box("请输入有效的M3U8链接!")

    def _play(self):
        player = self.player_combobox.currentText()
        url = self.play_input.text()
        if is_m3u8_url(url):
            if player.lower() == 'vlc':
                print("open the film with vlc")
                play_task(self, url)
            else:
                print(Constant.PLAYERS[player] + url)
                # http://chyd-sn.wasu.tv/tbvideo/20141108/a5715565-44de-43ff-864d-2e8c5011e361.m3u8
                QDesktopServices.openUrl(QUrl(url.strip()))
            self.play_input.clear()
        else:
            message_box("请输入有效的M3U8链接!")


@singleton
class Settings(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.con = get_db()
        self.settings = self.con.query("select modes, path, concurrencyNum, themeStyle from setting")
        self.setWindowTitle("偏好设置")
        self.setFixedSize(400, 400)
        self.setWindowIcon(QIcon(get_icon_dir("settings.png")))
        # 去掉dialog右上角的 ？
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.btn_open = QPushButton("")
        self.label = QLabel("下载路径: ")
        self.path_input = QLineEdit(self.settings[0][1], self)
        main_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.setting = QWidget()
        self.tab_widget.addTab(self.setting, "设置")
        self.tab_widget.setStyleSheet(label_style)
        main_layout.addWidget(self.tab_widget)
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._save)
        button_box.rejected.connect(self._cancel)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)
        self.setting_ui()
        self.btn_open.clicked.connect(self._select_path)

    def closeEvent(self, QCloseEvent):  # real signature unknown; restored from __doc__
        """ closeEvent(self, QCloseEvent) """
        self._cancel()

    def _select_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose Directory", "C:\\", QFileDialog.ShowDirsOnly)
        if folder:
            print(QDir.rootPath())
            print(QDir.homePath())
            folder = QDir.toNativeSeparators(folder)
        if os.path.isdir(folder):
            self.path_input.setText(folder)

    def _save(self):
        print("click the save button")
        # QLightPalette().set_app(video_tools)
        value = 1 if self.checkbox.isChecked() else 0
        update_setting = f"update setting set modes={value}, path='{self.path_input.text()}', " \
                         f"concurrencyNum={self.spin_box.text()}, themeStyle='{self.style_combobox.currentText()}' " \
                         f"where id=1"
        self.con.execute(update_setting)
        self.close()

    def _cancel(self):
        print("click the cancel button")
        modes, path, concurrency_num, theme_style = self.settings[0]
        if not modes:
            QLightPalette().set_app(video_tools)
            self.checkbox.setChecked(False)
        self.path_input.setText(path)
        self.spin_box.setValue(concurrency_num)
        self._change_style(theme_style)
        self.style_combobox.setCurrentText(theme_style)
        self.close()

    @staticmethod
    def _change_style(style_name):
        # 改变Style
        video_tools.setStyle(QStyleFactory.create(style_name))

    @staticmethod
    def _change_mode(state):
        # app = QApplication.instance()
        if state == Qt.Checked:
            QDarkPalette().set_app(video_tools)
        else:
            QLightPalette().set_app(video_tools)

    def setting_ui(self):
        form_layout = QFormLayout()
        self.path_input.setReadOnly(True)
        self.path_input.setStyleSheet(setting_input_style)
        self.btn_open.setFixedSize(30, 30)
        self.btn_open.setStyleSheet(btn_open_style)
        h_box_layout = QHBoxLayout()
        h_box_layout.addWidget(self.label)
        h_box_layout.addWidget(self.path_input)
        h_box_layout.addWidget(self.btn_open)
        self.spin_box = QSpinBox()
        self.spin_box.setValue(self.settings[0][2])
        self.spin_box.setStyleSheet(spin_box_style)

        self.style_combobox = QComboBox()
        # 获取本机支持的主题，并添加到QComboBox中
        self.style_combobox.addItems(QStyleFactory.keys())
        self.style_combobox.setCurrentText("Fusion")
        # 绑定槽函数，
        self.style_combobox.activated[str].connect(self._change_style)
        self.style_combobox.setStyleSheet(combobox_style)
        self.style_combobox.setMinimumHeight(22)
        self.style_combobox.setMaximumWidth(145)
        self.style_combobox.setMinimumWidth(80)

        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet(checkbox_style)
        if self.settings[0][0]:
            self.checkbox.setChecked(True)
        if self.checkbox.isChecked():
            QDarkPalette().set_app(video_tools)
        else:
            QLightPalette().set_app(video_tools)
        # self.checkbox.setChecked(True)
        self.checkbox.stateChanged.connect(self._change_mode)

        form_layout.addRow(h_box_layout)
        form_layout.addRow("并发数: ", self.spin_box)
        form_layout.addRow("主题风格: ", self.style_combobox)
        form_layout.addRow("黑暗模式: ", self.checkbox)
        self.setting.setLayout(form_layout)


class VideoToolsUi(QMainWindow):

    def __init__(self):
        super(VideoToolsUi, self).__init__()
        self._init_ui()

    # def closeEvent(self, QCloseEvent):  # real signature unknown; restored from __doc__
    #     """ closeEvent(self, QCloseEvent) """
    #     print("#main window更新数据，关闭App")
    #     print(download_list_data)
    #     for key, value in download_list_data.items():
    #         get_db().execute(f"update downloadList set downloaded='{value[2]}',status=1 where url='{key}'")
    #     print("###############更新完毕")

    def _init_ui(self):
        self.setWindowTitle("Video Tools")
        self.setFixedSize(550, 500)
        self.setWindowIcon(QIcon(get_icon_dir("logo.gif")))
        self.general_layout = QVBoxLayout()
        self.result_layout = QVBoxLayout()
        self.search_layout = QHBoxLayout()
        self.central_widget = QWidget()
        self.result_table = QTableWidget()
        self.detail_table = QTableWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.general_layout)
        self._search_layout()
        self._result_layout()
        self._result_table()
        self._detail_table()
        self.general_layout.addLayout(self.search_layout)
        self.general_layout.addLayout(self.result_layout)
        self._create_menu_bar()
        self.download_list_dialog = DownloadList(self)
        self._setting = Settings(self)
        self._m3u8 = M3U8(self)

    # menu ui and action
    def _download_list(self):
        print("download list clicked")
        self.download_list_dialog.show()

    def _m3u8(self):
        print("m3u8 clicked")
        self._m3u8.show()

    def _downloader(self):
        print("downloader clicked")
        self._m3u8.show()
        self._m3u8.tab_widget.setCurrentIndex(1)

    def _vlc(self):
        print("open the vlc player")
        play_task(self)

    @staticmethod
    def _help():
        print("click the help button")
        QDesktopServices.openUrl(QUrl("https://github.com/lucas234/video-tool"))

    def _select_file(self):
        print("click the select_file button")
        # 单选
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open a file', "C:\\", 'All Files (*.*)')
        # 多选
        # file_names, _ = QFileDialog.getOpenFileNames(self, 'Open a file', "C:\\", 'All Files (*.*)')
        if file_name:
            file_name = QDir.toNativeSeparators(file_name)
            # file_names = [QDir.toNativeSeparators(file) for file in file_names]
            print(file_name)

    def _settings(self):
        print("open the settings")
        self._setting.show()

    @staticmethod
    def _open_file():
        print("open file clicked")
        os.startfile("C:\\")

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet(menu_style)
        file_menu = QMenu("&文件(F)", self)
        tool_menu = QMenu("&工具(T)", self)
        help_menu = QMenu("&帮助(H)", self)
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(tool_menu)
        menu_bar.addMenu(help_menu)
        self.download_list = QAction(QIcon(get_icon_dir("films_list.png")), "下载列表", self)
        self.settings = QAction(QIcon(get_icon_dir("settings.png")), "设置", self)
        self.open_file = QAction(QIcon(get_icon_dir("folder-open-film.png")), "打开文件夹", self)
        self.m3u8 = QAction(QIcon(get_icon_dir("m3u8.png")), "M3U8")
        self.downloader = QAction(QIcon(get_icon_dir("downloader.png")), "下载器")
        self.version = QAction(QIcon(get_icon_dir("about.png")), "关于", self)
        self.help = QAction(QIcon(get_icon_dir("help.png")), "帮助", self)
        tool_menu.addActions([self.m3u8, self.downloader])
        self.players = tool_menu.addMenu(QIcon(get_icon_dir("disc-blue.png")), "播放器")
        self.vlc = QAction(QIcon(get_icon_dir("vlc.png")), "VLC")
        self.players.addActions([self.vlc])
        file_menu.addActions([self.settings, self.download_list, self.open_file])
        help_menu.addActions([self.help, self.version])
        self.version.triggered.connect(lambda: message_box("当前版本 1.0 "))
        self.open_file.triggered.connect(self._open_file)
        self.download_list.triggered.connect(self._download_list)
        self.m3u8.triggered.connect(self._m3u8)
        self.downloader.triggered.connect(self._downloader)
        self.vlc.triggered.connect(self._vlc)
        self.settings.triggered.connect(self._settings)
        self.help.triggered.connect(self._help)

    def _search_layout(self):
        self.search_input = QLineEdit()
        self.search_button = QPushButton("")
        self.search_input.setPlaceholderText("搜索影片名")
        self.search_input.setStyleSheet(search_input_style)
        self.search_button.setStyleSheet(search_button_style)
        self.search_input.setFixedHeight(25)
        self.search_button.setFixedHeight(25)
        self.search_button.setFixedWidth(90)
        self.search_button.setIconSize(QSize(23, 23))
        self.search_button.setIcon(QIcon(get_icon_dir("search.png")))
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_button)

    def _result_layout(self):
        self.result_label = QLabel("搜索结果: (PS: 双击查看详情)")
        self.detail_label = QLabel("播放下载: (PS: 右键查看菜单)")
        self.result_label.setStyleSheet(label_style)
        self.detail_label.setStyleSheet(label_style)
        self.detail_label.setFixedHeight(30)
        self.result_label.setFixedHeight(30)
        self.result_layout.addWidget(self.result_label)
        self.result_layout.addWidget(self.result_table)
        self.result_layout.addWidget(self.detail_label)
        self.result_layout.addWidget(self.detail_table)

    def _result_table(self):
        Table(self.result_table, 0, 4, ['#', '名称', '类别', '更新时间'])
        self.result_table.setColumnWidth(0, 50)
        self.result_table.setColumnWidth(1, 270)
        self.result_table.setColumnWidth(2, 80)
        self.result_table.setColumnWidth(3, 130)
        self.result_table.sortItems(3, Qt.DescendingOrder)

    def _detail_table(self):
        Table(self.detail_table, 0, 3, ["#", "剧集", "播放地址"])
        self.detail_table.setColumnWidth(0, 50)
        self.detail_table.setColumnWidth(1, 150)
        self.detail_table.setColumnWidth(2, 330)

        def context_menu(pos):
            table_widget = self.detail_table
            row_num = table_widget.currentRow()
            # column_num = table_widget.currentColumn()
            menu = QMenu()
            download_all = menu.addAction(QIcon(get_icon_dir("download_all.png")), u'全部下载')
            download = menu.addAction(QIcon(get_icon_dir("download.png")), u'下载')
            play = menu.addAction(QIcon(get_icon_dir("play.png")), u'播放')
            download_list = menu.addAction(QIcon(get_icon_dir("films_list.png")), "下载列表")
            # copy_link = menu.addAction(QIcon(get_icon_dir("copy.png")), u'复制链接')
            # copy_link.setShortcut(QKeySequence.Copy)
            action = menu.exec_(table_widget.mapToGlobal(pos))
            # 显示选中行的数据文本
            url = table_widget.item(row_num, 2).text()
            episode = table_widget.item(row_num, 1).text()
            result_table_row = self.result_table.currentRow()
            name = self.result_table.item(result_table_row, 1).text()

            if action == download_all:
                print('你选了{下载所有}：', url)
            if action == download:
                print('你选了{下载}：', episode, url)
                download_task(self, name, url, episode)
            if action == play:
                print('你选了{播放}：', url)
                play_task(self, link=url)
                QApplication.processEvents()
            if action == download_list:
                download_list_dialog = DownloadList(self)
                download_list_dialog.show()
                print('你选了{下载列表}：', url)

        self.detail_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.detail_table.customContextMenuRequested.connect(context_menu)


class VideoToolsCtrl(object):

    def __init__(self, view):
        self._view = view
        self.data = []
        self._connect_signals()

    def _connect_signals(self):
        def _display_search_results():
            self.table_widget = self._view.result_table
            self.table_widget.setRowCount(len(self.data))
            for i, value in enumerate(self.data):
                for j, v in enumerate([str(i), value['name'], value["type"], value["date"]]):
                    cell = QTableWidgetItem(v)
                    cell.setTextAlignment(Qt.AlignCenter)
                    self.table_widget.setItem(i, j, cell)

        def search_function():
            keyword = self._view.search_input.text()
            if not keyword:
                message_box("请输入要搜索的影片名")
            else:
                # 添加loading效果
                self.loading = LoadingMask(self._view, get_icon_dir("loading.gif"))
                self.loading.show_loading(self._view)

                def handle_result(result):
                    self.data = result
                    if not self.data:
                        self._view.search_input.clear()
                        message_box("未搜到影片, 请重新输入新的影片名")
                    _display_search_results()

                self.search_thread = SearchThread(handle_result, keyword=keyword)
                self.search_thread.finished.connect(lambda: self.loading.deleteLater())
                self.search_thread.start()

        self._view.search_button.clicked.connect(search_function)
        # press Enter key to search
        self._view.search_input.returnPressed.connect(search_function)
        self._view.result_table.doubleClicked.connect(self._display_detail_results)

    def _display_detail_results(self):
        row = self._view.result_table.currentRow()
        # column = self._view.result_table.currentColumn()
        # print(self._view.result_table.item(row, 1).text())
        self.table_widget = self._view.detail_table
        links = self.data[row]['m3u8_links'] if self.data else []
        self.table_widget.setRowCount(len(links))
        for i, value in enumerate(links):
            episode, link = value.split("$")
            for j, v in enumerate([str(i), episode, link]):
                cell = QTableWidgetItem(v)
                cell.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(i, j, cell)

    def emit_signal(self):
        # if self._view.download_list_dialog.data:
        self._view.download_list_dialog.signal.emit()


if __name__ == "__main__":
    video_tools = QApplication(sys.argv)
    ui = VideoToolsUi()
    ui.show()
    v_ctrl = VideoToolsCtrl(view=ui)
    # 实时刷新下载列表
    timer = QTimer()
    timer.timeout.connect(v_ctrl.emit_signal)
    timer.start(1000)
    sys.exit(video_tools.exec_())
