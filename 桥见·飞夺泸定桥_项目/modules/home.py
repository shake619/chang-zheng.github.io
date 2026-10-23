# -*- coding: utf-8 -*-
"""首页与主题导览。"""
import streamlit as st

from modules import spirit, utils


def render(navigate):
    utils.load_css()

    st.markdown("""
    <div class="qd-hero">
      <span class="qd-kicker">红色之旅 · 追梦铸魂</span>
      <h1>桥见 · 飞夺泸定桥</h1>
      <div class="sub">一座可交互的数字历史展览 —— 每一段历史陈述，都可以回溯到它的史料来源</div>
      <div class="desc">
        1935年5月29日，中国工农红军第一方面军长征途中，红四团22名勇士攀着13根铁链，
        冒着枪林弹雨飞夺泸定桥，为危境中的中央红军杀开一条血路。<br>
        本展览以权威党史文献与官方机构公开资料为基础，通过交互式时间轴、历史空间示意图、
        三维展厅与史料档案库，探索红色历史的数字化保护与传播。
      </div>
      <div class="meta">史料核验状态：已核验 8 条 · 待核验 2 条 · 全部来源可追溯（2026-10-22 访问核验）</div>
    </div>
    """, unsafe_allow_html=True)

    # 长征精神主题横幅（自绘 SVG 插画）
    spirit.render()

    st.markdown('<div class="qd-cards">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    entries = [
        (c1, "01", "历史事件时间轴", "按时间顺序回望飞夺泸定桥的完整经过，点击任意节点查看详情与来源。",
         "时间轴"),
        (c2, "02", "历史空间展示", "大渡河峡谷与泸定桥的自绘示意图，点击地点标记查看地理与历史信息。",
         "历史空间"),
        (c3, "03", "史料档案库", "本项目的核心特色：可筛选、可检索的史料档案，每条资料注明来源与核验状态。",
         "史料档案"),
        (c4, "04", "三维展厅", "three.js 交互地球仪呈现长征路线，泸定桥三维艺术化模型可拖拽环视。",
         "三维展厅"),
    ]
    for col, no, title, desc, page in entries:
        with col:
            st.markdown(f"""
            <a class="qd-card" href="#" onclick="return false;">
              <div class="no">ENTRY · {no}</div>
              <h3>{title}</h3><p>{desc}</p>
            </a>
            """, unsafe_allow_html=True)
            st.button(f"进入 · {title}", key=f"go_{page}",
                      use_container_width=True, on_click=navigate, args=(page,))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="qd-footer">
      《桥见·飞夺泸定桥》—— 数字历史交互展览 · 学生竞赛作品<br>
      本作品为教学与研究用途，引用内容版权归原作者所有；如有权利问题请联系作者移除。
    </div>
    """, unsafe_allow_html=True)
