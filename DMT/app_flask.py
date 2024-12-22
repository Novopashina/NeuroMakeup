from flask import Flask, request, send_file
import sys
from main import DMT
from io import BytesIO

app = Flask(__name__)
neural_network = DMT()

@app.route('/process_images', methods=['POST'])
def process_images():
    # Получаем два изображения из POST-запроса
    image1 = request.files['image1']
    image2 = request.files['image2']

    # Преобразуем изображения в байтовые массивы
    image1_bytes = image1.read()
    image2_bytes = image2.read()

    # Обрабатываем изображения с помощью нейросети
    result_image_bytes = neural_network.pairwise(image1_bytes, image2_bytes)

    # Создаем файловый объект для отправки результата обратно клиенту
    result_file = BytesIO(result_image_bytes)

    # Отправляем файл обратно клиенту
    return send_file(result_file, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)
