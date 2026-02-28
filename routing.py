from flask import Flask, render_template
from flask_babel import Babel, gettext
import json
import os

backend_path = os.path.join(os.path.dirname(__file__), 'backend')
src_path = os.path.join(os.path.dirname(__file__), 'src')
skill_stats_path = os.path.join(backend_path, 'skill_stats.json')
img_path = os.path.join(src_path, 'img_site.json')

app = Flask(__name__)

LANGUAGES = {
   'en': 'English',
   'es': 'Español'
}

@app.route('/')
def stats():
    if not os.path.exists(skill_stats_path):
        return "Error, skills not found. Use skill script.", 500

    with open(skill_stats_path, 'r') as json_file:
        data = json.load(json_file)
    with open(img_path, 'r') as json_file:
        img_data = json.load(json_file)
    return render_template('stats.html', data=data, data2=img_data)

@app.route('/economy')
def economy():
    return render_template('economy.html')

@app.route('/login')
def login():
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
