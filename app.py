from flask import Flask, request, send_file, render_template_string
from pypdf import PdfReader
from gtts import gTTS
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FILE = "static/audiobook.mp3"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------- HTML FRONTEND ----------
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>PDF to Audiobook</title>
</head>
<body style="font-family: Arial; padding: 40px;">

    <h1 PDF to Audio-Book</h1>

    <form action="/upload" method="POST" enctype="multipart/form-data">
        <input type="file" name="file" accept=".pdf" required>
        <button type="submit">Convert</button>
    </form>

</body>
</html>
"""


# ---------- ROUTES ----------
@app.route("/")
def home():
    return render_template_string(HTML)


def extract_text(pdf_path):
    reader = PdfReader(pdf_path)

    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def chunk_text(text, max_chars=3000):
    chunks = []
    while len(text) > max_chars:
        split_point = text.rfind(" ", 0, max_chars)
        if split_point == -1:
            split_point = max_chars

        chunks.append(text[:split_point])
        text = text[split_point:]

    chunks.append(text)
    return chunks


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]

    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    # Extract text
    text = extract_text(pdf_path)

    if not text.strip():
        return "No readable text found in PDF."

    chunks = chunk_text(text)

    audio_chunks = []

    # Generate audio chunks
    for i, chunk in enumerate(chunks):
        tts = gTTS(text=chunk, lang="en")

        chunk_file = f"{UPLOAD_FOLDER}/chunk_{i}.mp3"
        tts.save(chunk_file)

        audio_chunks.append(chunk_file)

    # Combine audio (simple binary merge)
    with open(OUTPUT_FILE, "wb") as outfile:
        for fpath in audio_chunks:
            with open(fpath, "rb") as f:
                outfile.write(f.read())

    # Instead of download → show player page
    return f"""
    <h2>🎧 Your Audiobook is Ready</h2>

    <audio controls style="width: 100%;">
        <source src="/static/audiobook.mp3" type="audio/mpeg">
        Your browser does not support audio playback.
    </audio>

    <br><br>
    <a href="/">⬅ Upload another file</a>
    """

if __name__ == "__main__":
    app.run(debug=True)

'''
st.title("PDF to Audio-Book")

uploaded_file = st.file_uploader(
    "Upload a PDF",
    type="pdf"
)

if uploaded_file is not None:
    pdf_reader = PdfReader(uploaded_file)

    for page_num, page in enumerate(pdf_reader.pages):
        text = page.extract_text()
'''
