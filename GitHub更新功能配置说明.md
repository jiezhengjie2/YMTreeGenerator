# GitHub更新功能配置说明

## 问题描述

当您点击"检查更新"按钮时，如果出现以下错误提示：

> GitHub仓库不存在或无法访问，请检查version.json中的github_repo配置

这表示程序无法连接到指定的GitHub仓库来检查更新。

## 解决方法

### 方法一：通过程序界面配置

1. 点击"检查更新"按钮
2. 程序会检测到GitHub仓库配置未完成，并自动弹出配置对话框
3. 在对话框中输入您的GitHub仓库路径（格式：username/YMTreeGenerator）
4. 点击"保存配置"按钮

### 方法二：手动修改配置文件

1. 打开项目根目录下的`version.json`文件
2. 修改`github_repo`字段，将其值改为您的GitHub仓库路径
   ```json
   "github_repo": "your-username/YMTreeGenerator"
   ```
   将`your-username`替换为您的GitHub用户名
3. 同时修改`download_url`字段，确保其中的用户名与`github_repo`一致
   ```json
   "download_url": "https://github.com/your-username/YMTreeGenerator/releases/download/v{version}/义脉树枝图生成器_发布包.zip"
   ```

## 创建GitHub仓库

如果您还没有GitHub仓库，请按照以下步骤创建：

1. 访问[GitHub](https://github.com)并登录您的账户
2. 点击右上角的"+"按钮，选择"New repository"
3. 输入仓库名称（如：YMTreeGenerator）
4. 选择仓库可见性（公开或私有）
5. 点击"Create repository"按钮

## 发布版本

要使检查更新功能正常工作，您需要在GitHub仓库中发布版本：

1. 在GitHub仓库页面，点击"Releases"选项卡
2. 点击"Create a new release"按钮
3. 输入版本号（如：v1.0.0）
4. 添加版本说明
5. 上传打包好的程序文件
6. 点击"Publish release"按钮

## 注意事项

- 确保您的GitHub仓库是公开的，或者您已经登录了有权限访问该仓库的GitHub账户
- 版本号格式应为：x.y.z（如：1.0.0）
- 检查更新功能需要安装requests库，可以通过`pip install requests`命令安装