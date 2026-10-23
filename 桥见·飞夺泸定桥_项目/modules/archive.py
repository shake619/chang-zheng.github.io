# -*- coding: utf-8 -*-
"""史料档案库：列表、筛选、搜索、详情与双向关联。"""
import streamlit as st

from modules import utils

TYPE_OPTIONS = ["全部", "文献", "历史图片", "地图", "视频", "研究资料"]


def render(navigate):
    sources = utils.load_sources()
    events = utils.build_event_index(utils.load_events())

    sel = st.session_state.get("selected_source")
    if sel:
        _render_detail(sel, sources, events, navigate)
    else:
        _render_list(sources, navigate)


def _open_source(source_id: str):
    """按钮回调：记录选中史料并刷新。"""
    st.session_state.selected_source = source_id


def _render_list(sources, navigate):
    st.markdown("""
    <div class="qd-section-head"><div class="rule"></div>
      <h2>史料档案与来源追溯</h2>
      <p>本展览的核心特色。每条资料记录来源、核验状态与它所支持的历史陈述；
      没有经过实际核验的资料不会被标记为「已核验」。</p>
    </div>
    """, unsafe_allow_html=True)

    if not sources:
        st.warning("暂无史料数据（sources.json 为空或读取失败）。")
        return

    f1, f2 = st.columns([1, 2])
    with f1:
        ftype = st.selectbox("按资料类型筛选", TYPE_OPTIONS)
    with f2:
        kw = st.text_input("关键词搜索（标题 / 发布机构 / 支持的历史陈述）", "")

    shown = sources
    if ftype != "全部":
        shown = [s for s in shown if s.get("source_type") == ftype]
    if kw.strip():
        k = kw.strip().lower()
        shown = [s for s in shown
                 if k in s.get("title", "").lower()
                 or k in s.get("publisher", "").lower()
                 or k in s.get("source_id", "").lower()
                 or any(k in c.lower() for c in s.get("supported_claims", []))]

    st.caption(f"共 {len(shown)} 条 / 全库 {len(sources)} 条")

    for s in shown:
        link = (s.get("source_url") or "").strip()
        link_html = f'<a href="{link}" target="_blank">🔗 查看原始来源</a>' if link \
            else '<span style="color:var(--qd-muted);">无在线链接（见核验说明）</span>'
        n_claims = len(s.get("supported_claims", []))
        left, right = st.columns([4, 1], gap="small")
        with left:
            st.markdown(f"""
            <div class="qd-src-card">
              <div class="qd-src-id">{s['source_id']} · {s.get('source_type','')}</div>
              <div class="qd-src-title">{s.get('title','')}</div>
              <div class="qd-src-pub">{s.get('publisher','')} · {s.get('publication_date') or '日期待核验'}</div>
              <div class="qd-src-meta">
                {utils.source_badge(s.get('verification_status','待核验'))}
                <span class="qd-chip">支持 {n_claims} 条历史陈述</span>
                <span style="color:var(--qd-muted);">{link_html}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
        with right:
            st.markdown('<div class="qd-tl-btn"></div>', unsafe_allow_html=True)
            st.button("查看档案详情", key=f"src_{s['source_id']}",
                      use_container_width=True,
                      on_click=_open_source, args=(s["source_id"],))


def _render_detail(source_id, sources, events, navigate):
    s = next((x for x in sources if x["source_id"] == source_id), None)
    if s is None:
        st.error("未找到该史料档案，请返回列表重新选择。")
        if st.button("← 返回史料列表"):
            st.session_state.selected_source = None
            st.rerun()
        return

    badge = utils.source_badge(s.get("verification_status", "待核验"))
    url = (s.get("source_url") or "").strip()
    url_html = f'<a href="{url}" target="_blank">{url}</a>' if url \
        else "无（待补充正式馆藏或出版信息）"

    st.markdown(f"""
    <div class="qd-detail">
      <div class="qd-src-id">史料档案 · {s['source_id']} · {s.get('source_type','')}</div>
      <h2>{s.get('title','')} &nbsp;{badge}</h2>
      <div class="lead">{s.get('publisher','')}</div>
    </div>
    """, unsafe_allow_html=True)

    d1, d2 = st.columns(2)
    with d1:
        st.markdown("**发布日期 / 出版信息**")
        st.write(s.get("publication_date") or "待核验")
        st.markdown("**实际访问日期**")
        st.write(s.get("accessed_date") or "尚未实际访问")
    with d2:
        st.markdown("**原始来源链接**")
        st.markdown(url_html, unsafe_allow_html=True)
        st.markdown("**版权与使用权限**")
        st.write(s.get("rights_status") or "待确认")

    st.markdown("**该资料支持的历史陈述**")
    claims = s.get("supported_claims", [])
    if claims:
        st.markdown('<ul class="qd-claims">' +
                    "".join(f"<li>{c}</li>" for c in claims) +
                    "</ul>", unsafe_allow_html=True)
    else:
        st.caption("暂无记录。")

    st.markdown("**核验说明**")
    st.caption(s.get("notes", "无"))

    # 反向关联：史料 -> 事件
    st.markdown("**关联的历史事件**")
    related = [e for e in events.values()
               if s["source_id"] in (e.get("source_ids") or [])]
    if not related:
        st.caption("暂无直接关联的事件。")
    for e in related:
        st.markdown(
            f'<span class="qd-chip">{e.get("display_date","")} · {e.get("title","")}</span>',
            unsafe_allow_html=True)
    if related and st.button("在时间轴中查看第一个关联事件"):
        st.session_state.selected_source = None
        st.session_state.selected_event = related[0]["event_id"]
        navigate("时间轴")
        return

    if st.button("← 返回史料列表"):
        st.session_state.selected_source = None
        st.rerun()
