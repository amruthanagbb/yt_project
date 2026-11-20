import streamlit as st
import re
import os
import requests
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI YouTube Summarizer",
    page_icon="🎥",
    layout="wide"
)


# ============================================================
# GLOBAL CSS
# ============================================================

st.html("""
<style>
.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(0,255,200,.12), transparent 30%),
        radial-gradient(circle at 90% 10%, rgba(150,80,255,.14), transparent 30%),
        linear-gradient(135deg, #070b14, #0c1220, #090b17);
    color: white;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

.hero {
    text-align: center;
    padding: 65px 20px 45px 20px;
}

.badge {
    display: inline-block;
    padding: 9px 20px;
    border-radius: 30px;
    background: rgba(100,255,220,.08);
    border: 1px solid rgba(100,255,220,.25);
    color: #8fffe7;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 22px;
}

.hero-title {
    font-size: 60px;
    font-weight: 800;
    line-height: 1.05;
    margin-bottom: 20px;
    background: linear-gradient(90deg,#72ffe0,#9c8cff,#ff82c9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    max-width: 720px;
    margin: auto;
    color: #aeb7ca;
    font-size: 18px;
    line-height: 1.7;
}

.feature-card {
    background: rgba(255,255,255,.045);
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 22px;
    padding: 30px;
    min-height: 215px;
    box-shadow: 0 15px 40px rgba(0,0,0,.25);
}

.feature-icon {
    font-size: 40px;
    margin-bottom: 15px;
}

.feature-title {
    font-size: 21px;
    font-weight: 750;
    color: white;
    margin-bottom: 10px;
}

.feature-text {
    color: #9ba6bb;
    font-size: 14px;
    line-height: 1.7;
}

.section-title {
    font-size: 28px;
    font-weight: 750;
    color: white;
    margin-top: 35px;
    margin-bottom: 18px;
}

.video-info {
    background: rgba(255,255,255,.045);
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 20px;
    padding: 25px;
    min-height: 200px;
}

.video-title {
    font-size: 25px;
    font-weight: 750;
    line-height: 1.35;
    color: white;
}

.channel {
    color: #9aa6bd;
    margin-top: 12px;
}

.stat-card {
    background: rgba(255,255,255,.05);
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 18px;
    padding: 22px 10px;
    text-align: center;
}

.stat-number {
    font-size: 25px;
    font-weight: 800;
    color: #8fffe7;
}

.stat-label {
    margin-top: 6px;
    color: #929db3;
    font-size: 13px;
}

.summary-card {
    background: rgba(255,255,255,.045);
    border: 1px solid rgba(143,255,231,.15);
    border-left: 4px solid #72ffe0;
    border-radius: 16px;
    padding: 28px;
    color: #dfe5f2;
    line-height: 1.8;
}

.comment-card {
    background: rgba(255,255,255,.045);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 15px;
    padding: 18px;
    margin-bottom: 12px;
    color: #dce2ef;
    line-height: 1.6;
}

.positive-label {
    color: #82ffe2;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 8px;
}

.footer-text {
    text-align: center;
    color: #626d82;
    font-size: 12px;
    padding: 30px;
}
</style>
""")


# ============================================================
# LOAD GROQ KEY
# ============================================================

GROQ_KEY_FILE = "groq-api.key"

if not os.path.exists(GROQ_KEY_FILE):
    st.error("❌ groq-api.key was not found.")
    st.info("Make sure groq-api.key is in the same folder as app.py.")
    st.stop()

with open(GROQ_KEY_FILE, "r") as file:
    groq_key = file.read().strip()

if not groq_key:
    st.error("❌ groq-api.key is empty.")
    st.stop()

client = Groq(api_key=groq_key)


# ============================================================
# OPTIONAL YOUTUBE API KEY
# ============================================================

YOUTUBE_KEY_FILE = "youtube-api.key"

youtube_key = None

if os.path.exists(YOUTUBE_KEY_FILE):
    with open(YOUTUBE_KEY_FILE, "r") as file:
        youtube_key = file.read().strip()


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "home"


# ============================================================
# VIDEO ID
# ============================================================

def extract_video_id(url):

    patterns = [
        r"v=([^&]+)",
        r"youtu\.be/([^?&]+)",
        r"youtube\.com/shorts/([^?&]+)",
        r"youtube\.com/embed/([^?&]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)

        if match:
            return match.group(1)

    return None


# ============================================================
# VIDEO INFORMATION
# ============================================================

def get_video_info(url):

    try:

        options = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True
        }

        with yt_dlp.YoutubeDL(options) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

        return {
            "title": info.get("title", "Unknown Title"),
            "channel": info.get("channel", "Unknown Channel"),
            "duration": info.get("duration"),
            "views": info.get("view_count"),
            "likes": info.get("like_count"),
            "thumbnail": info.get("thumbnail")
        }

    except Exception as error:

        st.error(f"❌ Could not retrieve video information: {error}")

        return None


