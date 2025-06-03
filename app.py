import os
from flask import Flask, request, render_template, send_file
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# These paths work in the Docker container
POPPLER_PATH = "/usr/bin"
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def preprocess(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return thresh

@app.route('/', methods=['GET', 'POST'])
def upload_pdf():
    if request.method == 'POST':
        file = request.files['pdf']
        if file:
            pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(pdf_path)

            pages = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
            full_text = ""

            for page in pages:
                processed = preprocess(page)
                text = pytesseract.image_to_string(processed, lang='eng+ara')  # example
                full_text += text + "\n\n"

            output_path = os.path.join(UPLOAD_FOLDER, 'output.txt')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_text)

            return send_file(output_path, as_attachment=True)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
