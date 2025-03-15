#(base) PS D:\FACULTATE\hackathon\ITfest\web-app> cd d:/FACULTATE/hackathon/ITfest/web-app/my_project
#(base) PS D:\FACULTATE\hackathon\ITfest\web-app\my_project> python firstPage.py

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
STATIC_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('index.html')

# Audio Upload Route
@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and file.filename.endswith(('.wav', '.mp3')):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename})
    return jsonify({'error': 'Invalid file format'})

# JSON Upload & Visualization Route
@app.route('/upload_json', methods=['POST'])
def upload_json():
    if 'jsonfile' not in request.files:
        return jsonify({'error': 'No JSON file part'})
    file = request.files['jsonfile']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and file.filename.endswith('.json'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(DATA_FOLDER, filename)
        file.save(filepath)
        
        # Read JSON and generate charts
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract Data
        labels = [item['disease_titles'][0] for item in data]
        values = [item['percent'] for item in data]
        df = pd.DataFrame({'Disease': labels, 'Percentage': values})
        
        sns.set_theme(style="whitegrid")
        
        # Pie Chart
        plt.figure(figsize=(6, 6))
        plt.pie(values, labels=labels, autopct='%1.1f%%', colors=sns.color_palette("pastel"))
        plt.title('Disease Distribution')
        pie_chart_path = os.path.join(STATIC_FOLDER, 'pie_chart.png')
        plt.savefig(pie_chart_path, bbox_inches='tight')
        plt.close()
        
        # Horizontal Bar Chart
        plt.figure(figsize=(8, 5))
        sns.barplot(x=values, y=labels, palette="Blues_r")
        plt.xlabel('Percentage')
        plt.ylabel('Disease')
        plt.title('Disease Percentage (Bar Chart)')
        bar_chart_path = os.path.join(STATIC_FOLDER, 'bar_chart.png')
        plt.savefig(bar_chart_path, bbox_inches='tight')
        plt.close()
        
        # Line Chart
        plt.figure(figsize=(8, 5))
        sns.lineplot(x=labels, y=values, marker='o', linestyle='-', color='b')
        plt.xlabel('Disease')
        plt.ylabel('Percentage')
        plt.title('Disease Percentage Trend')
        line_chart_path = os.path.join(STATIC_FOLDER, 'line_chart.png')
        plt.savefig(line_chart_path, bbox_inches='tight')
        plt.close()
        
        return jsonify({'message': 'JSON processed successfully', 'pie_chart': pie_chart_path, 'bar_chart': bar_chart_path, 'line_chart': line_chart_path})
    return jsonify({'error': 'Invalid file format'})

if __name__ == '__main__':
    app.run(debug=True)
