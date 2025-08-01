#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建YMTree发布版本的脚本
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_release():
    """构建发布版本"""
    print("开始构建YMTree发布版本...")
    
    # 当前目录
    current_dir = Path.cwd()
    
    # 清理之前的构建文件
    build_dir = current_dir / "build"
    dist_dir = current_dir / "dist"
    spec_file = current_dir / "ymtree.spec"
    
    for path in [build_dir, dist_dir, spec_file]:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"已清理: {path}")
    
    # PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包成单个文件
        "--windowed",  # 不显示控制台窗口
        "--name=YMTreeGenerator",  # 可执行文件名称
        "--icon=icon.ico" if (current_dir / "icon.ico").exists() else "",  # 图标文件（如果存在）
        "--add-data=version.json;.",  # 包含版本文件
        "--add-data=requirements.txt;.",  # 包含依赖文件
        "--hidden-import=PyQt5",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=requests",
        "--hidden-import=sqlite3",
        "--collect-all=PyQt5",
        "ymtree.py"
    ]
    
    # 移除空的图标参数
    cmd = [arg for arg in cmd if arg]
    
    try:
        print("执行PyInstaller命令...")
        print(" ".join(cmd))
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建成功！")
        
        # 检查生成的文件
        exe_file = dist_dir / "YMTreeGenerator.exe"
        if exe_file.exists():
            file_size = exe_file.stat().st_size / (1024 * 1024)  # MB
            print(f"生成的可执行文件: {exe_file}")
            print(f"文件大小: {file_size:.2f} MB")
            
            # 创建发布目录
            release_dir = current_dir / "release"
            if release_dir.exists():
                shutil.rmtree(release_dir)
            release_dir.mkdir()
            
            # 复制文件到发布目录
            shutil.copy2(exe_file, release_dir / "YMTreeGenerator.exe")
            
            # 复制说明文件
            docs = ["README.md", "使用说明.txt", "义脉树枝图案例.txt", "LICENSE"]
            for doc in docs:
                doc_path = current_dir / doc
                if doc_path.exists():
                    shutil.copy2(doc_path, release_dir / doc)
            
            print(f"发布文件已准备完成，位于: {release_dir}")
            print("\n发布包内容:")
            for item in release_dir.iterdir():
                print(f"  - {item.name}")
                
        else:
            print("错误: 未找到生成的可执行文件")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"构建过程中出现错误: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = build_release()
    if success:
        print("\n✅ 构建完成！可以将release目录中的文件上传到GitHub Releases。")
    else:
        print("\n❌ 构建失败，请检查错误信息。")
        sys.exit(1)