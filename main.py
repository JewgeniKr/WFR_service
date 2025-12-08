from flask import Flask, render_template, request, jsonify
import os


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
        # Сохраняем файл
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'path': file_path
        }), 200


if __name__ == '__main__':
    app.run(debug=True, port=9999)