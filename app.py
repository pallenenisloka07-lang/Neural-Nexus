import streamlit as st
import random
import speech_recognition as sr
import tempfile
from pydub import AudioSegment
from streamlit_mic_recorder import mic_recorder

st.set_page_config(page_title="HireMate AI", layout="wide")

# =========================
# 🎨 CLEAN BRIGHT UI
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef2ff, #e0f2fe);
    color: #111827;
}
section[data-testid="stSidebar"] {
    background: #1e293b !important;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}
.topbar {
    background: white;
    padding: 18px 25px;
    border-radius: 14px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}
.main-title {
    font-size: 34px;
    font-weight: 800;
    color: #111827;
}
.subtitle {
    color: #6b7280;
}
.card {
    background: white;
    padding: 25px;
    border-radius: 16px;
    margin-top: 20px;
}
.info-box {
    background: #e0f2fe;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #2563eb;
    margin-bottom: 15px;
}
.stButton>button {
    width: 100%;
    height: 48px;
    border-radius: 10px;
    background: #2563eb;
    color: white;
    font-weight: bold;
}
textarea {
    background: white !important;
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("""
<div class="topbar">
    <div class="main-title">HireMate AI</div>
    <div class="subtitle">Your Personal AI Interview Coach</div>
</div>
""", unsafe_allow_html=True)

# =========================
# 🔊 VOICE FUNCTIONS
# =========================
def speak_question(text):
    js = f"""
    <script>
    var msg = new SpeechSynthesisUtterance(`{text}`);
    msg.rate = 0.9;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js, height=0)

def speak_full(level, feedback, improvement, better):
    text = f"{level}. {feedback}. Improve like this: {improvement}. Better answer: {better}"
    js = f"""
    <script>
    var msg = new SpeechSynthesisUtterance(`{text}`);
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js, height=0)

# =========================
# QUESTIONS
# =========================
QUESTION_SETS = {
    "Fresher":[
        "Tell me about yourself",
        "What are your strengths",
        "Tell me about one academic project",
        "Why should we hire you",
        "Where do you see yourself in five years"
    ],
    "Experienced":[
        "Tell me about your work experience",
        "What is your biggest achievement",
        "Describe a difficult project you handled",
        "Why are you changing your job",
        "How do you handle deadlines"
    ],
    "HR Discussion":[
        "How are you feeling today",
        "What motivates you",
        "How do you handle conflict",
        "What environment suits you",
        "What are your career goals"
    ]
}

# =========================
# 🔥 UPDATED FEEDBACK ONLY
# =========================
def evaluate_answer(question, answer):

    answer = answer.lower()
    q = question.lower()

    if len(answer) < 10:
        level = "Bad Answer"
        score = random.randint(2,4)
    elif len(answer) < 30:
        level = "Average Answer"
        score = random.randint(4,6)
    else:
        level = "Good Answer"
        score = random.randint(7,9)

    if "yourself" in q:
        feedback = "You did not introduce yourself properly."
        improvement = "Include name, education, skills, and goal."
        better = """I am an AIML student with strong interest in machine learning.
I have worked on projects like fraud detection using XGBoost.
I enjoy solving real-world problems."""

    elif "strength" in q:
        feedback = "Your strengths are not clearly explained."
        improvement = "Mention strengths with examples."
        better = """My strengths include problem-solving and teamwork.
I adapt quickly and handle challenges effectively."""

    elif "project" in q:
        feedback = "Project explanation is not detailed."
        improvement = "Explain role, tools, and result."
        better = """I worked on a fraud detection system using machine learning.
I used XGBoost and improved accuracy."""

    elif "hire" in q:
        feedback = "You did not explain your value clearly."
        improvement = "Show confidence and value."
        better = """You should hire me because I am a quick learner
and ready to contribute effectively."""

    elif "five years" in q:
        feedback = "Your career vision is unclear."
        improvement = "Explain future goals clearly."
        better = """In five years, I see myself as a skilled AI engineer
working on impactful projects."""

    elif "motivate" in q:
        feedback = "Motivation is not clearly explained."
        improvement = "Explain what drives you."
        better = """I am motivated by solving real-world problems
and continuously learning new skills."""

    else:
        feedback = "Your answer needs clarity."
        improvement = "Structure your answer better."
        better = "Give a structured answer with examples."

    return level, feedback, improvement, score, better


# =========================
# SESSION
# =========================
if "started" not in st.session_state:
    st.session_state.started = False

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "spoken_q" not in st.session_state:
    st.session_state.spoken_q = False


# =========================
# SIDEBAR
# =========================
st.sidebar.title("Dashboard")

mode = st.sidebar.selectbox("Candidate Type", ["Fresher","Experienced","HR Discussion"])
style = st.sidebar.selectbox("Interviewer Style", ["Friendly","Strict","Mixed"])

if st.sidebar.button("Reset"):
    st.session_state.started = False
    st.session_state.q_index = 0
    st.session_state.spoken_q = False
    st.rerun()


# =========================
# HOME
# =========================
if not st.session_state.started:

    st.markdown(f"""
    <div class="card">
        <div class="info-box">
            Candidate Type: {mode}<br>
            Interviewer Style: {style}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Start Interview"):
        st.session_state.started = True
        st.session_state.spoken_q = False
        st.rerun()


# =========================
# INTERVIEW
# =========================
if st.session_state.started:

    questions = QUESTION_SETS[mode]

    if st.session_state.q_index < len(questions):

        q = questions[st.session_state.q_index]

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-box">
            Candidate Type: {mode}<br>
            Interviewer Style: {style}
        </div>
        """, unsafe_allow_html=True)

        st.subheader(f"Question {st.session_state.q_index+1}")
        st.write(q)

        if not st.session_state.spoken_q:
            speak_question(q)
            st.session_state.spoken_q = True

        audio = mic_recorder(
            start_prompt="Start Speaking",
            stop_prompt="Stop",
            key=f"mic_{st.session_state.q_index}"
        )

        if audio:

            recognizer = sr.Recognizer()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as f:
                f.write(audio["bytes"])
                webm_path = f.name

            wav_path = webm_path.replace(".webm", ".wav")
            AudioSegment.from_file(webm_path).export(wav_path, format="wav")

            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)

            try:
                transcript = recognizer.recognize_google(audio_data)
            except:
                transcript = "Could not understand clearly"

            st.write("You said:", transcript)

            level, fb, improve, score, better = evaluate_answer(q, transcript)

            st.write(level)
            st.write("Feedback:", fb)
            st.write("Improvement:", improve)
            st.write("Score:", score)
            st.write("Better Answer:", better)

            speak_full(level, fb, improve, better)

            if st.button("Next"):
                st.session_state.q_index += 1
                st.session_state.spoken_q = False
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("<h2 style='text-align:center;color:#111827;'>Interview Completed</h2>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Hire Score", "50%")
        c2.metric("Confidence", "87%")
        c3.metric("Communication", "79%")

        st.line_chart([6,5,6,4,4])