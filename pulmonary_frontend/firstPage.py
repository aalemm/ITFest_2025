from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)
CORS(app)

# Folder setup
UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
STATIC_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Serve static files
@app.route('/static/<filename>')
def serve_static(filename):
    return send_from_directory(STATIC_FOLDER, filename)

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
        
        try:
            # Read JSON and generate charts
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract Data
            labels = [item['disease_titles'][0] for item in data]
            values = [item['percent'] for item in data]
            df = pd.DataFrame({'Disease': labels, 'Percentage': values})
            
            sns.set_theme(style="whitegrid")
            
            # Pie Chart
            plt.figure(figsize=(8, 8))
            plt.pie(values, labels=labels, autopct='%1.1f%%', colors=sns.color_palette("pastel"))
            plt.title('Disease Distribution')
            pie_chart_path = os.path.join(STATIC_FOLDER, 'pie_chart.png')
            plt.savefig(pie_chart_path, bbox_inches='tight')
            plt.close()
            
            # Horizontal Bar Chart
            plt.figure(figsize=(8, 8))
            sns.barplot(x=values, y=labels, palette="Blues_r")
            plt.xlabel('Percentage')
            plt.ylabel('Disease')
            plt.title('Disease Percentage (Bar Chart)')
            bar_chart_path = os.path.join(STATIC_FOLDER, 'bar_chart.png')
            plt.savefig(bar_chart_path, bbox_inches='tight')
            plt.close()
            
            # Line Chart
            plt.figure(figsize=(8, 8))
            sns.lineplot(x=labels, y=values, marker='o', linestyle='-', color='b')
            plt.xlabel('Disease')
            plt.ylabel('Percentage')
            plt.title('Disease Percentage Trend')
            line_chart_path = os.path.join(STATIC_FOLDER, 'line_chart.png')
            plt.savefig(line_chart_path, bbox_inches='tight')
            plt.close()
            
            # Return paths to the frontend
            return jsonify({
                'message': 'JSON processed successfully',
                'pie_chart': '/static/pie_chart.png',
                'bar_chart': '/static/bar_chart.png',
                'line_chart': '/static/line_chart.png'
            })
        except Exception as e:
            return jsonify({'error': f'Error processing JSON file: {str(e)}'})
    return jsonify({'error': 'Invalid file format'})

# Disease Information Route
WIKI_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"
DISEASES = ["URTI", "Pneumonia", "LRTI", "COPD", "Bronchiolitis", "Bronchiectasis", "Asthma"]

# Map disease abbreviations to their full Wikipedia page titles
DISEASE_MAPPING = {
    "LRTI": "Lower respiratory tract infection",
    "URTI": "Upper respiratory tract infection",
    "COPD": "Chronic obstructive pulmonary disease",
}

@app.route("/get_disease_info", methods=["GET"])
def get_disease_info():
    disease_info = {}
    for disease in DISEASES:
        try:
            # Use the mapped title if available, otherwise use the disease abbreviation
            title = DISEASE_MAPPING.get(disease, disease)
            response = requests.get(WIKI_API_URL.format(title), timeout=5)
            if response.status_code == 200:
                data = response.json()
                disease_info[disease] = data.get("extract", "No information available.")
            else:
                # Fallback description for LRTI
                if disease == "LRTI":
                    disease_info[disease] = (
                        "Lower respiratory tract infection (LRTI) is a type of infection that affects the "
                        "lower respiratory tract, including the lungs, bronchi, and trachea. Common causes "
                        "include bacteria and viruses."
                    )
                else:
                    disease_info[disease] = "No information available."
        except requests.exceptions.RequestException:
            disease_info[disease] = "Error fetching data."
    return jsonify(disease_info)

if __name__ == '__main__':
    app.run(debug=True)