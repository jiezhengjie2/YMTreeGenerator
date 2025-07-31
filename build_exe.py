#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
义脉树枝图生成器打包脚本
使用PyInstaller将应用程序打包成可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_requirements():
    """安装打包所需的依赖"""
    print("正在安装打包依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller 安装成功")
    except subprocess.CalledProcessError:
        print("PyInstaller 安装失败，请手动安装: pip install pyinstaller")
        return False
    return True

def create_spec_file():
    """创建PyInstaller规格文件"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ymtree.py'],
    pathex=[],
    binaries=[],
    datas=[

        ('database.py', '.'),
        ('*.db', '.'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'sqlite3',
        'datetime',
        'json',
        'os',
        'sys'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='义脉树枝图生成器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('ymtree.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("已创建 ymtree.spec 文件")

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    try:
        # 清理之前的构建
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        
        # 使用spec文件构建
        subprocess.check_call(['pyinstaller', '--clean', 'ymtree.spec'])
        print("可执行文件构建成功！")
        print("可执行文件位置: dist/义脉树枝图生成器.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False

def create_installer_script():
    """创建安装包脚本"""
    installer_content = '''
; 义脉树枝图生成器安装脚本
; 使用Inno Setup编译此脚本

[Setup]
AppName=义脉树枝图生成器
AppVersion=1.0
DefaultDirName={autopf}\YMTreeGenerator
DefaultGroupName=义脉树枝图生成器
OutputDir=installer
OutputBaseFilename=YMTreeGenerator_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\义脉树枝图生成器.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "*.py"; DestDir: "{app}\source"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "*.db"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\义脉树枝图生成器"; Filename: "{app}\义脉树枝图生成器.exe"
Name: "{group}\{cm:UninstallProgram,义脉树枝图生成器}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\义脉树枝图生成器"; Filename: "{app}\义脉树枝图生成器.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\义脉树枝图生成器.exe"; Description: "{cm:LaunchProgram,义脉树枝图生成器}"; Flags: nowait postinstall skipifsilent
'''
    
    with open('installer.iss', 'w', encoding='utf-8') as f:
        f.write(installer_content)
    print("已创建 installer.iss 安装脚本")

def create_readme():
    """创建README文件"""
    readme_content = '''
# 义脉树枝图生成器

## 简介
义脉树枝图生成器是一个基于PyQt5开发的桌面应用程序，用于生成和管理义脉树枝图。

## 功能特性
- 现代化的用户界面设计
- 支持深色和浅色主题
- 图表创建和编辑
- 专题分类管理
- 数据库存储
- 图表预览和导出

## 系统要求
- Windows 7/8/10/11
- 至少 100MB 可用磁盘空间

## 安装说明
1. 下载 YMTreeGenerator_Setup.exe
2. 双击运行安装程序
3. 按照向导完成安装
4. 从开始菜单或桌面快捷方式启动程序

## 使用说明
1. 启动程序后，可以在主界面创建新的树枝图
2. 使用工具栏切换主题和调整字体大小
3. 在"我的树枝图"页面管理已创建的图表
4. 支持按专题分类和筛选图表

## 源码说明
源码文件位于安装目录的 source 文件夹中，包含：
- ymtree.py - 主程序文件

- database.py - 数据库管理文件
- 其他相关文件

## 技术支持
如有问题或建议，请联系开发者。

## 版本信息
版本: 1.0
构建日期: 2024年
'''
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("已创建 README.md 文件")

def main():
    """主函数"""
    print("=" * 50)
    print("义脉树枝图生成器打包工具")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists('ymtree.py'):
        print("错误: 未找到 ymtree.py 文件，请在项目根目录运行此脚本")
        return
    
    # 安装依赖
    if not install_requirements():
        return
    
    # 创建配置文件
    create_spec_file()
    create_installer_script()
    create_readme()
    
    # 构建可执行文件
    if build_executable():
        print("\n" + "=" * 50)
        print("打包完成！")
        print("可执行文件: dist/义脉树枝图生成器.exe")
        print("安装脚本: installer.iss (需要Inno Setup编译)")
        print("源码已保留在当前目录")
        print("=" * 50)
    else:
        print("打包失败，请检查错误信息")

if __name__ == '__main__':
    main()