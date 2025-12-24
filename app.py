from flask import Flask, render_template, request, jsonify, send_file
import configparser
import os
from infra import other_destination
from services import document_parsing
from services.page_validation import PageClassificator

config = configparser.ConfigParser()
config.read(f'settings.ini')

TEMP_FOLDER = config['ImagePath']['temp']
PDF_FOLDER = config['ImagePath']['pdf']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = PDF_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def root():
    return render_template('index.html', title='Главная')


@app.route('/waybill/<path:image_path>')
def get_temp_image(image_path):
    """Безопасный endpoint для файлов из временной папки"""
    # Заменяем слэши для Windows/Linux совместимости
    safe_path = os.path.join(TEMP_FOLDER, image_path.replace('/', os.sep))

    # Приводим к абсолютному пути для проверки безопасности
    abs_base = os.path.abspath(TEMP_FOLDER)
    abs_path = os.path.abspath(safe_path)

    # Проверяем, что путь внутри разрешенной директории
    if not abs_path.startswith(abs_base):
        return "Forbidden", 403

    if not os.path.exists(abs_path):
        return "Not found", 404

    return send_file(abs_path, mimetype='image/png')


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
        else:
            return jsonify({'error': 'Do not allowed file type'}), 400


@app.route('/api/recognize', methods=['POST'])
def api_recognize():
    # Проверяем наличие файла в запросе
    if 'uploaded_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['uploaded_file']

    # Проверяем, выбрал ли пользователь файл
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Проверяем, что файл существует
    if not file:
        return jsonify({'error': 'File is empty'}), 400

    # Проверяем допустимый тип файла
    if not other_destination.allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Only PDF files are accepted.'}), 400

    try:
        # Сохраняем файл
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            # Обрабатываем документ
            doc_parser = document_parsing.DocumentParser(file_path)
            result = doc_parser.get_text_values()

            # Возвращаем успешный результат
            return jsonify(result), 200

        except Exception as e:
            # Удаляем временный файл в случае ошибки
            if os.path.exists(file_path):
                os.remove(file_path)

            app.logger.error(f"Error processing document: {str(e)}")
            return jsonify({
                'status': 'error',
                'error': f'Error processing document: {str(e)}'
            }), 500

    except Exception as e:
        app.logger.error(f"Error in API endpoint: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': f'Internal server error: {str(e)}'
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=8080)
