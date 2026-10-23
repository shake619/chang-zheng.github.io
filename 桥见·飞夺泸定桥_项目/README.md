# 桥见 · 飞夺泸定桥

**基于史料可追溯机制的红色历史交互叙事 —— 数字历史展览**

对应"2026年第十四届全国大学生数字媒体科技作品及创意竞赛——红色之旅追梦铸魂"赛道的本地可运行数字媒体作品。

## 功能模块

| 模块 | 说明 |
|------|------|
| 首页与主题导览 | 数字博物馆风格首页，四个展览入口与版权说明 |
| 历史事件时间轴 | 9 个已核验事件按时间排序，点击查看详情并跳转关联史料 |
| 历史空间展示 | 自绘 SVG 示意图（非真实地图、无精确坐标），地点档案与事件/史料双向关联 |
| 史料档案库 | 核心特色：10 条史料可按类型筛选、按关键词搜索，每条注明来源链接、核验状态、支持的历史陈述 |
| 三维展厅 | three.js 交互地球仪（长征路线示意）+ 泸定桥三维艺术化模型；拖拽/缩放/悬停/点击；WebGL 不可用时自动降级为 2D 版 |
| 互动问答 | 6 道基于已核验史料的知识问答，答案附依据来源与时间轴跳转 |
| 项目说明 | 创作目的、技术架构、核验方法、版权与 AI 使用说明、局限性 |

## Windows 本地安装与启动

1. 安装 Python 3.9 及以上版本（安装时勾选 *Add Python to PATH*）。
2. 打开命令提示符（cmd），执行：

```bat
cd qiaojian_project
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\streamlit run app.py
```

3. 浏览器会自动打开 `http://localhost:8501`。

macOS / Linux：

```bash
cd qiaojian_project
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

## 运行测试

```bash
.venv/Scripts/python -m pytest tests/ -v      # Windows
.venv/bin/python -m pytest tests/ -v          # macOS/Linux
```

测试覆盖：JSON 数据结构、必需字段、事件-史料-地点-问答四类数据之间的关联完整性、核验状态合法性、模块可导入性。

## 断网可用性

全部页面、数据、示意图与交互均本地运行，**断网情况下核心功能完全可用**；
仅"打开原始来源"等外部链接需要联网。

## 数据与核验

- 所有历史数据位于 `data/*.json`，与界面代码分离。
- 史料核验记录：`docs/source_verification.md`（含访问日期）。
- 版权与 AI 使用说明：`docs/copyright.md`。
- 项目介绍：`docs/project_description.md`。
- 演示视频脚本：`docs/video_script.md`；答辩讲稿：`docs/defense_speech.md`；已知问题：`docs/known_issues.md`。

## 项目结构

```
qiaojian_project/
├── app.py                  # 入口：导航与会话状态
├── requirements.txt
├── data/                   # 历史数据（events / sources / locations / quiz）
├── static/                 # 三维展厅本地资源（three.js 已本地化，离线可用）
│   ├── lib/three.module.min.js   # three.js r160（MIT）
│   ├── globe/              # 交互地球仪（WebGL 版 + Canvas2D 自动降级版）
│   └── bridge/             # 泸定桥三维艺术化示意模型
├── modules/                # home, timeline, archive, map_view, quiz, about, utils
├── assets/styles/main.css  # 全局视觉样式
├── tests/test_data.py      # 数据与关联校验测试（8 项）
└── docs/                   # 核验记录、版权、说明、视频脚本、讲稿
```

## 免责与版权

本项目不使用任何来源不明的历史照片；所有图形为自绘矢量示意图。引用的新闻报道与官方公开资料仅作摘引与链接，版权归原作者所有。详见 `docs/copyright.md`。
