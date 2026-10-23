# -*- coding: utf-8 -*-
"""历史事件时间轴 + 事件详情。"""
import streamlit as st

from modules import spirit, utils


def render(navigate):
    events = utils.load_events()
    sources = {s["source_id"]: s for s in utils.load_sources()}

    sel = st.session_state.get("selected_event")

    if sel:
        _render_detail(sel, events, sources, navigate)
    else:
        _render_timeline(events, navigate)


def _open_event(event_id: str):
    """按钮回调：记录选中事件并刷新。"""
    st.session_state.selected_event = event_id


def _render_timeline(events, navigate):
    st.markdown("""
    <div class="qd-section-head"><div class="rule"></div>
      <h2>历史事件时间轴</h2>
      <p>点击任意事件查看详细说明与资料来源。所有事件按时间顺序排列，读取自 data/events.json。</p>
    </div>
    """, unsafe_allow_html=True)

    spirit.render()

    if not events:
        st.warning("暂无事件数据（events.json 为空或读取失败）。")
        return

    st.markdown('<div class="qd-timeline">', unsafe_allow_html=True)
    for ev in events:
        badge = utils.source_badge(ev.get("verification_status", "待核验"))
        left, right = st.columns([4, 1], gap="small")
        with left:
            st.markdown(f"""
            <div class="qd-tl-item">
              <div class="qd-tl-date">{ev.get('display_date', ev.get('date', '时间待核验'))}</div>
              <div class="qd-tl-title">{ev.get('title', '（无标题）')} &nbsp;{badge}</div>
              <div class="qd-tl-sum">{ev.get('summary', '')}</div>
            </div>
            """, unsafe_allow_html=True)
        with right:
            st.markdown('<div class="qd-tl-btn"></div>', unsafe_allow_html=True)
            st.button("查看详情", key=f"ev_{ev['event_id']}",
                      use_container_width=True,
                      on_click=_open_event, args=(ev["event_id"],))
    st.markdown("</div>", unsafe_allow_html=True)


def _render_detail(event_id, events, sources, navigate):
    # 用索引查事件，避免把整个 dict 存入 session
    ev = next((e for e in events if e["event_id"] == event_id), None)
    if ev is None:
        st.error("未找到该事件的详细数据，请返回时间轴重新选择。")
        if st.button("← 返回时间轴"):
            st.session_state.selected_event = None
            st.rerun()
        return

    badge = utils.source_badge(ev.get("verification_status", "待核验"))
    st.markdown(f"""
    <div class="qd-detail">
      <div class="qd-tl-date">{ev.get('display_date', '')}</div>
      <h2>{ev.get('title', '')} &nbsp;{badge}</h2>
      <div class="lead">{ev.get('detail', '')}</div>
    </div>
    """, unsafe_allow_html=True)

    # 核验说明
    st.markdown("**核验说明**")
    st.caption(ev.get("notes", "无"))

    # 关联史料（核心：事件 -> 史料）
    st.markdown("**关联史料来源**")
    sids = ev.get("source_ids") or []
    if not sids:
        st.warning("该事件尚未关联史料来源。")
    for sid in sids:
        s = sources.get(sid)
        if s is None:
            st.warning(f"事件引用了不存在的史料编号：{sid}（数据关联错误，请检查 events.json）")
            continue
        link = (s.get("source_url") or "").strip()
        link_html = f'<a href="{link}" target="_blank">🔗 打开来源</a>' if link \
            else '<span style="color:var(--qd-muted);">无在线链接</span>'
        st.markdown(f"""
        <div class="qd-src-card">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;">
            <div>
              <div class="qd-src-id">{s['source_id']}</div>
              <div class="qd-src-title">{s.get('title','')}</div>
              <div class="qd-src-pub">{s.get('publisher','')} · {s.get('publication_date','日期待核验')}</div>
            </div>
            <div class="qd-src-meta">{utils.source_badge(s.get('verification_status','待核验'))} &nbsp;{link_html}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"查看史料档案 · {sid}", key=f"evsrc_{sid}_{event_id}"):
            st.session_state.selected_source = sid
            navigate("史料档案")
            return

    # 相关地点跳转
    locs, _ = utils.load_locations()
    related_locs = [l for l in locs if event_id in (l.get("related_events") or [])]
    if related_locs:
        st.markdown("**相关历史地点**")
        for l in related_locs:
            st.markdown(f'<span class="qd-chip">📍 {l["name"]}</span>', unsafe_allow_html=True)
        if st.button("前往历史空间展示"):
            st.session_state.selected_event = event_id  # 保持上下文
            navigate("历史空间")
            return

    if st.button("← 返回时间轴"):
        st.session_state.selected_event = None
        st.rerun()
