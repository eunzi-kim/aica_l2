import streamlit as st
import random
import json
import os
from datetime import datetime

# Set Page Config
st.set_page_config(page_title="AICA L2 AIU Quiz Bot", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

# ==================== 로컬 저장소 관리 ====================
LEARNING_HISTORY_FILE = "learning_history.json"

def load_learning_history():
    if os.path.exists(LEARNING_HISTORY_FILE):
        try:
            with open(LEARNING_HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 혹시 기존 데이터와 호환성을 위해 기본값 설정
                return {
                    "total_score": data.get("total_score", 0),
                    "wrong_notes": data.get("wrong_notes", []),
                    "solved_indices": data.get("solved_indices", []), # 추가된 부분
                    "last_updated": data.get("last_updated", "")
                }
        except:
            pass
    return {"total_score": 0, "wrong_notes": [], "solved_indices": [], "last_updated": ""}

def save_learning_history(score, wrong_notes, solved_indices):
    """학습 기록을 로컬에 저장"""
    history = {
        "total_score": score,
        "wrong_notes": wrong_notes,
        "solved_indices": solved_indices,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(LEARNING_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def reset_learning_history():
    """학습 기록 초기화"""
    if os.path.exists(LEARNING_HISTORY_FILE):
        os.remove(LEARNING_HISTORY_FILE)
    return {"total_score": 0, "wrong_notes": [], "last_updated": ""}

def get_next_question():
    # 전체 인덱스에서 푼 문제 제외
    all_indices = set(range(len(QUIZ_DATA)))
    solved = set(st.session_state.solved_indices)
    unsolved = list(all_indices - solved)
    
    if not unsolved:
        return None  # 모든 문제를 다 풀었을 때
        
    # 안 푼 문제 중 랜덤 선택
    random_idx = random.choice(unsolved)
    return random_idx, QUIZ_DATA[random_idx]

# 🎨 모던 & 반응형 UI 스타일
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* ===== 전체 배경 ===== */
    .stApp {
        background: linear-gradient(180deg, #f8f9ff 0%, #f0f2ff 100%);
        min-height: 100vh;
    }
    
    /* ===== 메인 컨테이너 ===== */
    .main {
        background: linear-gradient(180deg, #f8f9ff 0%, #f0f2ff 100%);
        padding: 20px !important;
    }
    
    /* ===== 제목 스타일 ===== */
    h1 {
        color: #333 !important;
        font-size: 2.4rem !important;
        font-weight: 900 !important;
        text-align: center;
        margin: 15px 0 20px 0 !important;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    
    h3 {
        color: #333 !important;
        font-weight: 700 !important;
    }
    
    p {
        color: #333 !important;
    }
    
    /* ===== 메트릭 컨테이너 ===== */
    .metric-container {
        display: flex;
        gap: 10px;
        justify-content: space-between;
        margin: 8px 0;
    }
    
    .metric-card {
        flex: 1;
        background: rgba(255, 255, 255, 0.98);
        border-radius: 14px;
        padding: 12px 16px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.4);
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 6px 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #222;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* ===== 질문 카드 ===== */
    .question-card {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 14px;
        padding: 16px 18px;
        margin: 15px 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border-left: 6px solid #667eea;
    }
    
    .category-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 6px 12px;
        border-radius: 25px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 3px 12px rgba(102, 126, 234, 0.3);
    }
    
    .question-text {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1a202c;
        line-height: 1.6;
        margin: 10px 0;
        letter-spacing: 0.2px;
    }
    
    /* ===== 라디오 버튼 스타일 ===== */
    .stRadio {
        margin: 12px 0 !important;
    }
    
    .stRadio > label {
        font-size: 1.05rem !important;
        padding: 12px 14px !important;
        background: rgba(102, 126, 234, 0.06) !important;
        border-radius: 10px !important;
        border: 2px solid rgba(102, 126, 234, 0.2) !important;
        margin: 6px 0 !important;
        transition: all 0.2s ease !important;
        font-weight: 600 !important;
        line-height: 1.4 !important;
        color: #333 !important;
    }
    
    .stRadio > label:hover {
        background: rgba(102, 126, 234, 0.15) !important;
        border-color: #667eea !important;
        transform: translateX(5px) !important;
    }
    }
    
    /* ===== 버튼 스타일 ===== */
    .stButton > button {
        width: 100% !important;
        padding: 10px 16px !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        min-height: 42px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.7) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
    
    /* ===== 채팅 버블 ===== */
    .chat-bubble-bot {
        background: rgba(255, 255, 255, 0.97);
        color: #1a202c;
        padding: 18px 22px;
        border-radius: 20px 20px 20px 2px;
        margin: 18px 0;
        max-width: 95%;
        border-left: 5px solid #667eea;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
        font-size: 1.1rem;
        line-height: 1.6;
        font-weight: 500;
    }
    
    .chat-bubble-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 18px 22px;
        border-radius: 20px 20px 2px 20px;
        margin: 18px 0 18px auto;
        float: right;
        max-width: 95%;
        font-weight: 600;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.35);
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    .clear {
        clear: both;
    }
    
    /* ===== 진행률 표시 ===== */
    .progress-bar {
        background: rgba(200, 200, 220, 0.5);
        border-radius: 15px;
        height: 12px;
        margin: 12px 0;
        overflow: hidden;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.08);
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        transition: width 0.5s ease;
        border-radius: 15px;
        box-shadow: 0 0 8px rgba(102, 126, 234, 0.4);
    }
    
    /* ===== 반응형 디자인 (모바일) ===== */
    @media (max-width: 768px) {
        h1, h3, p, .metric-label, .metric-value {
            color: #333 !important;
            -webkit-text-fill-color: #333 !important; /* 모바일 웹킷 브라우저 대응 */
        }

        /* 2. 라디오 버튼 선택지 스타일 강제 고정 */
        .stRadio > label {
            color: #333 !important;
            background: rgba(255, 255, 255, 0.9) !important;
            border: 2px solid rgba(102, 126, 234, 0.3) !important;
        }

        /* 3. 버튼 색상 재확인 */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            -webkit-text-fill-color: white !important;
        }
        
        .metric-container {
            display: flex !important;
            gap: 8px !important;
            margin: 6px 0 !important;
        }
        
        .metric-card {
            flex: 1 !important;
            padding: 10px 12px !important;
            margin: 0 !important;
        }
        
        .question-text {
            font-size: 1rem;
            margin: 6px 0 !important;
        }
        
        .metric-value {
            font-size: 1.8rem;
            margin: 4px 0 !important;
        }
        
        .metric-label {
            font-size: 0.75rem;
        }
        
        .stRadio > label {
            font-size: 0.95rem !important;
            padding: 10px 12px !important;
            margin: 5px 0 !important;
            color: #333 !important;
        }
        
        .chat-bubble-bot, .chat-bubble-user {
            font-size: 0.9rem;
            padding: 12px 14px !important;
        }
        
        .stButton > button {
            font-size: 0.9rem !important;
            padding: 9px 12px !important;
            min-height: 38px !important;
            /* 아래 3줄을 추가/유지하여 모바일에서도 스타일이 적용되게 합니다 */
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border: none !important;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
        }
        
        .category-badge {
            padding: 4px 8px !important;
            font-size: 0.7rem !important;
            margin-bottom: 6px !important;
        }
        
        .question-card {
            padding: 12px 14px !important;
            margin: 10px 0 !important;
        }
    }
    
    /* ===== 알림 메시지 ===== */
    .stSuccess, .stInfo {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 16px !important;
        border-left: 5px solid #667eea !important;
        font-size: 1.1rem !important;
        padding: 20px !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
</style>
""", unsafe_allow_html=True)

# Sample structured quiz database compiled from AICA L2 core standards (expanded internally)
with open("quiz_data.json", "r", encoding="utf-8") as f:
    QUIZ_DATA = json.load(f)

# 로컬 학습 기록 불러오기
LEARNING_HISTORY = load_learning_history()

# Initialize Session States
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "bot", "content": "안녕하세요! 사내 AICA L2 시험 대비 챗봇입니다. 준비되셨으면 '퀴즈 시작' 버튼을 누르거나 원하는 학습 모드를 선택해 주세요!"}]
if "wrong_notes" not in st.session_state:
    st.session_state.wrong_notes = LEARNING_HISTORY.get("wrong_notes", [])  # 로컬 저장된 오답 불러오기
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "all" # 'all' or 'wrong'
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "score" not in st.session_state:
    st.session_state.score = LEARNING_HISTORY.get("total_score", 0)  # 로컬 저장된 점수 불러오기
if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False
if "solved_indices" not in st.session_state:
    st.session_state.solved_indices = LEARNING_HISTORY.get("solved_indices", [])

st.title("🤖 AICA L2 합격 챗봇")

# 모드 전환 섹션
st.markdown("<h3 style='text-align: center; color: #333; margin-bottom: 20px;'>📚 학습 모드 선택</h3>", unsafe_allow_html=True)

mode_col1, mode_col2 = st.columns(2, gap="small")

with mode_col1:
    if st.button("🎯 전체 문제 풀기", use_container_width=True):
        st.session_state.current_mode = "all"
        st.session_state.current_index = 0
        st.session_state.quiz_active = True
        st.session_state.messages.append({"role": "bot", "content": "🎓 전체 문제 모드로 시작합니다!\n\n지금부터 모든 200개 문제를 풀어봅시다! 화이팅! 💪"})
        st.rerun()

with mode_col2:
    if st.button("🚨 오답 노트 풀기", use_container_width=True):
        if len(st.session_state.wrong_notes) == 0:
            st.info("🎉 아직 틀린 문제가 없습니다! 훌륭해요!")
        else:
            st.session_state.current_mode = "wrong"
            st.session_state.current_index = 0
            st.session_state.quiz_active = True
            st.session_state.messages.append({"role": "bot", "content": f"🎯 오답 노트를 시작합니다!\n\n틀렸던 **{len(st.session_state.wrong_notes)}문제**를 완벽히 마스터해 봅시다! 화이팅! 💪"})
            st.rerun()

# 초기화 버튼
if st.button("🔴 학습 기록 초기화", use_container_width=True):
    reset_learning_history()
    st.session_state.score = 0
    st.session_state.wrong_notes = []
    st.session_state.quiz_active = False
    st.session_state.current_index = 0
    st.session_state.messages = [{"role": "bot", "content": "🔄 모든 학습 기록이 초기화되었습니다.\n\n새로 시작해 봅시다! 파이팅! 💪"}]
    st.success("✅ 학습 기록이 초기화되었습니다!")
    st.rerun()

st.markdown("---")

# 채팅 기록 표시
st.markdown("<h3 style='color: #333; margin-top: 20px; margin-bottom: 15px;'>💬 대화 기록</h3>", unsafe_allow_html=True)

chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "bot":
            st.markdown(f'<div class="chat-bubble-bot">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div><div class="clear"></div>', unsafe_allow_html=True)

# Quiz System Logic
if st.session_state.quiz_active:
    # 1. 푼 문제 리스트와 전체 문제 범위를 기반으로 안 푼 문제 리스트 생성
    solved = st.session_state.solved_indices
    unsolved = [i for i in range(len(QUIZ_DATA)) if i not in solved]
    
    # 2. 모든 문제를 다 풀었는지 확인
    if not unsolved:
        st.balloons()
        st.write("🎉 축하합니다! 모든 문제를 마스터하셨습니다!")
        st.session_state.quiz_active = False
        st.rerun()
    else:
        # [핵심 수정] 현재 세션에 고정된 문제가 없거나, 이미 푼 문제라면 새로 뽑아서 고정합니다.
        if "current_question_idx" not in st.session_state or st.session_state.current_question_idx in solved:
            st.session_state.current_question_idx = random.choice(unsolved)
        
        # 고정된 인덱스로 문제를 가져옵니다.
        q_idx = st.session_state.current_question_idx
        q = QUIZ_DATA[q_idx]
        st.session_state.current_index = q_idx 
        
        # 4. 진행률 계산
        progress = len(solved) / len(QUIZ_DATA)
        progress_percent = int(progress * 100)
        
        # [진행률 표시]
        st.markdown(f"""
        <div style="margin: 20px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #333; font-weight: 700; font-size: 0.95rem;">진행률</span>
                <span style="color: #333; font-weight: 700; font-size: 0.95rem;">{len(solved)} / {len(QUIZ_DATA)} ({progress_percent}%)</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress_percent}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 5. 질문 카드
        st.markdown(f"""
        <div class="question-card">
            <span class="category-badge">{q['category']}</span>
            <div class="question-text">Q. {q['question']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 6. 선택지 (라디오 버튼)
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        # index=None을 주어 처음엔 아무것도 선택되지 않은 상태로 만듭니다.
        choice = st.radio("정답을 선택하세요:", q["options"], key=f"quiz_radio_{q_idx}", index=None, label_visibility="collapsed")
        
        # 7. 제출 버튼
        if st.button("✨ 정답 제출하기", use_container_width=True):
            if choice is None:
                st.warning("⚠️ 정답을 선택한 후 제출해 주세요!")
            else:
                if choice == q["answer"]:
                    st.session_state.score += 1
                    if q_idx not in st.session_state.solved_indices:
                        st.session_state.solved_indices.append(q_idx)
                    st.session_state.messages.append({"role": "bot", "content": f"🎉 **정답입니다!**\n\n📖 {q['explanation']}"})
                else:
                    if q not in st.session_state.wrong_notes:
                        st.session_state.wrong_notes.append(q)
                    st.session_state.messages.append({"role": "bot", "content": f"❌ **아쉽습니다.** 정답: **{q['answer']}**\n\n📖 {q['explanation']}"})
                
                # 저장 후 새로고침 (새로고침 되면 위의 3번 로직에 의해 다음 문제가 뽑힙니다)
                save_learning_history(st.session_state.score, st.session_state.wrong_notes, st.session_state.solved_indices)
                st.rerun()

elif not st.session_state.quiz_active and st.session_state.get("score", 0) > 0:
    pass
        
elif st.session_state.quiz_active:
    st.balloons()
    st.markdown("""
    <div style="text-align: center; margin-top: 40px;">
        <div style="font-size: 3rem; margin-bottom: 20px;">🏆</div>
        <h2 style="color: #333; font-size: 2rem; margin-bottom: 10px;">모든 문제를 완료했습니다!</h2>
        <p style="color: #555; font-size: 1.1rem;">대단한 노력입니다! 💪</p>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.quiz_active = False

# 하단 메트릭 대시보드 (반응형 레이아웃)
st.markdown("---")
st.markdown(f"""
<div class="metric-container">
    <div class="metric-card">
        <div class="metric-label">✅ 맞춘 문제</div>
        <div class="metric-value">{st.session_state.score}</div>
        <div style="color: #333; font-weight: 600; margin-top: 4px; font-size: 0.85rem;">개</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">❌ 오답 노트</div>
        <div class="metric-value">{len(st.session_state.wrong_notes)}</div>
        <div style="color: #333; font-weight: 600; margin-top: 4px; font-size: 0.85rem;">개</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 저장 정보 표시
if LEARNING_HISTORY.get("last_updated"):
    st.markdown(f"""
    <div style="text-align: center; color: #555; font-size: 0.8rem; margin-top: 8px;">
        📅 마지막 저장: <strong>{LEARNING_HISTORY['last_updated']}</strong>
    </div>
    """, unsafe_allow_html=True)
