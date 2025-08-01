# GitHub连接问题解决方案

## 问题描述

在使用Git推送代码到GitHub时遇到以下错误：

```
fatal: unable to access 'https://github.com/jiezhengjie2/YMTreeGenerator.git/': Recv failure: Connection was reset
```

## 解决方案

以下提供多种解决方案，可以按顺序尝试，直到问题解决。

### 方案1：刷新DNS缓存

有时候连接问题是由DNS解析引起的，可以尝试刷新DNS缓存：

1. 打开命令提示符(CMD)，以管理员身份运行
2. 执行以下命令：
   ```
   ipconfig /flushdns
   ```
3. 再次尝试推送代码

### 方案2：配置SSL证书

如果出现SSL连接问题，可以尝试以下命令：

```
git config --global http.sslBackend "openssl"
git config --global http.sslCAInfo "C:\Program Files\Git\mingw64\ssl\cert.pem"
```

注意：请将路径替换为你的Git安装路径下的cert.pem文件位置。

### 方案3：配置SSH通过443端口连接

当标准的22端口被防火墙阻止时，可以通过443端口连接GitHub：

1. 在`~/.ssh/`目录下创建或编辑`config`文件（无后缀名）
2. 添加以下内容：

```
Host github.com
User git
Hostname ssh.github.com
PreferredAuthentications publickey
IdentityFile ~/.ssh/id_rsa
Port 443
```

3. 保存文件后，测试连接：

```
ssh -T git@github.com
```

如果成功，会显示：`Hi username! You've successfully authenticated, but GitHub does not provide shell access.`

4. 然后更改仓库的远程URL为SSH方式：

```
git remote set-url origin git@github.com:jiezhengjie2/YMTreeGenerator.git
```

### 方案4：配置或取消代理

#### 设置代理（如果你使用了代理软件）

```
git config --global http.proxy 127.0.0.1:端口号
git config --global https.proxy 127.0.0.1:端口号
```

将"端口号"替换为你的代理软件使用的端口（常见如：7890、10809等）

#### 取消代理（如果设置了代理但实际未使用）

```
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 方案5：添加Windows防火墙规则

1. 打开控制面板 -> Windows Defender 防火墙 -> 高级设置
2. 选择"入站规则" -> "新建规则"
3. 选择"端口" -> 输入"22"（或"443"）
4. 选择"允许连接" -> 完成向导并命名规则

## 其他建议

- 检查网络连接是否稳定
- 尝试使用不同的网络环境
- 如果使用公司或学校网络，可能需要联系网络管理员
- 考虑使用GitHub Desktop等图形界面工具作为备选方案

如果以上方法都无法解决问题，可以将代码保存到U盘或其他存储设备，在网络环境较好的地方进行推送。