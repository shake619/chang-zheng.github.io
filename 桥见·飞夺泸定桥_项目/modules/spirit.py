# -*- coding: utf-8 -*-
"""长征精神主题横幅（自绘 SVG 装饰插画）。

视觉素材说明：以下图形均为本项目自绘矢量示意（铁索、山脉、五角星、
旭日等意象），不使用任何来源不明的历史图片，不作为史实证据。
精神要义文字摘自党史文献中对伟大长征精神的概括，此处仅取四个短语作
展陈点缀，完整表述以正式党史文献为准。
"""

_SVG = """
<svg viewBox="0 0 1200 260" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="长征精神主题自绘插画：铁索横跨大渡河，旭日升起，五角星高照">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#a32418"/>
      <stop offset=".62" stop-color="#7a150c"/>
      <stop offset="1" stop-color="#4d0d07"/>
    </linearGradient>
    <linearGradient id="sun" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffe4a8"/>
      <stop offset="1" stop-color="#e8b45f"/>
    </linearGradient>
    <linearGradient id="chain" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#d9b36a"/>
      <stop offset=".5" stop-color="#f3d9a4"/>
      <stop offset="1" stop-color="#d9b36a"/>
    </linearGradient>
  </defs>

  <rect width="1200" height="260" fill="url(#sky)"/>

  <!-- 旭日与光芒 -->
  <circle cx="600" cy="200" r="150" fill="url(#sun)" opacity="0.16"/>
  <g stroke="#e8c88f" opacity="0.5">
    <line x1="600" y1="36" x2="600" y2="0" stroke-width="2"/>
    <line x1="470" y1="52" x2="452" y2="22" stroke-width="2"/>
    <line x1="730" y1="52" x2="748" y2="22" stroke-width="2"/>
    <line x1="380" y1="90" x2="348" y2="66" stroke-width="2"/>
    <line x1="820" y1="90" x2="852" y2="66" stroke-width="2"/>
  </g>
  <circle cx="600" cy="30" r="0" fill="none"/>

  <!-- 五角星 -->
  <g transform="translate(96,74) scale(1.5)">
    <path d="M0,-30 L7.6,-9.3 L29.4,-9.3 L11.7,3.5 L18.5,24.3 L0,12 L-18.5,24.3
             L-11.7,3.5 L-29.4,-9.3 L-7.6,-9.3 Z"
          fill="#f3d9a4" stroke="#b98a2f" stroke-width="2"/>
  </g>

  <!-- 远山剪影 -->
  <path d="M0,210 L90,150 L170,200 L260,128 L350,196 L440,150 L540,206
           L640,140 L740,200 L840,132 L940,198 L1040,148 L1130,204 L1200,162
           L1200,260 L0,260 Z" fill="#3d0904" opacity="0.85"/>
  <path d="M0,232 L120,190 L240,228 L360,182 L480,226 L600,186 L720,228
           L860,184 L980,226 L1100,188 L1200,224 L1200,260 L0,260 Z"
        fill="#2b0603" opacity="0.9"/>

  <!-- 大渡河与铁索 -->
  <path d="M0,244 Q300,224 600,240 T1200,240 L1200,260 L0,260 Z" fill="#1f2c33" opacity="0.9"/>
  <path d="M80,196 Q600,140 1120,196" fill="none" stroke="url(#chain)" stroke-width="4"/>
  <path d="M80,204 Q600,148 1120,204" fill="none" stroke="url(#chain)" stroke-width="2.4" opacity="0.6"/>
  <!-- 桥板残影 -->
  <g stroke="#b98a2f" stroke-width="2" opacity="0.55">
    <line x1="240" y1="180" x2="240" y2="192"/>
    <line x1="420" y1="167" x2="420" y2="179"/>
    <line x1="600" y1="164" x2="600" y2="176"/>
    <line x1="780" y1="167" x2="780" y2="179"/>
    <line x1="960" y1="180" x2="960" y2="192"/>
  </g>

  <!-- 主标题 -->
  <text x="600" y="86" text-anchor="middle" font-size="40" font-weight="800"
        fill="#fbe9c8" letter-spacing="14"
        font-family="'PingFang SC','Microsoft YaHei',sans-serif">伟大长征精神</text>
  <text x="600" y="126" text-anchor="middle" font-size="15"
        fill="#e8c88f" letter-spacing="6"
        font-family="'PingFang SC','Microsoft YaHei',sans-serif">坚 定 信 念 · 不 怕 牺 牲 · 独 立 自 主 · 紧 密 团 结</text>

  <!-- 右下注记 -->
  <text x="1178" y="248" text-anchor="end" font-size="11" fill="#c9a06a"
        font-family="'PingFang SC','Microsoft YaHei',sans-serif">自绘示意插画 · 精神要义完整表述见正式党史文献</text>
</svg>
"""


def render():
    """渲染长征精神横幅（自绘 SVG）。"""
    import streamlit as st
    st.markdown(f'<div class="qd-spirit">{_SVG}</div>', unsafe_allow_html=True)
