from flask import Flask, send_from_directory, render_template_string
import inspect

app = Flask(__name__, static_folder='site', static_url_path='')

_script_injections = []
_button_callbacks = {}

# ---- JS Helper Builders ----
def alert(message):
    _script_injections.append(f'alert("{message}");')

def alert_input(prompt_msg="Enter something", alert_msg=""):
    _script_injections.append(f'''
    (function() {{
        let input = prompt("{prompt_msg}");
        alert("{alert_msg}\\nYou entered: " + input);
    }})();
    ''')

def getinput(input_id):
    return f'document.getElementById("{input_id}").value'

def setcontent(element_id, content):
    # Escape quotes
    safe_content = content.replace('"', '\\"').replace('\n', '\\n')
    _script_injections.append(f'document.getElementById("{element_id}").innerHTML = "{safe_content}";')

def defbutton(button_id, func):
    func_name = func.__name__
    _button_callbacks[button_id] = func
    _script_injections.append(f'''
    document.getElementById("{button_id}").addEventListener("click", async function() {{
        await fetch('/_pycall/{button_id}');
    }});
    ''')

# ---- Flask Routes ----
@app.route('/')
def root():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory(app.static_folder, path)

@app.route('/script.js')
def js_bundle():
    final_script = "window.onload = function() {\n" + "\n".join(_script_injections) + "\n};"
    return render_template_string(final_script), 200, {'Content-Type': 'application/javascript'}

@app.route('/_pycall/<button_id>')
def call_python(button_id):
    if button_id in _button_callbacks:
        _button_callbacks[button_id]()
    return "OK"

def run_app(port=5001):
    app.run(host='0.0.0.0', port=port)
    
