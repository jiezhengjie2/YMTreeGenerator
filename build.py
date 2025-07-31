import PyInstaller.__main__
import os

# 确保在正确的目录中
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 运行PyInstaller
PyInstaller.__main__.run([
    'ymtree.py',
    '--name=义脉树枝图生成器',
    '--onefile',
    '--windowed',
    '--icon=icon.ico',  # 如果有图标文件的话
])