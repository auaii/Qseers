"""Qseer — Modernized web interface with streaming agent steps and output."""

import sys
import tempfile
from pathlib import Path

import streamlit as st
from langchain_core.messages import AIMessageChunk, ToolMessage

# ── Path setup ────────────────────────────────────────────────────────────────
_root = Path(__file__).parent.parent
_src = _root / "src"
sys.path.insert(0, str(_src / "orchestrate_agent"))
sys.path.insert(0, str(_src))

@st.cache_resource(show_spinner="Loading Qseer agents…")
def load_agent():
    from Main_agent import Main_agent as _agent  # noqa: E402
    return _agent

Main_agent = load_agent()

# ── Tool metadata: (icon, label, description) ─────────────────────────────────
TOOL_META: dict[str, tuple[str, str, str]] = {
    "analyze_face_image": ("🔍", "Visual Analysis",    "Analyzing facial features via vision model"),
    "Visual_Structure":   ("📐", "Structure Record",   "Recording facial structure"),
    "RAG_Search":         ("📚", "Knowledge Search",   "Searching Wuxing knowledge base"),
    "think_tool":         ("🧠", "Reasoning",          "Reasoning about findings"),
}

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Qseer · Face Destiny Analysis",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Inject CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Global ───────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif;
}
.stApp {
    background: radial-gradient(ellipse at top, #1a0533 0%, #0d0d1a 55%, #050510 100%);
    min-height: 100vh;
}
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 820px !important;
}

/* ── Hide Streamlit chrome ───────────────────────── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Hero ────────────────────────────────────────── */
.hero {
    text-align: center;
    padding: 2rem 1rem 1rem;
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(120deg, #f6d365 0%, #fda085 50%, #f6d365 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 3s linear infinite;
    letter-spacing: -1px;
    margin: 0 0 6px 0;
}
@keyframes shimmer { to { background-position: 200% center; } }
.hero-sub {
    color: rgba(255,255,255,0.35);
    font-size: 0.78rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin: 0;
}

/* ── Section labels ──────────────────────────────── */
.section-label {
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.4);
    margin-bottom: 8px;
}

/* ── Mode badge ──────────────────────────────────── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 14px;
    border-radius: 99px;
    font-size: 0.78rem;
    font-weight: 500;
    margin: 8px 0 4px;
}
.badge-img  { background: rgba(99,102,241,.15); border: 1px solid rgba(99,102,241,.35); color: #a5b4fc; }
.badge-txt  { background: rgba(16,185,129,.15); border: 1px solid rgba(16,185,129,.35); color: #6ee7b7; }
.badge-both { background: rgba(245,158,11,.15);  border: 1px solid rgba(245,158,11,.35); color: #fcd34d; }

/* ── Divider ─────────────────────────────────────── */
.qdivider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
    margin: 1.2rem 0;
}

/* ── Pipeline step cards ─────────────────────────── */
.step-card {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 6px;
    animation: fadeIn 0.25s ease;
}
.step-call {
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.25);
}
.step-done {
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.2);
}
.step-icon { font-size: 1.1rem; line-height: 1.4; }
.step-body { flex: 1; }
.step-title { font-size: 0.85rem; font-weight: 600; color: rgba(255,255,255,0.9); margin: 0; }
.step-desc  { font-size: 0.75rem; color: rgba(255,255,255,0.4); margin: 2px 0 0; }
.step-preview {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.3);
    margin: 4px 0 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 580px;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }

/* ── Output area ─────────────────────────────────── */
.output-wrap {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
}
.output-wrap p, .output-wrap li, .output-wrap h1,
.output-wrap h2, .output-wrap h3, .output-wrap h4 {
    color: rgba(255,255,255,0.88);
}
.output-wrap h2 { font-size: 1.15rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 6px; margin-top: 1.2rem; }
.output-wrap h3 { font-size: 0.97rem; color: rgba(253,211,77,0.9) !important; margin-top: 1rem; }
.cursor { animation: blink 0.9s step-end infinite; }
@keyframes blink { 50% { opacity: 0; } }

/* ── Streamlit widget overrides ──────────────────── */
.stTextArea textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: rgba(255,255,255,0.9) !important;
    font-size: 0.88rem !important;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: rgba(99,102,241,0.5) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}
