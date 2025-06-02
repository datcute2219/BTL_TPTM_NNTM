from flask import Flask, request
import base64
import re

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    data = request.get_json()
    img_data = data['image']
    img_data = re.sub('^data:image/.+;base64,', '', img_data)
    
    with open('captured_image.png', 'wb') as f:
        f.write(base64.b64decode(img_data))
    
    return {'status': 'success'}

if __name__ == '__main__':
    app.run(debug=True)
