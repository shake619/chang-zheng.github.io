# -*- coding: utf-8 -*-
"""《桥见·飞夺泸定桥》—— 红色历史交互叙事数字展览 · 应用入口。

运行：streamlit run app.py
页面导航为顶部横向布局；历史数据从 data/*.json 读取。
"""
import sys
from pathlib import Path

import streamlit as st

# 保证以任意工作目录启动时均可导入 modules/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from modules import archive, home, map_view, quiz, timeline, globe_view  # noqa: E402
from modules.utils import init_session, load_css  # noqa: E402

PAGES = {
    "首页": home,
    "时间轴": timeline,
    "历史空间": map_view,
    "三维展厅": globe_view,
    "史料档案": archive,
    "互动问答": quiz,
}

st.set_page_config(
    page_title="桥见 · 飞夺泸定桥",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session()
load_css()


def navigate(page: str):
    """跨页面导航：切换并清除上个页面的选中状态。"""
    st.session_state.page = page
    if page != "时间轴":
        st.session_state.selected_event = None
    if page != "史料档案":
        st.session_state.selected_source = None
    if page != "历史空间":
        st.session_state.selected_location = None
    st.rerun()


# ---------- 顶部品牌条 ----------
st.markdown("""
<div class="qd-nav">
  <div class="brand">桥见 · 飞夺泸定桥
    <small>基于史料可追溯机制的红色历史交互叙事</small>
  </div>
  <div style="font-size:.78rem;color:#e8c88f;letter-spacing:.2em;">数字历史展览</div>
</div>
""", unsafe_allow_html=True)

# ---------- 顶部横向导航 ----------
st.markdown('<div class="qd-navzone">', unsafe_allow_html=True)
cols = st.columns(len(PAGES), gap="small")
for col, (name, _) in zip(cols, PAGES.items()):
    with col:
        st.button(
            name,
            key=f"nav_{name}",
            use_container_width=True,
            type="primary" if st.session_state.page == name else "secondary",
            on_click=navigate,
            args=(name,),
        )
st.markdown("</div>", unsafe_allow_html=True)
st.markdown('<hr class="qd-navline">', unsafe_allow_html=True)

# ---------- 渲染当前页面 ----------
PAGES[st.session_state.page].render(navigate)
