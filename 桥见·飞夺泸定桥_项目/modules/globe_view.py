# -*- coding: utf-8 -*-
"""三维展厅：three.js 交互地球仪（长征路线）+ 三维泸定桥艺术化示意模型。

技术说明：
- three.js 与场景代码**全部内联**进单个自包含 HTML（见 modules/embed3d.py），
  通过 st.components.v1.html 嵌入——不依赖静态目录服务、不依赖 st.iframe，
  兼容旧版 Streamlit，无外部请求，离线可用；
- 地球仪内置 WebGL 不可用时的 Canvas 2D 自动降级版本；
- 三维模型为程序化建模的艺术化示意，页面明确标注性质，不作史实证据。
"""
import streamlit as st
import streamlit.components.v1 as components

from modules import embed3d, utils


def render(navigate):
    utils.load_css()
    st.markdown("""
    <div class="qd-section-head"><div class="rule"></div>
      <h2>三维展厅</h2>
      <p>基于 three.js 的沉浸式三维展示：长征路线示意地球仪与泸定桥三维艺术化模型，
      均支持拖拽、缩放与悬停查看。三维资源已全部内联，断网可用。</p>
    </div>
    """, unsafe_allow_html=True)

    n1, n2 = st.tabs(["🌐 长征路线 · 交互地球仪", "⛓️ 泸定桥 · 三维模型"])

    with n1:
        st.markdown(
            '<div class="qd-map-note">🌐 地球为程序化绘制的示意性球体（非卫星影像）；'
            '长征路线仅连接关键节点作示意，不代表已核验的精确行军路线。</div>',
            unsafe_allow_html=True)
        components.html(embed3d.globe_html(), height=620, scrolling=False)
        st.caption(
            "操作：拖拽旋转 · 滚轮缩放 · 悬停节点查看名称与时间。"
            "蓝色＝起点（瑞金）/终点（吴起镇）· 金色＝途经节点 · "
            "红色＝遵义会议 · 亮金色＝泸定桥（打开时自动定位）。")

    with n2:
        st.markdown(
            '<div class="qd-map-note">⛓️ 本模型为三维艺术化复原示意（程序化建模）：'
            '仅表达「13 根铁索」这一已核验史实（见史料 S01/S02/S03）与桥梁结构意象，'
            '不呈现、不代表任何战斗细节或精确形制。</div>',
            unsafe_allow_html=True)
        components.html(embed3d.bridge_html(), height=640, scrolling=False)
        st.caption(
            "操作：左键拖拽环视 · 滚轮缩放 · 悬停高亮铁索 · 点击铁索查看说明。"
            "若浏览器不支持 WebGL，页面会给出中文提示。")

    st.markdown("""
    <div class="qd-footer">
      三维展示采用 three.js（MIT 开源协议），已内嵌于页面，离线可用；<br>
      场景中的历史表述均与「史料档案」页面的核验状态一致。
    </div>
    """, unsafe_allow_html=True)
