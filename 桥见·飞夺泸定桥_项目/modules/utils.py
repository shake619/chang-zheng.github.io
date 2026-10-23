# -*- coding: utf-8 -*-
"""通用工具：数据加载、校验提示与跨页面状态。

所有历史数据与界面代码分离，均从 data/*.json 读取；
文件缺失、JSON 损坏、字段缺失时给出明确提示而不是让页面崩溃。
"""
import json
import os
from pathlib import Path

import streamlit as st

# 项目根目录（modules/ 的上一级）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

REQUIRED_EVENT_FIELDS = ("event_id", "date", "display_date", "title",
                         "summary", "detail", "source_ids", "verification_status")
REQUIRED_SOURCE_FIELDS = ("source_id", "title", "publisher", "source_url",
                          "source_type", "supported_claims", "verification_status",
                          "rights_status", "notes")
REQUIRED_LOCATION_FIELDS = ("location_id", "name", "description",
                            "related_events", "source_ids")
REQUIRED_QUIZ_FIELDS = ("question_id", "question", "options", "correct_index",
                        "explanation", "source_ids")

# 核验状态 -> 徽章样式（文本、颜色）
STATUS_BADGE = {
    "已核验": ("✅ 已核验", "#2e7d32", "rgba(46,125,50,.12)"),
    "待核验": ("⏳ 待核验", "#b26a00", "rgba(179,106,0,.12)"),
    "存在争议": ("⚠️ 存在争议", "#c62828", "rgba(198,40,40,.12)"),
}


def _load_json(filename: str):
    """读取 data 目录下的 JSON 文件；出错时返回 None 并在页面提示。"""
    path = DATA_DIR / filename
    if not path.exists():
        st.error(f"数据文件缺失：`data/{filename}`。请检查项目是否完整。")
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        st.error(f"数据文件 `data/{filename}` 格式错误（JSON 解析失败）：{e}")
        return None


def _pick(obj: dict, key_list):
    """取 obj 中第一个存在且非空的键值；用于兼容顶层列表或带 _meta 包裹的结构。"""
    for k in key_list:
        if isinstance(obj, dict) and isinstance(obj.get(k), list):
            return obj[k]
    return []


@st.cache_data(ttl=3600)
def load_events():
    """加载历史事件列表，按 date 字符串排序。"""
    data = _load_json("events.json")
    if data is None:
        return []
    events = _pick(data, ("events",))
    for ev in events:
        missing = [f for f in REQUIRED_EVENT_FIELDS if f not in ev]
        if missing:
            st.warning(f"事件 {ev.get('event_id', '?')} 缺少字段：{', '.join(missing)}")
    return sorted(events, key=lambda e: (str(e.get("sort_date") or e.get("date", "")),
                                         int(e.get("day_order", 0))))


@st.cache_data(ttl=3600)
def load_sources():
    """加载史料列表。"""
    data = _load_json("sources.json")
    if data is None:
        return []
    sources = _pick(data, ("sources",))
    for s in sources:
        missing = [f for f in REQUIRED_SOURCE_FIELDS if f not in s]
        if missing:
            st.warning(f"史料 {s.get('source_id', '?')} 缺少字段：{', '.join(missing)}")
    return sources


@st.cache_data(ttl=3600)
def load_locations():
    """加载历史空间地点列表。"""
    data = _load_json("locations.json")
    if data is None:
        return [], ""
    if isinstance(data, dict):
        return _pick(data, ("locations",)), data.get("map_note", "")
    return [], ""


@st.cache_data(ttl=3600)
def load_quiz():
    """加载问答题目。"""
    data = _load_json("quiz.json")
    if data is None:
        return []
    return _pick(data, ("questions",))


# ---------- 索引辅助 ----------

def build_event_index(events):
    return {e["event_id"]: e for e in events if e.get("event_id")}


def build_source_index(sources):
    return {s["source_id"]: s for s in sources if s.get("source_id")}


def source_badge(status: str) -> str:
    """把核验状态渲染成小徽章 HTML。"""
    text, color, bg = STATUS_BADGE.get(status, ("❓ 未知状态", "#757575", "rgba(0,0,0,.06)"))
    return (f'<span style="display:inline-block;padding:2px 10px;border-radius:999px;'
            f'font-size:.78rem;color:{color};background:{bg};'
            f'border:1px solid {color}33;">{text}</span>')


def source_link(s: dict) -> str:
    """史料来源链接：有 URL 显示链接，否则显示馆藏/核验说明。"""
    url = (s.get("source_url") or "").strip()
    if url:
        return f'<a href="{url}" target="_blank">🔗 查看原始来源</a>'
    return '<span style="color:var(--qd-muted);">无在线链接（见核验说明）</span>'


# ---------- 跨页面会话状态 ----------

def init_session():
    """初始化会话状态：当前页面、选中的事件/史料/地点。"""
    defaults = {
        "page": "首页",
        "selected_event": None,
        "selected_source": None,
        "selected_location": None,
        "quiz_answers": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def load_css():
    """注入全局样式表。"""
    css_path = PROJECT_ROOT / "assets" / "styles" / "main.css"
    if css_path.exists():
        st.markdown(f'<style>{css_path.read_text(encoding="utf-8")}</style>',
                    unsafe_allow_html=True)
    else:
        st.warning("样式文件缺失：assets/styles/main.css（页面将以默认样式显示）")
