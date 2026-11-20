# 🎥 AI YouTube Video Summarizer

## 📌 Project Overview

The AI YouTube Video Summarizer is a web application built using **Python**, **Streamlit**, and **Groq AI**. It accepts a YouTube video URL, extracts the video's transcript, and uses a Large Language Model (LLM) to generate a structured summary.

This application helps users quickly understand the key concepts of long YouTube videos without watching the entire video.

---

## ✨ Features

- 🔗 Accepts any valid YouTube video URL
- 📄 Extracts the video transcript automatically
- 🤖 Generates an AI-powered summary using Groq LLM
- 📌 Displays:
  - Video Title
  - Summary
  - Five Key Points
  - Three Important Takeaways
  - Important Keywords
  - Target Audience
  - Difficulty Level
  - Suggested Next Learning Steps
- 🌐 Simple and user-friendly Streamlit interface

---

## 🛠️ Technologies Used

- Python
- Streamlit
- Groq API
- YouTube Transcript API
- yt-dlp
- Regular Expressions (Regex)

---

## 📂 Project Structure

```
youtube-video-summarizer/
│
├── app.py
├── groq-api.key
├── requirements.txt
├── README.md
└── output/
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/youtube-video-summarizer.git
```

### 2. Navigate to the project folder

```bash
cd youtube-video-summarizer
```

### 3. Install the required packages

```bash
pip install -r requirements.txt
```

### 4. Add your Groq API Key

Create a file named:

```
groq-api.key
```

Paste your Groq API key into this file.

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at:

```
http://localhost:8501
```

---

## 📷 Sample Workflow

1. Enter a YouTube video URL.
2. Click **Generate Summary**.
3. The application extracts the transcript.
4. Groq AI generates a structured summary.
5. The summary is displayed on the webpage.

---

## 📸 Sample Output

The application displays:

- 🎬 Video Title
- 📝 Summary
- 📌 Five Key Points
- ✅ Three Important Takeaways
- 🏷️ Important Keywords
- 👥 Target Audience
- 📈 Difficulty Level
- 🚀 Suggested Next Learning Steps

---

## ⚠️ Limitations

- Some YouTube videos may not have transcripts available.
- Very long videos may exceed the free Groq API token limit.
- Internet connection is required.

---

## 🚀 Future Enhancements

- Download summary as PDF
- Download summary as Markdown
- Generate quiz questions
- Generate interview questions
- Translate summaries into multiple languages
- Chat with the video
- Improved UI design

---

## 👩‍💻 Author

**Amrutha**

AI YouTube Video Summarizer Project

Built using **Python**, **Streamlit**, and **Groq AI**.