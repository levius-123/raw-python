import os
from flask import Flask, request, render_template_string, send_from_directory
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)

# Nastavení složky pro ukládání souborů
UPLOAD_FOLDER = '/mnt/konvert/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Povolené typy souborů
ALLOWED_EXTENSIONS = {'mp4', 'mp3', 'jpg', 'png', 'wav', 'jpeg', 'm4a', 'avi', 'mkv', 'flac', 'aiff', 'aac'}

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
    output_file = input_file.rsplit('.', 1)[0] + '_raw.raw'  # Výstup jako nekomprimovaný RAW
    # Konverze do RAW: 16-bit PCM, 44.1 kHz, mono
    subprocess.run(['ffmpeg', '-i', input_file, '-f', 's16le', '-ar', '44100', '-ac', '2', output_file]) 
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
            var allowedExtensions = /(\.mp4|\.mp3|\.jpg|\.png|\.wav|\.jpeg|\.m4a|\.avi|\.mkv|\.flac|\.aiff|\.aac)$/i;

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

.navbar {
            overflow: hidden;
            background-color: #333;
        }

        .navbar a, .navbar span {
            float: left;
            font-size: 16px;
            color: white;
            text-align: center;
            padding: 14px 16px;
            text-decoration: none;
        }

        .navbar span {
            float: right;
        }

        .dropdown {
            float: left;
            overflow: hidden;
        }

        .dropdown .dropbtn {
            font-size: 16px;
            border: none;
            outline: none;
            color: white;
            padding: 14px 16px;
            background-color: inherit;
            font-family: inherit;
            margin: 0;
        }

        .navbar a:hover, .dropdown:hover .dropbtn {
            background-color: red;
        }

        .dropdown-content {
            display: none;
            position: absolute;
            background-color: #f9f9f9;
            min-width: 160px;
            box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
            z-index: 1;
        }

        .dropdown-content a {
            float: none;
            color: black;
            padding: 12px 16px;
            text-decoration: none;
            display: block;
            text-align: left;
        }

        .dropdown-content a:hover {
            background-color: #ddd;
        }

        .dropdown:hover .dropdown-content {
            display: block;
        }
</style>
</head>
<body>
<div class="navbar">
    <a href="http://10.0.0.3:88/index.html">DOMOVSKÁ STRÁNKA</a>
    <a href="http://10.0.0.3:88/novinky.html">NOVINKY</a>
    <a href="http://10.0.0.3:88/kontakt.html">KONTAKT</a>
    <div class="dropdown">
        <button class="dropbtn">VÝBĚR OBSAHU
            <i class="fa fa-caret-down"></i>
        </button>
        <div class="dropdown-content">
            <a href="http://10.0.0.3:88/krestan.html">KŘESŤANSKÁ HUDBA</a>
           <!--- <a href="ostatni.html">OSTATNÍ HUDBA</a>--->
            <a href="http://10.0.0.3:88/videa.html">VIDEA</a>
        </div>
    </div>
    <span>AUDIFY 0.1</span>
</div>
    <h1>Upload File for Conversion</h1>
    <form method="POST" enctype="multipart/form-data" onsubmit="return validateForm();">
        <label for="file">Choose file:</label>
        <input type="file" name="file" id="file" required>
        <br><br>

        <label for="output_type">Select Output Type:</label>
        <select name="output_type" id="output_type" required>
            <option value="">--Select Type--</option>
            <option value="video">Video</option>
            <option value="audio">Audio</option>
            <option value="image">Image</option>
        </select>
        <br><br>

        <input type="submit" value="Convert">
    </form>
</body>
</html>
'''

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, host='0.0.0.0', port=9002)
