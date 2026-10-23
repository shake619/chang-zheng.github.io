# -*- coding: utf-8 -*-
"""历史空间展示：自绘 SVG 示意图 + 可点击地点信息。

地图性质声明：这是手绘矢量示意图（艺术化示意），不是真实地图，
不标注精确坐标，不呈现未经核验的行军路线或战斗部署。
"""
import streamlit as st

from modules import utils


def _svg_map(locations):
    """生成大渡河峡谷示意图（简化表达，明确标注为示意图）。"""
    marks = ""
    for loc in locations:
        x, y = loc["svg"]["x"], loc["svg"]["y"]
        is_bridge = loc["location_id"] == "L03"
        r = 11 if is_bridge else 7
        color = "#8c1c13" if is_bridge else "#b98a2f"
        marks += f"""
        <g class="loc" data-loc="{loc['location_id']}" style="cursor:pointer;">
          <circle cx="{x}" cy="{y}" r="{r + 6}" fill="{color}" opacity="0.14"/>
          <circle cx="{x}" cy="{y}" r="{r}" fill="{color}"
                  stroke="#fff" stroke-width="2"/>
          <text x="{x}" y="{y - r - 10}" text-anchor="middle"
                font-size="13" fill="#2b2723" font-weight="600">{loc['name']}</text>
        </g>"""

    return f"""
    <svg viewBox="0 0 760 470" xmlns="http://www.w3.org/2000/svg"
         style="width:100%;height:auto;background:#f3ede2;border-radius:14px;
                border:1px solid var(--qd-line);">
      <!-- 峡谷地形（艺术化示意） -->
      <path d="M0,60 Q190,120 380,90 Q570,60 760,110 L760,0 L0,0 Z"
            fill="#e5dcc9" opacity="0.7"/>
      <path d="M0,430 Q200,380 380,410 Q580,445 760,395 L760,470 L0,470 Z"
            fill="#e5dcc9" opacity="0.7"/>
      <!-- 大渡河 -->
      <path d="M0,250 C150,215 250,320 380,285 C510,250 600,300 760,255
               L760,330 C600,375 510,325 380,360 C250,395 150,290 0,325 Z"
            fill="#9db8a8" opacity="0.75"/>
      <text x="600" y="345" font-size="14" fill="#5f7263" font-style="italic">大渡河（示意河道走向）</text>
      <!-- 泸定桥：13 根铁链意象 -->
      <g>
        <line x1="470" y1="250" x2="650" y2="268" stroke="#5f120b" stroke-width="2.5"/>
        <line x1="470" y1="256" x2="650" y2="274" stroke="#5f120b" stroke-width="2.5" opacity="0.6"/>
        <line x1="470" y1="262" x2="650" y2="280" stroke="#5f120b" stroke-width="2.5" opacity="0.35"/>
      </g>
      {marks}
      <!-- 图例 -->
      <g font-size="12" fill="#7a736b">
        <circle cx="30" cy="446" r="6" fill="#8c1c13"/><text x="44" y="450">核心地点</text>
        <circle cx="140" cy="446" r="6" fill="#b98a2f"/><text x="154" y="450">关联地点</text>
        <text x="540" y="30">※ 手绘示意图 · 非真实地图 · 无精确坐标</text>
      </g>
    </svg>"""


def render(navigate):
    locations, map_note = utils.load_locations()
    events = utils.build_event_index(utils.load_events())
    sources = utils.build_source_index(utils.load_sources())

    st.markdown("""
    <div class="qd-section-head"><div class="rule"></div>
      <h2>历史空间展示</h2>
      <p>泸定桥及周边地理空间的自绘示意图。点击地点标记查看名称、地理说明、
      相关历史事件与资料来源。</p>
    </div>
    """, unsafe_allow_html=True)

    if not locations:
        st.warning("暂无地点数据（locations.json 为空或读取失败）。")
        return

    st.markdown(f'<div class="qd-map-note">🗺️ {map_note}</div>', unsafe_allow_html=True)
    # 说明：Streamlit 的 HTML 净化会剥离 st.markdown 中的 SVG 子元素，
    # 因此示意图通过 st.iframe 内嵌 HTML 渲染（本地内容，无外部依赖，离线可用）。
    st.iframe(
        f'<style>.stApp{{background:transparent;}}</style>'
        f'<style>:root{{--qd-line:#e8e1d6;--qd-muted:#7a736b;}}'
        f'body{{margin:0;}}</style>{_svg_map(locations)}',
        height=560)

    st.markdown('<div class="qd-section-head"><div class="rule"></div>'
                '<h2>地点档案</h2></div>', unsafe_allow_html=True)
    names = ["（选择地点）"] + [l["name"] for l in locations]
    preselect = None
    # 若从事件页跳来，可保留上下文（selected_location 存 id）
    loc_sel = st.session_state.get("selected_location")
    if loc_sel:
        m = next((l for l in locations if l["location_id"] == loc_sel), None)
        if m:
            preselect = m["name"]
    idx = names.index(preselect) if preselect in names else 0
    choice = st.selectbox("选择地点查看详情", names, index=idx)
    if choice == names[0]:
        return
    loc = next(l for l in locations if l["name"] == choice)

    badge = utils.source_badge(loc.get("verification_status", "待核验"))
    evs = [events[eid] for eid in (loc.get("related_events") or [])
           if eid in events]
    ev_html = "".join(
        f'<li>{e.get("display_date","")} · {e.get("title","")}</li>' for e in evs) \
        or "<li>暂无关联事件</li>"
    src_html = "".join(
        f'<span class="qd-chip">{sid}</span>' for sid in (loc.get("source_ids") or []))

    st.markdown(f"""
    <div class="qd-loc-card">
      <h3 style="margin-top:0;">📍 {loc['name']} &nbsp;{badge}</h3>
      <div class="lead">{loc.get('description','')}</div>
      <h4>相关历史事件</h4>
      <ul class="qd-claims">{ev_html}</ul>
      <h4>资料来源</h4>
      <div>{src_html}</div>
    </div>
    """, unsafe_allow_html=True)

    st.caption(f"核验说明：{loc.get('notes','无')}")
    c1, c2 = st.columns(2)
    with c1:
        if evs and st.button("在时间轴中查看相关事件"):
            st.session_state.selected_location = loc["location_id"]
            st.session_state.selected_event = evs[0]["event_id"]
            navigate("时间轴")
            return
    with c2:
        if st.button("查看关联史料（跳转史料档案）"):
            st.session_state.selected_location = loc["location_id"]
            sids = loc.get("source_ids") or []
            if sids:
                st.session_state.selected_source = sids[0]
                navigate("史料档案")
            else:
                st.warning("该地点暂无关联史料。")
            return
