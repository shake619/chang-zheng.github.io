# -*- coding: utf-8 -*-
"""历史理解与互动探索：基于已核验史料的知识问答。"""
import streamlit as st

from modules import utils


def render(navigate):
    questions = utils.load_quiz()
    sources = utils.build_source_index(utils.load_sources())
    events = utils.build_event_index(utils.load_events())

    st.markdown("""
    <div class="qd-section-head"><div class="rule"></div>
      <h2>历史理解与互动探索</h2>
      <p>所有题目均建立在已核验史料之上；每道题的答案都注明依据来源，
      并可跳转到对应的时间轴节点与史料档案。</p>
    </div>
    """, unsafe_allow_html=True)

    if not questions:
        st.warning("暂无问答数据（quiz.json 为空或读取失败）。")
        return

    # 答题
    for q in questions:
        qid = q["question_id"]
        with st.container():
            st.markdown(f'<div class="qd-quiz-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="qd-quiz-q">❓ {q["question"]}</div>',
                        unsafe_allow_html=True)
            choice = st.radio("选择答案", q["options"], index=None,
                              key=f"quiz_{qid}", label_visibility="collapsed")
            if choice is not None:
                i = q["options"].index(choice)
                correct = i == q["correct_index"]
                st.session_state.quiz_answers[qid] = correct
                if correct:
                    st.markdown('<p class="qd-ok">✔ 回答正确</p>',
                                unsafe_allow_html=True)
                else:
                    st.markdown(f'<p class="qd-no">✘ 回答错误。正确答案：'
                                f'{q["options"][q["correct_index"]]}</p>',
                                unsafe_allow_html=True)
                st.info(f"**依据**：{q['explanation']}")

                # 依据来源
                sids = q.get("source_ids", [])
                src_names = "、".join(
                    f"{sources[sid]['title']}（{sid}）" for sid in sids if sid in sources)
                if src_names:
                    st.caption(f"来源：{src_names}")
                # 跳转按钮
                evs = [events[e] for e in q.get("related_event_ids", []) if e in events]
                b1, b2 = st.columns(2)
                with b1:
                    if evs and st.button(f"查看相关事件 · {evs[0]['title'][:14]}…",
                                         key=f"qe_{qid}"):
                        st.session_state.selected_event = evs[0]["event_id"]
                        navigate("时间轴")
                        break
                with b2:
                    if sids and sids[0] in sources and st.button(
                            f"查看史料 · {sids[0]}", key=f"qs_{qid}"):
                        st.session_state.selected_source = sids[0]
                        navigate("史料档案")
                        break
            st.markdown("</div>", unsafe_allow_html=True)

    # 学习结果
    answered = st.session_state.quiz_answers
    if answered:
        n = len(answered)
        c = sum(1 for v in answered.values() if v)
        pct = c / n * 100
        st.markdown(f"""
        <div class="qd-loc-card" style="border-left-color:var(--qd-red);">
          <h3 style="margin-top:0;">🎓 学习结果</h3>
          <p>已完成 <b>{n}</b> 题 · 正确 <b class="qd-ok">{c}</b> 题 ·
          正确率 <b>{pct:.0f}%</b></p>
          <p style="color:var(--qd-muted);font-size:.86rem;">
          {'表现很好！你已经掌握了飞夺泸定桥的核心史实。' if pct >= 80 else
           '建议回到时间轴与史料档案，回顾尚未掌握的细节。'}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("重新作答"):
            st.session_state.quiz_answers = {}
            st.rerun()
    else:
        st.caption("完成作答后，这里将显示你的学习结果。")
