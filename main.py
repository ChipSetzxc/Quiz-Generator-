from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename
import fitz  # for PDF
from docx import Document
import random

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs('uploads', exist_ok=True)

def extract_text(path):
    if path.lower().endswith('.pdf'):
        doc = fitz.open(path)
        return "\n".join(page.get_text() for page in doc)
    elif path.lower().endswith('.docx'):
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    return ""

def generate_questions(text, num):
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
    random.shuffle(sentences)
    questions = []
    for i, sent in enumerate(sentences[:num]):
        answer = sent.split()[0]
        opts = {answer}
        while len(opts) < 4:
            opts.add(random.choice(sentences).split()[0])
        opts = list(opts)
        random.shuffle(opts)
        questions.append({'q': sent[:60] + '...', 'opts': opts, 'ans': opts.index(answer)})
    return questions

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        f = request.files['file']
        n = int(request.form['num'])
        path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
        f.save(path)
        text = extract_text(path)
        qs = generate_questions(text, n)
        return render_template('quiz.html', qs=qs)
    return render_template('upload.html')

@app.route('/submit', methods=['POST'])
def submit():
    total = int(request.form['total'])
    score = sum(1 for i in range(total)
                if request.form.get(f'r{i}') == request.form.get(f'a{i}'))
    return render_template('result.html', score=score, total=total)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=81)
      
