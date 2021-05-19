##### 安装 QtDesigner
`pip install pyqt5-tools`

###### 查看帮助
`pyqt5-tools --help`

###### 打开designer
`pyqt5-tools designer`

###### 打开已存在的`*.ui`文件
`pyqt5-tools designer test.ui`

###### 将`.ui`文件转换为`.py`文件
`pyuic5 calc.ui -o calc.py`

### 打包
`pyinstaller -F --name="工具" --add-data="video_tool.db;." --add-data="dependencies;." --i
con=icon.ico --noconsole  --windowed --onedir video_tools.py
`