# ============================================================
# NUMBER FORMAT
# ============================================================

def format_number(number):

    if number is None:
        return "N/A"

    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"

    if number >= 1_000:
        return f"{number / 1_000:.1f}K"

    return str(number)


# ============================================================
# DURATION FORMAT
# ============================================================

def format_duration(seconds):

    if seconds is None:
        return "N/A"

    seconds = int(seconds)

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    return f"{minutes}:{seconds:02d}"


# ============================================================
# TRANSCRIPT
# ============================================================

def get_transcript(video_id):

    try:

        api = YouTubeTranscriptApi()

        transcript = api.fetch(
            video_id,
            languages=["en", "hi", "kn", "ta", "te"]
        )

        text = " ".join(
            item.text for item in transcript
        )

        return text

    except Exception as error:

        st.error(f"❌ Transcript Error: {error}")

        return None


# ============================================================
# AI SUMMARY
# ============================================================

def summarize(transcript):

    transcript = transcript[:12000]

    prompt = f"""
You are an expert educational content analyst.

Analyze this YouTube transcript.

Provide the following:

## Summary
Write 150-200 words.

## Five Key Points
Give exactly five important points.

## Three Important Takeaways
Give exactly three useful takeaways.

## Important Keywords
List the important concepts and terms.

## Target Audience
Explain who should watch this video.

## Difficulty Level
Choose Beginner, Intermediate, or Advanced and explain why.

## Suggested Next Learning Steps
Give practical next steps.

Use simple, clear English.

Transcript:

{transcript}
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as error:

        return f"❌ AI Summary Error: {error}"


# ============================================================
# YOUTUBE COMMENTS
# ============================================================

def get_comments(video_id):

    if not youtube_key:
        return []

    try:

        url = "https://www.googleapis.com/youtube/v3/commentThreads"

        params = {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": 20,
            "order": "relevance",
            "textFormat": "plainText",
            "key": youtube_key
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return []

        data = response.json()

        comments = []

        for item in data.get("items", []):

            comment = (
                item["snippet"]
                ["topLevelComment"]
                ["snippet"]
                ["textDisplay"]
            )

            comments.append(comment)

        return comments

    except Exception:
        return []


# ============================================================
# POSITIVE COMMENTS
# ============================================================

def find_positive_comments(comments):

    if not comments:
        return []

    numbered = "\n".join(
        f"{i + 1}. {comment}"
        for i, comment in enumerate(comments)
    )

    prompt = f"""
Analyze these YouTube comments.

Select only comments that are clearly positive,
appreciative, enthusiastic, helpful or praising
the video.

Do not create or modify comments.

Return ONLY the numbers of positive comments.

Comments:

{numbered}
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        answer = response.choices[0].message.content

        numbers = re.findall(r"\d+", answer)

        positive = []

        for number in numbers:

            index = int(number) - 1

            if 0 <= index < len(comments):
                positive.append(comments[index])

        return positive[:5]

    except Exception:
        return []


# ============================================================
# HOME PAGE
# ============================================================

if st.session_state.page == "home":

    st.html("""
    <div class="hero">
        <div class="badge">
            ✨ AI-POWERED LEARNING ASSISTANT
        </div>

        <div class="hero-title">
            🎥 YouTube → Knowledge
        </div>

        <div class="hero-subtitle">
            Transform long YouTube videos into concise summaries,
            useful insights and audience intelligence —
            powered by Artificial Intelligence.
        </div>
    </div>
    """)


    col1, col2, col3 = st.columns(3)


    with col1:

        st.html("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>

            <div class="feature-title">
                AI Summarization
            </div>

            <div class="feature-text">
                Understand lengthy videos through intelligent
                summaries, key points, takeaways and learning steps.
            </div>
        </div>
        """)


    with col2:

        st.html("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>

            <div class="feature-title">
                Video Analytics
            </div>

            <div class="feature-text">
                Explore views, likes, duration, thumbnails and
                other useful information about the video.
            </div>
        </div>
        """)


    with col3:

        st.html("""
        <div class="feature-card">
            <div class="feature-icon">💬</div>

            <div class="feature-title">
                Audience Insights
            </div>

            <div class="feature-text">
                Analyze viewer reactions and discover positive
                comments about the content.
            </div>
        </div>
        """)


    st.write("")


    button_col1, button_col2, button_col3 = st.columns([1, 1, 1])


    with button_col2:

        if st.button(
            "🚀 Start Summarizing",
            use_container_width=True
        ):

            st.session_state.page = "summary"

            st.rerun()


    st.html("""
    <div class="footer-text">
        Built with Python • Streamlit • Groq AI • YouTube APIs
    </div>
    """)


# ============================================================
# SUMMARY PAGE
# ============================================================

