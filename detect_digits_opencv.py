import cv2

# Đọc ảnh đầu vào
image = cv2.imread("Công tơ điện 2.jpeg")
assert image is not None, "Không tìm thấy ảnh!"

# Chuyển sang grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Làm mượt và tăng độ tương phản
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
_, thresh = cv2.threshold(blurred, 120, 255, cv2.THRESH_BINARY_INV)

# Tìm contours (vùng đen trắng có thể chứa chữ số)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Lọc và vẽ khung quanh những vùng có kích thước hợp lý (giống như số)
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    if 20 < w < 80 and 30 < h < 100:  # Tùy chỉnh theo ảnh thực tế
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

# Hiển thị ảnh kết quả
cv2.imshow("Detected Digits Area", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
