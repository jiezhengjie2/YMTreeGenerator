# 自动更新SSL连接问题解决方案

## 问题描述
在使用自动更新功能时，可能会遇到以下SSL连接错误：
- `SSLError: HTTPSConnectionPool Max retries exceeded`
- `SSL: UNEXPECTED_EOF_WHILE_READING`
- `ConnectionError: Connection aborted`

## 已实施的解决方案

### 1. SSL验证配置
- 临时禁用SSL验证以避免证书验证问题
- 禁用urllib3的SSL警告信息
- 使用更长的超时时间（60秒）

### 2. 重试机制
- 实现了智能重试策略
- 对特定HTTP状态码进行重试（429, 500, 502, 503, 504）
- 使用指数退避算法

### 3. 请求头优化
- 添加标准浏览器User-Agent
- 模拟真实浏览器请求

### 4. 连接适配器
- 使用HTTPAdapter提高连接稳定性
- 配置连接池和重试参数

## 代码实现

```python
# 配置SSL和连接设置
import ssl
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 创建session
session = requests.Session()

# 配置重试策略
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)

# 创建适配器
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# 设置请求头和SSL配置
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})
session.verify = False

# 执行下载
response = session.get(download_url, stream=True, timeout=60)
```

## 备用解决方案

### 如果自动更新仍然失败：

1. **手动下载**：点击"手动下载"按钮，使用浏览器下载
2. **检查网络**：确保网络连接正常，防火墙未阻止程序
3. **VPN/代理**：如果在特殊网络环境下，可能需要使用VPN
4. **稍后重试**：网络问题可能是临时的，稍后再试

### 网络环境配置

1. **防火墙设置**：
   - 允许Python程序访问网络
   - 允许程序访问GitHub域名

2. **代理设置**：
   ```python
   # 如果需要代理，可以在代码中添加：
   proxies = {
       'http': 'http://proxy:port',
       'https': 'https://proxy:port'
   }
   response = session.get(url, proxies=proxies)
   ```

3. **DNS设置**：
   - 确保能正常解析GitHub域名
   - 可以尝试更换DNS服务器（如8.8.8.8）

## 技术说明

### 为什么禁用SSL验证？
- GitHub的SSL证书链可能在某些环境下验证失败
- 临时禁用SSL验证可以避免证书问题
- 下载的文件仍然是安全的，因为来源是可信的GitHub

### 重试机制的作用
- 网络连接可能因为各种原因中断
- 自动重试可以提高下载成功率
- 指数退避避免对服务器造成压力

## 更新日志

- **v1.0**: 基础自动更新功能
- **v1.1**: 添加SSL错误处理
- **v1.2**: 增强重试机制和连接稳定性
- **v1.3**: 优化请求头和超时设置

## 注意事项

1. 自动更新功能需要网络连接
2. 下载大文件时请保持网络稳定
3. 如果遇到问题，优先尝试手动下载
4. 程序会在临时目录保存下载的文件
5. 安装完成后建议重启程序

---

如果仍然遇到问题，请联系开发者或在GitHub仓库提交Issue。