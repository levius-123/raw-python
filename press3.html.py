import os
from flask import Flask, request, render_template_string, send_from_directory
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)

# Nastavení složky pro ukládání souborů
UPLOAD_FOLDER = '/mnt/konvert/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Povolené typy souborů
ALLOWED_EXTENSIONS = {'mp4', 'mp3', 'jpg', 'png', 'wav', 'jpeg', 'm4a', 'avi', 'mkv', 'flac', 'aiff', 'aac', 'raw'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        output_type = request.form['output_type']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Zde proběhne konverze na základě zvoleného typu (video, audio, fotka)
            if output_type == 'video':
                converted_file = convert_to_raw_video(file_path)
            elif output_type == 'audio':
                converted_file = convert_to_raw_audio(file_path)
            elif output_type == 'image':
                converted_file = convert_to_raw_image(file_path)

            if converted_file and os.path.exists(converted_file):
                return send_from_directory(app.config['UPLOAD_FOLDER'], os.path.basename(converted_file), as_attachment=True)
            else:
                return "Error in conversion.", 500

    return render_template_string(html_template)

def convert_to_raw_video(input_file):
    output_file = input_file.rsplit('.', 1)[0] + '_raw.mp4'
    # Použijeme h264 pro konverzi do MP4 s maximálním bitrate
    subprocess.run(['ffmpeg', '-i', input_file, '-c:v', 'libx264', '-preset', 'ultrafast', '-b:v', '100M', '-c:a', 'aac', '-b:a', '320k', output_file])
    return output_file if os.path.exists(output_file) else None

def convert_to_raw_audio(input_file):
    output_file = input_file.rsplit('.', 1)[0] + '_raw.wav'
    subprocess.run(['ffmpeg', '-i', input_file, '-c:a', 'pcm_s16le', output_file])
    return output_file if os.path.exists(output_file) else None

def convert_to_raw_image(input_file):
    output_file = input_file.rsplit('.', 1)[0] + '_raw.png'
    subprocess.run(['ffmpeg', '-i', input_file, '-q:v', '1', output_file])  # Nejlepší kvalita pro PNG
    return output_file if os.path.exists(output_file) else None

html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Converter</title>
    <script>
        function validateForm() {
            var fileInput = document.getElementById('file');
            var filePath = fileInput.value;
            var allowedExtensions = /(\.mp4|\.mp3|\.jpg|\.png|\.wav|\.jpeg|\.m4a|\.avi|\.mkv|\.flac|\.aiff|\.aac|\.raw)$/i;

            if (!allowedExtensions.exec(filePath)) {
                alert('Invalid file type! Please upload a valid file.');
                fileInput.value = '';
                return false;
            }

            var outputType = document.getElementById('output_type').value;
            if (!outputType) {
                alert('Please select an output type.');
                return false;
            }

            return true;
        }
    </script>
<style>
body{
font-family: Arial, Helvetica, sans-serif;
    background-color: white;
}
.formular{
background-color: red;
width: 30%;
}
.leva{
width: 30%;
    padding: 5px;
    border-radius: 10px;
}
.prava{
width: 60%;
    padding: 5px;
    border-radius: 10px;
}
.container{
display: flex;
    justify-content: space-between;
    padding: 20px;
    margin-top: 20px;
}

</style>
</head>
<body>
    <h1>Nahraj soubor pro konverzi do bezztrátového formátu</h1>

<div class="container">
<div class="leva">
</div>
<div class="formular">
    <form method="POST" enctype="multipart/form-data" onsubmit="return validateForm();">
        <label for="file">Vyber soubor:</label>
        <input type="file" name="file" id="file" required>
        <br><br>

        <label for="output_type">Vyber výstupní typ:</label>
        <select name="output_type" id="output_type" required>
            <option value="">--Vyber Možnost--</option>
            <option value="video">Video</option>
            <option value="audio">Zvuk</option>
            <option value="image">Obrázek</option>
        </select>
        <br><br>

        <input type="submit" value="Konvertovat">
    </form>
</div>
<div class="prava">
</div>
</div>

</body>
</html>
'''

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, host='0.0.0.0', port=5001)

