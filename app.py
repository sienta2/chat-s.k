from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'mp4', 'mp3', 'exe', 'txt'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# データを保存するリスト
saved_data = []

# 1日（24時間）経過したデータを削除する関数
def clean_expired_data():
    current_time = time.time()
    global saved_data
    saved_data = [item for item in saved_data if current_time - item['timestamp'] < 86400]  # 86400秒 = 24時間

# 許可された拡張子かどうか確認する関数
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/save', methods=['POST'])
def save_data():
    data = request.form.get('data')  # テキストデータ
    timestamp = time.time()  # 現在の時間（Unixタイムスタンプ）

    # ファイルのアップロード処理
    file_url = None
    file = request.files.get('file')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        file_url = f'/uploads/{filename}'  # アップロードしたファイルのURL

    # データを保存
    saved_data.append({"data": data, "timestamp": timestamp, "file_url": file_url})

    # 古いデータを削除
    clean_expired_data()

    return jsonify({'message': 'データが保存されました!', 'data': saved_data}), 200

@app.route('/get', methods=['GET'])
def get_data():
    clean_expired_data()  # データ取得時に期限切れデータを削除
    return jsonify({'data': saved_data}), 200

# ダウンロード用のルート
@app.route('/uploads/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
