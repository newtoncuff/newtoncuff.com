from flask import Flask, render_template, send_from_directory

app = Flask(__name__, static_folder="static", template_folder="templates", static_url_path='/resume/static')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
