# Online Deployment

当前程序是 Streamlit 应用，不能直接只靠 GitHub Pages 运行。GitHub Pages 只托管 HTML、CSS、JavaScript 等静态文件；`app.py` 需要 Python 服务端持续运行。

短期上线建议：

1. 用 Streamlit Community Cloud 部署真正的转换工具。
2. 用 GitHub Pages 发布一个固定入口页。
3. 生产人员访问 GitHub Pages 入口页，再进入 Streamlit 在线工具。

## 1. 部署 Streamlit Cloud

1. 打开 Streamlit Community Cloud。
2. 选择 GitHub 仓库 `lzyscg/lyrics-transition`。
3. Branch 选择 `main`。
4. Main file path 填写：

   ```text
   app.py
   ```

5. Python 版本在 Advanced settings 中选择 Python 3.12。
6. 点击 Deploy。

依赖会从根目录的 `requirements.txt` 安装。Streamlit 官方文档要求 Python 依赖放在根目录或入口文件同目录的 `requirements.txt` 中。

建议把 Streamlit 应用命名为：

```text
lyrics-transition
```

这样入口页默认指向：

```text
https://lyrics-transition.streamlit.app/
```

如果实际生成的地址不同，修改 `docs/index.html` 中的链接即可。

## 2. 启用 GitHub Pages

本项目已经包含 GitHub Pages 自动部署 workflow：

```text
.github/workflows/deploy-pages.yml
```

如果仓库还没有开启 Pages：

1. 打开 GitHub 仓库 Settings。
2. 进入 Pages。
3. Build and deployment 的 Source 选择 GitHub Actions。
4. 运行 `Deploy GitHub Pages` workflow。

发布成功后，入口地址通常是：

```text
https://lzyscg.github.io/lyrics-transition/
```

## 3. 生产人员使用方式

给生产人员发送 GitHub Pages 入口地址即可。以后底层服务换到专有服务器时，也只需要更新 `docs/index.html` 里的工具链接，生产人员入口可以保持不变。
