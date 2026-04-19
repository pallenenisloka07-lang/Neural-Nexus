import streamlit as st
import random
import speech_recognition as sr
import tempfile
from pydub import AudioSegment
from streamlit_mic_recorder import mic_recorder

st.set_page_config(page_title="HireMate AI", layout="wide")

# =========================
# 🌐 AMAZON STYLE UI
# =========================
st.markdown("""
<style>

/* Background */
.stApp{
background: #f3f4f6;
color: #111827;
}

/* Sidebar */
section[data-testid="stSidebar"]{
background: #111827 !important;
}
section[data-testid="stSidebar"] *{
color:white !important;
}

/* Header */
.header{
background:white;
padding:15px;
border-radius:10px;
box-shadow:0 2px 10px rgba(0,0,0,0.1);
margin-bottom:20px;
}

/* Title */
.title{
text-align:center;
font-size:42px;
font-weight:700;
color:#111827;
}

/* Card */
.card{
background:white;
padding:25px;
border-radius:12px;
margin-top:20px;
box-shadow:0 4px 20px rgba(0,0,0,0.08);
}

/* Button */
.stButton>button{
width:100%;
height:48px;
border-radius:8px;
background:#2563eb;
color:white;
font-weight:600;
border:none;
}
.stButton>button:hover{
background:#1d4ed8;
}

/* Selected box */
.selected-box{
background:#e0f2fe;
padding:15px;
border-radius:10px;
border-left:5px solid #2563eb;
margin-bottom:15px;
color:#111827;
}

/* Text */
h1,h2,h3,p{
color:#111827 !important;
}

/* Input */
textarea{
background:white !important;
color:black !important;
}

/* Center */
.block-container{
max-width:900px;
margin:auto;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("""
<div class="header">
    <h2 style="margin:0;">HireMate AI</h2>
</div>
""", unsafe_allow_html=True)

# =========================
# VOICE
# =========================
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
# FEEDBACK
# =========================
def evaluate_answer(question, answer):

    answer = answer.lower()

    if len(answer) < 10:
        level = "Bad Answer"
        score = random.randint(2,4)
    elif len(answer) < 30:
        level = "Average Answer"
        score = random.randint(4,6)
    else:
        level = "Good Answer"
        score = random.randint(7,9)

    if "yourself" in question.lower():
        feedback = "Introduce yourself clearly with skills."
        improvement = "Use: Name → Skills → Goal"
        better = "I am an AIML student interested in AI with project experience."

    elif "strength" in question.lower():
        feedback = "Mention strengths with proof."
        improvement = "Add example"
        better = "My strength is problem solving and quick learning."

    elif "project" in question.lower():
        feedback = "Explain project properly."
        improvement = "Use structured explanation"
        better = "I built a fraud detection system using ML."

    elif "hire" in question.lower():
        feedback = "Convince interviewer."
        improvement = "Show value"
        better = "I am motivated and ready to contribute."

    else:
        feedback = "Answer needs structure."
        improvement = "Be clear"
        better = "Give structured answer."

    return level, feedback, improvement, score, better


# =========================
# SESSION
# =========================
if "started" not in st.session_state:
    st.session_state.started = False

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

# =========================
# SIDEBAR
# =========================
st.sidebar.title("Dashboard")

mode = st.sidebar.selectbox(
    "Candidate Type",
    ["Fresher","Experienced","HR Discussion"]
)

style = st.sidebar.selectbox(
    "Interviewer Style",
    ["Friendly","Strict","Mixed"]
)

if st.sidebar.button("Reset"):
    st.session_state.started = False
    st.session_state.q_index = 0
    st.rerun()


# =========================
# HOME
# =========================
if not st.session_state.started:

    st.markdown('<div class="title">HireMate AI</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="selected-box">
        <b>Candidate Type:</b> {mode} <br>
        <b>Interviewer Style:</b> {style}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    if st.button("Start Interview"):
        st.session_state.started = True
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# INTERVIEW
# =========================
if st.session_state.started:

    questions = QUESTION_SETS[mode]

    if st.session_state.q_index < len(questions):

        q = questions[st.session_state.q_index]

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="selected-box">
            <b>Candidate Type:</b> {mode} <br>
            <b>Interviewer Style:</b> {style}
        </div>
        """, unsafe_allow_html=True)

        st.subheader(f"Question {st.session_state.q_index+1}")
        st.write(q)

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
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("<h1 style='text-align:center'>HireMate AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center'>Interview Completed</p>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Hire Score", "50%")
        c2.metric("Confidence", "87%")
        c3.metric("Communication", "79%")

        st.line_chart([6,5,6,4,4])