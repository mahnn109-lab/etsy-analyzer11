# Etsy 竞品分析器

一个基于 Streamlit 和 Playwright 的在线竞品分析工具，可以快速抓取和分析 Etsy 平台的商品数据。

## 功能特性

- 🔍 **关键词搜索**：输入任意关键词搜索 Etsy 商品
- 📊 **价格统计**：自动计算最高价、最低价、平均价
- 🖼️ **可视化展示**：网格布局展示商品图片和信息
- ☁️ **云端部署**：完全适配 Streamlit Cloud 环境
- 🛡️ **容错机制**：访问受限时自动切换到演示数据

## 部署到 Streamlit Cloud

### 1. 准备 GitHub 仓库

将以下文件上传到您的 GitHub 仓库：

```
your-repo/
├── app.py
├── requirements.txt
└── packages.txt
```

### 2. 连接 Streamlit Cloud

1. 访问 [streamlit.io/cloud](https://streamlit.io/cloud)
2. 使用 GitHub 账号登录
3. 点击 "New app"
4. 选择您的仓库和分支
5. 主文件路径设置为 `app.py`
6. 点击 "Deploy"

### 3. 等待部署完成

首次部署需要安装依赖，大约需要 3-5 分钟。部署成功后，您将获得一个公开访问的 URL。

## 本地运行

如果您想在本地测试：

```bash
# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium

# 运行应用
streamlit run app.py
```

## 技术栈

- **Frontend**: Streamlit
- **Backend**: Playwright (Python)
- **Data Processing**: Pandas
- **Deployment**: Streamlit Cloud

## 注意事项

### 云端限制

由于 Streamlit Cloud 使用共享 IP，可能会遇到以下情况：

- Etsy 可能会限制频繁访问
- 某些地区的 IP 可能被屏蔽
- 如果抓取失败，系统会自动展示演示数据

### 解决方案

如需获取真实数据，建议：

1. **本地部署**：在本地环境运行，使用您自己的 IP
2. **使用代理**：配置代理服务器（需修改代码）
3. **降低频率**：减少抓取频率，避免触发限制

## 文件说明

### `app.py`

主程序文件，包含：
- Streamlit 界面配置
- Playwright 浏览器自动化逻辑
- 数据抓取和处理函数
- 容错和模拟数据生成

### `requirements.txt`

Python 依赖包列表：
- `streamlit`: Web 应用框架
- `playwright`: 浏览器自动化工具
- `pandas`: 数据处理库

### `packages.txt`

系统级依赖（Streamlit Cloud 专用）：
- `chromium`: Chromium 浏览器
- `chromium-driver`: 浏览器驱动

## 自定义配置

### 修改抓取数量

在侧边栏中调整滑块，范围 6-24 个商品。

### 修改浏览器配置

编辑 `app.py` 中的 `scrape_etsy` 函数：

```python
browser = p.chromium.launch(
    headless=True,  # 云端必须为 True
    args=[
        '--no-sandbox',  # 云端必需
        '--disable-dev-shm-usage',  # 云端必需
        # 添加其他参数...
    ]
)
```

### 添加代理

在 `context` 创建时添加代理配置：

```python
context = browser.new_context(
    proxy={
        'server': 'http://your-proxy-server:port',
        'username': 'your-username',
        'password': 'your-password'
    }
)
```

## 常见问题

### Q: 为什么显示"演示数据"？

A: 这通常是因为：
- 云端 IP 被 Etsy 限制
- 网络连接问题
- 页面结构变化导致抓取失败

### Q: 如何获取真实数据？

A: 建议在本地环境运行，或者配置代理服务器。

### Q: 可以抓取其他网站吗？

A: 可以！修改 `scrape_etsy` 函数中的 URL 和选择器即可。

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。
