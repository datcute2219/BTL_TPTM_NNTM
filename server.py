from flask import Flask, request, render_template_string, send_from_directory, jsonify
import datetime, os
import pytesseract
import cv2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ⚠️ Đường dẫn tới tesseract nếu cần (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ HÀM GỬI EMAIL
def send_email(subject, body):
    sender_email = "datlexuan36@gmail.com"       # ✅ Thay bằng email của bạn
    receiver_email = "datlexuan36@gmail.com"     # ✅ Email nhận (có thể giống sender)
    password = "qxhb jcku cjwi mkwj"             # ✅ Mật khẩu ứng dụng (App password 16 ký tự từ Google)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        print("[📧] Đã gửi email thành công.")
    except Exception as e:
        print(f"[⚠️] Gửi email thất bại: {e}")

# ✅ OCR ẢNH
def ocr_image(image_path):
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, config='--psm 6 digits')
        
        # Gửi email sau khi OCR xong
        now = datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')
        subject = "Cảnh báo chỉ số công tơ"
        body = f"Chỉ số đọc được: {text.strip()} kWh\nThời gian: {now}\n(Được gửi tự động từ ESP32-CAM OCR Server)"
        send_email(subject, body)

        return text.strip()
    except Exception as e:
        return f"OCR Error: {e}"

@app.route('/')
def index():
    latest = get_latest_image()
    timestamp = datetime.datetime.now().timestamp()
    ocr_result = ""
    if latest:
        img_path = os.path.join(UPLOAD_FOLDER, latest)
        ocr_result = ocr_image(img_path)

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESP32-CAM Live + Capture</title>
        <style>
            body { font-family: Arial; text-align: center; background: #f5f5f5; padding: 30px; }
            img { border: 3px solid #4CAF50; border-radius: 10px; margin-top: 20px; }
            button { padding: 10px 25px; font-size: 16px; background: #4CAF50; color: white; border: none; border-radius: 8px; cursor: pointer; }
            button:hover { background: #45a049; }
        </style>
    </head>
    <body>
        <h2>📸 ESP32-CAM OCR Server</h2>

        <h3>📡 Live stream từ ESP32-CAM:</h3>
        <img id="stream" src="http://192.168.130.59:81/stream" width="320" height="240">

        <br><br>
        <button onclick="capturePhoto()">📷 Chụp ảnh từ ESP32-CAM</button>

        <div id="latest">
            {% if latest %}
                <h3>🖼️ Ảnh mới nhất:</h3>
                <img src="/uploads/{{ latest }}?t={{ time }}" width="320">
                <h3>🔍 Kết quả OCR:</h3>
                <p style="font-size: 24px; color: #333;">{{ ocr_result }}</p>
            {% endif %}
        </div>

        <script>
            function capturePhoto() {
                fetch("/trigger", { method: "POST" })
                    .then(() => location.reload())
                    .catch(err => alert("❌ Lỗi khi gửi lệnh chụp ảnh"));
            }
        </script>
    </body>
    </html>
    """, latest=latest, time=timestamp, ocr_result=ocr_result)

@app.route('/trigger', methods=['POST'])
def trigger():
    import requests
    ESP32_CAPTURE_URL = "http://192.168.130.59/capture"
    try:
        print("[📡] Gửi lệnh chụp ảnh đến ESP32...")
        img_data = requests.get(ESP32_CAPTURE_URL, timeout=5).content
        filename = datetime.datetime.now().strftime("image_%Y%m%d_%H%M%S.jpg")
        with open(os.path.join(UPLOAD_FOLDER, filename), 'wb') as f:
            f.write(img_data)
        print("[✓] Đã lưu ảnh:", filename)
    except Exception as e:
        print("[✗] Lỗi khi chụp:", e)
    return jsonify({"status": "ok"})

@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

def get_latest_image():
    files = sorted(os.listdir(UPLOAD_FOLDER), reverse=True)
    for f in files:
        if f.endswith('.jpg'):
            return f
    return None

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

