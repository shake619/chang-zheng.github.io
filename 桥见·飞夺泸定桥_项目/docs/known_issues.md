# 测试结果与已知问题清单

## 测试环境

- Ubuntu 22.04 / Python 3.11 / Streamlit 1.66.1（项目虚拟环境 .venv）
- 测试日期：2026-10-22

## 一、自动化测试结果（pytest，全部通过）

```
tests/test_data.py::test_data_files_exist PASSED
tests/test_data.py::test_events_sorted_and_fields PASSED
tests/test_data.py::test_sources_fields_and_status PASSED
tests/test_data.py::test_verified_sources_have_url_or_notes PASSED
tests/test_data.py::test_event_source_links_valid PASSED
tests/test_data.py::test_location_links_valid PASSED
tests/test_data.py::test_quiz_links_valid PASSED
tests/test_data.py::test_modules_importable PASSED
8 passed
```

## 二、运行期真实交互测试结果

1. **应用启动**：`streamlit run app.py`，HTTP 200，健康检查 `/​_stcore/health` 返回 ok。
2. **AppTest 端到端交互**（streamlit.testing.v1）：
   - 首页入口按钮 → 导航到时间轴：通过
   - 时间轴"查看详情" → 选中 E01 详情：通过
   - 事件详情"查看史料档案 · S04" → 跳转史料档案：通过
   - 史料详情"← 返回史料列表" → 返回列表：通过
   - 史料类型筛选（研究资料 → 5 条）：通过
   - 关键词搜索（"22勇士" → 命中）：通过
   - 问答作答记录与学习结果：通过
   - 历史空间选择"泸定桥" → 地点详情渲染：通过
   - 全程无异常（exception 列表为空）
3. **真实浏览器（Chromium）目检**：首页、时间轴、史料列表、史料详情、历史空间示意图、问答、项目说明共 7 个视图逐一截图检查，渲染正常。

## 三、开发中发现并已修复的真实问题

| 问题 | 修复 |
|------|------|
| 中文后缀日期（如 1935-05-29晨）导致事件排序错误 | 数据增加 `sort_date` + `day_order` 字段，utils 按其排序，测试同步更新 |
| Streamlit 的 `st.markdown` 会剥离 SVG 子元素，地图示意图渲染为空白 | 改用 `streamlit.components.v1.html` 本地 iframe 组件渲染（无外部依赖，离线可用） |
| 时间轴/史料列表的"查看详情"按钮与卡片分离、布局松散 | 改为双栏布局：卡片 + 同行右侧操作按钮，回调式绑定 |

## 三点五、三维展厅验证情况（2026-10-22）

- 已验证：静态资源本地服务（`/app/static/*`，需从项目目录启动）、地球仪 Canvas2D 降级版本真实渲染（拖拽/悬停交互正常）、无 WebGL 时的中文降级提示、泸定桥模型页性质声明与操作说明。
- **环境限制**：开发沙箱无 GPU 且无 X server，Chromium 无法创建 WebGL 上下文，因此 three.js 三维画面未能在开发环境完成视觉验收；需在支持 WebGL 的浏览器上查看。若浏览器不支持 WebGL，地球仪自动切换 2D 版本，泸定桥模型显示中文提示。
- three.js r160（ES Module）已本地化，离线可用；路线节点坐标仅为相对位置示意。

## 四、已知问题与限制（未解决，如实披露）

1. **数据内容限制**：S08（泸定桥桥体沿革）、S09（杨成武《忆长征》版次）为待核验状态，相关历史细节未在正文展开。
2. **无历史照片**：未获得合法授权的历史影像，视觉表现依赖自绘示意图。
3. **浏览器自动化测试的局限**：Streamlit 下拉框（自定义 listbox）在自动化操作中偶发无法展开，已改用 AppTest 验证该功能正常；人工操作不受影响。
4. **外部链接需联网**：史料"查看原始来源"需联网打开；其余功能断网可用。
5. **22 勇士完整名单**：历史原因不可考，作品不虚构补全。
6. 页面无障碍（accessibility）仅做了基础的对比度与语义优化，未做读屏软件完整适配。

## 三维加载失败修复（v2 内联方案）
- 原因：此前三维资源经 st.iframe + `/app/static/` 静态目录加载，依赖 Streamlit 版本、`enableStaticServing` 配置与启动时工作目录，任一不满足即白屏。
- 修复：`modules/embed3d.py` 将 three.js（r160 ESM）与场景脚本剥离 `export` 后**全部内联**进单份自包含 HTML，经 `st.components.v1.html` 注入。不再依赖静态目录，兼容各 Streamlit 版本，断网可用。
- WebGL 不可用时自动降级为 Canvas 2D 二维示意地球仪（功能相同）。
- 验证：8 项 pytest、AppTest 端到端交互测试、浏览器逐页截图检查均通过。
