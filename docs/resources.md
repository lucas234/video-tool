##### 使用`resources`文件引用图标（片）

###### 1.首先生成`resources.qrc`文件，类似如下格式：
```xml
<!DOCTYPE RCC>
   <RCC version="1.0">
       <qresource>
           <file alias='up.png'>assets/up.png</file>
           <file alias='vlc.png'>assets/vlc.png</file>
           <file alias='warning.png'>assets/warning.png</file>
       </qresource>
   </RCC>
```
###### 2.然后生成`resources.py`文件
`pyrcc5 resources.qrc -o resources.py`
###### 3.最后可以直接在文件中引用(通过`:up.png`,如果没有别名，则直接`:assets/up.png`)
```python
import resources
# 有别名
self.setWindowIcon(QIcon(":logo.ico"))
# 没有别名
self.setWindowIcon(QIcon(":assets/logo.ico"))
```
###### 4.自动生成`resources.py`文件脚本（直接输入图片的文件夹，调用函数即可）
```python
from pathlib import Path
import os

path = Path(__file__).parent.joinpath("assets")


def generate_resources_file(path_):
    path_ = Path(path_)
    resources = [f"           <file alias='{i.name}'>assets/{i.name}</file>\n" for i in path_.iterdir()]
    with open("resources.qrc", "w") as f:
        f.write("<!DOCTYPE RCC>\n")
        f.write('   <RCC version="1.0">\n')
        f.write('       <qresource>\n')
        f.writelines(resources)
        f.write('       </qresource>\n')
        f.write('   </RCC>\n')
    os.system("pyrcc5 resources.qrc -o resources.py")

generate_resources_file(path)
```