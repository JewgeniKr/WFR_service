from flask import Flask, render_template, request, jsonify
import os
from infra import other_destination
from services import document_parsing
from services.page_validation import PageClassificator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'temp/pdf'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def root():
    return render_template('index.html', title='Главная')

@app.route('/recognize', methods=['POST'])
def recognize():
    if 'uploaded_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['uploaded_file']

    # Проверяем, выбрал ли пользователь файл
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        if other_destination.allowed_file(file.filename):
            # Сохраняем файл
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            doc_parser = document_parsing.DocumentParser(file_path)
            result = doc_parser.get_text_values()

            return jsonify(result), 200
        else: return jsonify({'error': 'Do not allowed file type'}), 400

@app.route('/api/recognize', methods=['POST'])
def api_recognize():
    pass


if __name__ == '__main__':
    app.run(debug=True, port=8080)