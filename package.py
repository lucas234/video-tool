# @Time    : 2021/5/19 17:14
# @Author  : lucas
# @File    : package.py
# @Project : pyqt
# @Software: PyCharm
import PyInstaller.__main__


PyInstaller.__main__.run([
    'video_tools.py',
    '--name=videoTool',
    '--add-data=video_tool.db;.',
    '--add-data=dependencies;.',
    '--icon=icon.ico',
    '--noconsole',
    '--windowed',
    '--onedir',
    # '--onefile'
])
