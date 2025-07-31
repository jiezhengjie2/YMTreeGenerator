@echo off
chcp 65001 >nul
echo ====================================
echo 义脉树枝图生成器打包工具
echo ====================================
echo.
echo 正在启动打包程序...
echo.
python build_exe.py
echo.
echo 打包完成！按任意键退出...
pause >nul