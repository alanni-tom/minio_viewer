<div align="center">

# 🌊 Minio_Viewer

**一个基于 Flask & Tailwind CSS 构建的现代化对象存储管理工具**

[特性](#-核心特性) • [预览](#-截图预览) • [快速开始](#-快速开始) • [项目结构](#-项目结构)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-green?style=flat-square&logo=flask&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-3.0-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

</div>

---

## 📖 简介

**Minio_Viewer** 旨在解决官方控制台在轻量级使用场景下的繁琐问题。它采用 **极简主义设计**，提供比官方控制台更流畅的文件浏览体验。无论是多环境切换、文件预览，还是批量下载，都能在一个优雅的界面中高效完成。针对红队或开发人员调用 `Minio api key` 管理系统，可服务器部署。

---

## ✨ 核心特性

### 🔌 连接与管理
- **极速多环境切换**：基于 SQLite 本地存储，支持保存多组 MinIO/S3 配置（Endpoint, AK, SK），一键无缝切换生产/测试环境。
- **安全配置**：支持 HTTPS 连接，配置信息本地化存储。

### 🎨 现代化 UI/UX
- **响应式设计**：由 **Tailwind CSS** 驱动，适配不同尺寸屏幕。
- **双视图模式**：
    - **🖼️ 网格视图**：专为图片管理设计，支持缩略图懒加载、悬浮预览。
    - **📝 列表视图**：专为文件管理设计，展示详细信息，自动折叠图标保持整洁。
- **沉浸式体验**：左侧固定导航栏 + 面包屑路径导航。

### 🚀 高效操作
- **智能预览 Lightbox**：内置灯箱组件，支持在当前页面直接查看高清原图，无需下载。
- **批量打包下载**：后端流式处理，一键将当前目录所有文件打包为 **ZIP** 下载（不占用服务器磁盘空间）。
- **文件管理**：支持新建文件夹（虚拟目录）、拖拽上传、单文件下载。

---

## 📸 截图预览

<div align="center">

| 连接管理 | 网格预览 | 列表详情 |
| :---: | :---: | :---: |
| <img width="1609" height="842" alt="image" src="https://github.com/user-attachments/assets/54d75ff1-8e14-446d-8f63-d0c87fc80fb6" /> | <img width="1420" height="822" alt="image" src="https://github.com/user-attachments/assets/e8d1f8b1-2591-418e-a537-f34bcd12b86a" />| <img width="1417" height="824" alt="image" src="https://github.com/user-attachments/assets/84d73af2-128f-4a74-a026-730c9b0f1e8c" /> |

</div>

---

## 🚀 快速开始

### 1. 环境准备
确保你的环境中已安装 `Python 3.8+` 以及 `pip`。

### 2. 安装与运行

```bash
# 1. 克隆仓库
git clone https://github.com/alanni-tom/minio_viewer.git
cd minio_viewer

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动应用
python3 app.py