elif st.session_state.page == "summary":


    if st.button("← Back to Home"):

        st.session_state.page = "home"

        st.rerun()


    st.html("""
    <div class="hero" style="padding-top:25px;">
        <div class="badge">
            🔍 VIDEO INTELLIGENCE
        </div>

        <div class="hero-title" style="font-size:45px;">
            Understand Any Video
        </div>

        <div class="hero-subtitle">
            Paste a YouTube URL and get an AI-powered
            learning report in seconds.
        </div>
    </div>
    """)


    url = st.text_input(
        "🔗 YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=..."
    )


    analyze = st.button(
        "✨ Analyze Video",
        use_container_width=True
    )


    if analyze:

        if not url.strip():

            st.warning("⚠️ Please enter a YouTube URL.")
            st.stop()


        video_id = extract_video_id(url)


        if not video_id:

            st.error("❌ Invalid YouTube URL.")
            st.stop()


        with st.spinner("🔍 Fetching video information..."):

            video = get_video_info(url)

            transcript = get_transcript(video_id)


        if video is None or transcript is None:
            st.stop()


        # ----------------------------------------------------
        # VIDEO OVERVIEW
        # ----------------------------------------------------

        st.html("""
        <div class="section-title">
            🎬 Video Overview
        </div>
        """)


        image_col, info_col = st.columns([1, 1.5])


        with image_col:

            if video["thumbnail"]:

                st.image(
                    video["thumbnail"],
                    use_container_width=True
                )


        with info_col:

            safe_title = video["title"].replace(
                "<",
                "&lt;"
            ).replace(
                ">",
                "&gt;"
            )

            safe_channel = video["channel"].replace(
                "<",
                "&lt;"
            ).replace(
                ">",
                "&gt;"
            )


            st.html(
                f"""
                <div class="video-info">
                    <div class="video-title">
                        {safe_title}
                    </div>

                    <div class="channel">
                        📺 {safe_channel}
                    </div>

                    <br>

                    <div style="color:#7f8ba2;">
                        🎥 YouTube Video
                    </div>
                </div>
                """
            )


        # ----------------------------------------------------
        # COMMENTS
        # ----------------------------------------------------

        comments = get_comments(video_id)


        # ----------------------------------------------------
        # STATISTICS
        # ----------------------------------------------------

        st.html("""
        <div class="section-title">
            📊 Video Statistics
        </div>
        """)


        stat1, stat2, stat3, stat4 = st.columns(4)


        with stat1:

            st.html(
                f"""
                <div class="stat-card">
                    <div class="stat-number">
                        👁️ {format_number(video["views"])}
                    </div>

                    <div class="stat-label">
                        Views
                    </div>
                </div>
                """
            )


        with stat2:

            st.html(
                f"""
                <div class="stat-card">
                    <div class="stat-number">
                        👍 {format_number(video["likes"])}
                    </div>

                    <div class="stat-label">
                        Likes
                    </div>
                </div>
                """
            )


        with stat3:

            st.html(
                f"""
                <div class="stat-card">
                    <div class="stat-number">
                        ⏱️ {format_duration(video["duration"])}
                    </div>

                    <div class="stat-label">
                        Duration
                    </div>
                </div>
                """
            )


        with stat4:

            if youtube_key:
                comment_number = len(comments)
            else:
                comment_number = "N/A"


            st.html(
                f"""
                <div class="stat-card">
                    <div class="stat-number">
                        💬 {comment_number}
                    </div>

                    <div class="stat-label">
                        Comments Analyzed
                    </div>
                </div>
                """
            )


        # ----------------------------------------------------
        # AI REPORT
        # ----------------------------------------------------

        st.html("""
        <div class="section-title">
            🧠 AI Learning Report
        </div>
        """)


        with st.spinner("🤖 AI is analyzing the transcript..."):

            summary = summarize(transcript)


        st.markdown(summary)


        # ----------------------------------------------------
        # POSITIVE COMMENTS
        # ----------------------------------------------------

        st.html("""
        <div class="section-title">
            💚 What Viewers Liked
        </div>
        """)


        if not youtube_key:

            st.info(
                "💡 Add a youtube-api.key file to enable "
                "viewer comment analysis."
            )


        elif not comments:

            st.info(
                "No public comments were available for this video."
            )


        else:

            with st.spinner(
                "💚 Analyzing viewer reactions..."
            ):

                positive_comments = find_positive_comments(
                    comments
                )


            if positive_comments:

                for comment in positive_comments:

                    safe_comment = (
                        comment
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                    )


                    st.html(
                        f"""
                        <div class="comment-card">
                            <div class="positive-label">
                                💚 Positive Viewer Reaction
                            </div>

                            {safe_comment}
                        </div>
                        """
                    )

            else:

                st.info(
                    "No clearly positive comments were detected."
                )


        st.html("""
        <div class="footer-text">
            🤖 AI-generated insights • YouTube data •
            Built with Python & Streamlit
        </div>
        """)