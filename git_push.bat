@echo off
echo 正在推送代码到GitHub仓库...
git push -u origin main
if %errorlevel% neq 0 (
    echo 推送失败，请检查网络连接或GitHub凭据
    echo 您可以稍后手动执行以下命令：
    echo git push -u origin main
) else (
    echo 推送成功！
)
pause