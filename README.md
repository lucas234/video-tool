
####打包
`pyinstaller --name="工具" --add-data="video_tool.db;." --add-data="dependencies;." --icon=icon.ico --noconsole  --windowed --onedir video_tools.py`

[test](docs/resources.md)

####参考
1. pyinstaller
   - https://pyinstaller.readthedocs.io/en/stable/usage.html
   - https://www.mfitzp.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/
2. something