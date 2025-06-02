import requests

# Địa chỉ IP của camera ESP32
ESP32_URL = "http://192.168.130.59/capture"

# Địa chỉ server Flask
FLASK_URL = "http://192.168.130.82:5000/upload"  # Đổi đúng IP máy bạn

# Lấy ảnh từ ESP32
response = requests.get(ESP32_URL)
if response.status_code == 200:
    print("[✓] Đã chụp ảnh từ ESP32")

    # Gửi ảnh sang Flask server
    upload = requests.post(FLASK_URL, data=response.content)

    print("[→] Phản hồi từ server:", upload.text)
else:
    print("[✗] Không lấy được ảnh từ ESP32")