.stFileUploader > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px dashed rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
}
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 0 !important;
    transition: opacity 0.18s, transform 0.18s !important;
    width: 100% !important;
}
.stButton > button:hover:not(:disabled) {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:disabled { opacity: 0.3 !important; cursor: not-allowed !important; }

/* ── Status widget ───────────────────────────────── */
[data-testid="stStatusWidget"] { color: rgba(255,255,255,0.6) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <p class="hero-title">🔮 Qseer</p>
    <p class="hero-sub">โหง่วเฮ้ง &nbsp;·&nbsp; Five Element Face Reading &nbsp;·&nbsp; 黃局五行相面</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="qdivider"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# INPUT SECTION
# ─────────────────────────────────────────────────────────────────────────────
col_img, col_txt = st.columns([1, 1], gap="large")

with col_img:
    st.markdown('<p class="section-label">📷 Face Image</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "upload", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed"
    )
    if uploaded_file:
        st.image(uploaded_file, width="stretch")

with col_txt:
    st.markdown('<p class="section-label">✏️ Face Description <span style="opacity:.45">(optional)</span></p>', unsafe_allow_html=True)
    text_input = st.text_area(
        "desc",
        placeholder=(
            "เช่น ใบหน้ารูปไข่ หน้าผากกว้างและสูง\n"
            "คิ้วหนาตรง จมูกโด่ง ริมฝีปากอิ่ม คางกลม\n\n"
            "Or describe features in English…"
        ),
        height=210,
        label_visibility="collapsed",
    )

# ── Mode badge ────────────────────────────────────────────────────────────────
has_image = uploaded_file is not None
has_text  = bool(text_input.strip())

if has_image and has_text:
    st.markdown('<span class="badge badge-both">⚡ Image + Text mode</span>', unsafe_allow_html=True)
elif has_image:
    st.markdown('<span class="badge badge-img">📷 Image only mode</span>', unsafe_allow_html=True)
elif has_text:
    st.markdown('<span class="badge badge-txt">✏️ Text only mode</span>', unsafe_allow_html=True)

st.markdown('<div class="qdivider"></div>', unsafe_allow_html=True)

analyze = st.button(
    "✨ &nbsp; Analyze Destiny",
    type="primary",
    disabled=not (has_image or has_text),
    use_container_width=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS FLOW
# ─────────────────────────────────────────────────────────────────────────────
if analyze:
    # Save uploaded image to a temp file
    image_path = None
    if uploaded_file:
        suffix = Path(uploaded_file.name).suffix or ".jpg"
        tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        tmp.write(uploaded_file.getvalue())
        tmp.close()
        image_path = tmp.name

    parts = []
    if image_path:
        parts.append(f"image_path: {image_path}")
    if has_text:
        parts.append(f"text: {text_input.strip()}")
    user_content = "\n".join(parts)

    st.markdown('<div class="qdivider"></div>', unsafe_allow_html=True)

    # ── Pipeline status block (live steps stream into here) ───────────────────
    st.markdown('<p class="section-label">🔄 Agent Pipeline</p>', unsafe_allow_html=True)
    pipeline = st.status("Running multiagent pipeline…", expanded=True, state="running")

    # ── Output area (streams below, outside the pipeline block) ──────────────
    st.markdown('<p class="section-label">📋 Destiny Reading</p>', unsafe_allow_html=True)
    output_slot = st.empty()

    full_response = ""
    seen_tools: set[str] = set()

    try:
        with pipeline:
            for chunk, _ in Main_agent.stream(
                {"messages": [{"role": "user", "content": user_content}]},
                stream_mode="messages",
            ):

                # ── Streaming AI text ─────────────────────────────────────────
                if isinstance(chunk, AIMessageChunk):
                    if chunk.content:
                        full_response += chunk.content
                        # Live-update the output slot with a blinking cursor
                        output_slot.markdown(
                            f'<div class="output-wrap">\n\n{full_response}'
                            '<span class="cursor"> ▌</span></div>',
                            unsafe_allow_html=True,
                        )

                    # Tool call announced (first chunk carries the name)
                    for tc in chunk.tool_call_chunks or []:
                        name = tc.get("name")
                        if name and name not in seen_tools:
                            seen_tools.add(name)
                            icon, label, desc = TOOL_META.get(name, ("⚙️", name, "Processing…"))
                            st.markdown(
                                f'<div class="step-card step-call">'
                                f'  <span class="step-icon">{icon}</span>'
                                f'  <div class="step-body">'
                                f'    <p class="step-title">{label}</p>'
                                f'    <p class="step-desc">{desc}</p>'
                                f'  </div>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

                # ── Tool result ───────────────────────────────────────────────
                elif isinstance(chunk, ToolMessage):
                    name  = getattr(chunk, "name", "tool")
                    icon, label, _ = TOOL_META.get(name, ("⚙️", name, ""))
                    preview = chunk.content.replace("\n", " ")[:260]
                    if len(chunk.content) > 260:
                        preview += "…"
                    st.markdown(
                        f'<div class="step-card step-done">'
                        f'  <span class="step-icon">✅</span>'
                        f'  <div class="step-body">'
                        f'    <p class="step-title">{label} — completed</p>'
                        f'    <p class="step-preview">{preview}</p>'
                        f'  </div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

        # Streaming done — remove cursor, collapse pipeline
        pipeline.update(label="✅ Analysis complete", state="complete", expanded=False)
        output_slot.markdown(
            f'<div class="output-wrap">\n\n{full_response}</div>',
            unsafe_allow_html=True,
        )

    except Exception as exc:
        pipeline.update(label=f"❌ Error occurred", state="error", expanded=True)
        st.error(str(exc))
