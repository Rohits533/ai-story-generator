import streamlit as st
from groq import Groq
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
import io

st.set_page_config(
    page_title="AI Story Generator",
    page_icon="📖",
    layout="centered"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    .stApp { 
        background: linear-gradient(135deg, #0f1117 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }
    h1 { 
        background: linear-gradient(90deg, #00d4ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 2.5em !important;
        font-weight: 700 !important;
    }
    p { color: #888; text-align: center; }
    .story-box {
        background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
        border-radius: 20px;
        padding: 35px;
        border: 1px solid rgba(0, 212, 255, 0.2);
        margin: 10px 0;
        line-height: 1.9;
        font-size: 16px;
        color: #cdd6f4;
        animation: fadeIn 0.5s ease;
    }
    .genre-badge {
        display: inline-block;
        background: linear-gradient(90deg, #00d4ff, #7b2ff7);
        border-radius: 20px;
        padding: 6px 18px;
        font-size: 13px;
        font-weight: 600;
        color: white;
        margin: 4px;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stButton button {
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>📖 AI Story Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:16px'>Enter your idea — AI writes a creative story for you</p>", unsafe_allow_html=True)
st.divider()

api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

def generate_pdf(story, title, genre):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=20*mm, leftMargin=20*mm,
                           topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'],
                                fontSize=20, textColor=colors.HexColor('#00d4ff'),
                                spaceAfter=10, alignment=1)
    genre_style = ParagraphStyle('Genre', parent=styles['Normal'],
                                fontSize=12, textColor=colors.HexColor('#7b2ff7'),
                                spaceAfter=16, alignment=1)
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
                               fontSize=11, spaceAfter=8, leading=18)
    story_content = []
    story_content.append(Paragraph(title, title_style))
    story_content.append(Paragraph(f"Genre: {genre}", genre_style))
    story_content.append(Spacer(1, 6*mm))
    for para in story.split('\n'):
        if para.strip():
            story_content.append(Paragraph(para.strip(), body_style))
            story_content.append(Spacer(1, 3*mm))
    doc.build(story_content)
    buffer.seek(0)
    return buffer

col1, col2 = st.columns(2)
with col1:
    genre = st.selectbox("Genre:", [
        "🚀 Science Fiction",
        "🧙 Fantasy",
        "😱 Horror",
        "❤️ Romance",
        "🗺️ Adventure",
        "🔍 Mystery",
        "😄 Comedy",
        "🌟 Motivational"
    ])
with col2:
    length = st.selectbox("Story Length:", [
        "Short (300 words)",
        "Medium (600 words)",
        "Long (1000 words)"
    ])

col3, col4 = st.columns(2)
with col3:
    character = st.text_input("Main Character:", placeholder="e.g. Arjun, a young engineer")
with col4:
    setting = st.text_input("Setting:", placeholder="e.g. Mumbai in 2050")

plot = st.text_area("Story Idea:", placeholder="e.g. A young developer discovers his AI has become sentient...", height=100)

if st.button("✍️ Generate Story", use_container_width=True):
    if plot:
        word_count = length.split("(")[1].replace(" words)", "")

        with st.spinner("Writing your story..."):
            prompt = f"""Write a {word_count} word {genre} story with the following details:

Main Character: {character if character else "A protagonist of your choice"}
Setting: {setting if setting else "A setting that fits the genre"}
Plot idea: {plot}

Instructions:
- Write an engaging, creative story
- Include vivid descriptions
- Have a clear beginning, middle and end
- Make it emotionally engaging
- Give the story a title at the very beginning
- Write in a professional literary style"""

            # STREAMING — text appears word by word!
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"You are a creative {genre} writer. Write engaging, vivid stories that captivate readers."},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )

            st.markdown("### 📖 Your Story")
            story_placeholder = st.empty()
            full_story = ""

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_story += chunk.choices[0].delta.content
                    story_placeholder.markdown(f"""
                    <div class="story-box">{full_story}▌</div>
                    """, unsafe_allow_html=True)

            story_placeholder.markdown(f"""
            <div class="story-box">{full_story}</div>
            """, unsafe_allow_html=True)

            st.session_state.story = full_story
            st.session_state.genre = genre

        st.divider()

    else:
        st.warning("Please enter a story idea first!")

if "story" in st.session_state:
    title_line = st.session_state.story.split('\n')[0].replace('#', '').strip()
    pdf = generate_pdf(st.session_state.story, title_line, st.session_state.genre)
    st.download_button(
        label="📥 Download Story as PDF",
        data=pdf,
        file_name="my_story.pdf",
        mime="application/pdf",
        use_container_width=True
    )

st.markdown("<p style='margin-top:20px'>Built by Rohit • Powered by Groq + Llama 3</p>", unsafe_allow_html=True)
