# -*- coding: utf-8 -*-
"""数据完整性测试：JSON 结构、必需字段、事件-史料关联、核验状态合法性。

运行：python -m pytest tests/ -v
"""
import json
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent
DATA = PROJECT / "data"

VALID_STATUS = {"已核验", "待核验", "存在争议"}


def _load(name, key):
    with open(DATA / name, encoding="utf-8") as f:
        data = json.load(f)
    assert key in data, f"{name} 缺少键 {key}"
    assert isinstance(data[key], list) and data[key], f"{name} 的 {key} 不能为空"
    return data[key]


@pytest.fixture(scope="module")
def events():
    return _load("events.json", "events")


@pytest.fixture(scope="module")
def sources():
    return _load("sources.json", "sources")


@pytest.fixture(scope="module")
def locations():
    return _load("locations.json", "locations")


@pytest.fixture(scope="module")
def quiz():
    return _load("quiz.json", "questions")


def test_data_files_exist():
    for f in ("events.json", "sources.json", "locations.json", "quiz.json"):
        assert (DATA / f).exists(), f"缺少数据文件 {f}"


def test_events_sorted_and_fields(events):
    required = {"event_id", "date", "display_date", "title", "summary",
                "detail", "source_ids", "verification_status"}
    ids = []
    for e in events:
        missing = required - e.keys()
        assert not missing, f"事件 {e.get('event_id')} 缺字段: {missing}"
        ids.append(e["event_id"])
    assert len(ids) == len(set(ids)), "event_id 重复"
    keys = [(e["sort_date"], e["day_order"]) for e in events]
    assert keys == sorted(keys), "事件未按 sort_date/day_order 排序"


def test_sources_fields_and_status(sources):
    required = {"source_id", "title", "publisher", "source_url", "source_type",
                "supported_claims", "verification_status", "rights_status", "notes"}
    ids = []
    for s in sources:
        missing = required - s.keys()
        assert not missing, f"史料 {s.get('source_id')} 缺字段: {missing}"
        assert s["verification_status"] in VALID_STATUS, \
            f"{s['source_id']} 核验状态非法: {s['verification_status']}"
        assert s["source_type"] in {"文献", "历史图片", "地图", "视频", "研究资料"}
        ids.append(s["source_id"])
    assert len(ids) == len(set(ids)), "source_id 重复"


def test_verified_sources_have_url_or_notes(sources):
    """已核验的在线资料必须带 URL 和访问日期；无链接资料必须在 notes 中说明。"""
    for s in sources:
        if s["verification_status"] == "已核验" and not s.get("source_url"):
            assert s.get("accessed_date") and s.get("notes"), \
                f"{s['source_id']} 标为已核验但无来源链接且核验说明不足"
        if s["verification_status"] == "待核验":
            assert s.get("notes"), f"待核验史料 {s['source_id']} 必须给出核验说明"


def test_event_source_links_valid(events, sources):
    sids = {s["source_id"] for s in sources}
    for e in events:
        assert e["source_ids"], f"事件 {e['event_id']} 未关联任何史料"
        bad = set(e["source_ids"]) - sids
        assert not bad, f"事件 {e['event_id']} 引用了不存在的史料: {bad}"


def test_location_links_valid(locations, events, sources):
    eids = {e["event_id"] for e in events}
    sids = {s["source_id"] for s in sources}
    for l in locations:
        bad_e = set(l.get("related_events", [])) - eids
        bad_s = set(l.get("source_ids", [])) - sids
        assert not bad_e, f"地点 {l['location_id']} 关联了不存在的事件: {bad_e}"
        assert not bad_s, f"地点 {l['location_id']} 关联了不存在的史料: {bad_s}"
        assert "svg" in l and "x" in l["svg"] and "y" in l["svg"], \
            f"地点 {l['location_id']} 缺少示意图定位"


def test_quiz_links_valid(quiz, sources, events):
    sids = {s["source_id"] for s in sources}
    eids = {e["event_id"] for e in events}
    for q in quiz:
        assert 0 <= q["correct_index"] < len(q["options"]), \
            f"问题 {q['question_id']} 正确答案索引越界"
        assert set(q["source_ids"]) <= sids, \
            f"问题 {q['question_id']} 引用了不存在的史料"
        assert set(q.get("related_event_ids", [])) <= eids, \
            f"问题 {q['question_id']} 引用了不存在的事件"


def test_modules_importable():
    import modules.utils  # noqa: F401
    import modules.home  # noqa: F401
    import modules.timeline  # noqa: F401
    import modules.archive  # noqa: F401
    import modules.map_view  # noqa: F401
    import modules.quiz  # noqa: F401
    import modules.globe_view  # noqa: F401
