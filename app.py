from flask import Flask, render_template, request 
from flask import send_file
import requests
from datetime import datetime
import logging
import io
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MEME_API_URL="https://api.memegen.link"

@app.route('/download_meme')
def download_meme():
    meme_url = request.args.get('url')
    if not meme_url:
        return "No URL provided", 400

    try:
        response = requests.get(meme_url)
        response.raise_for_status()
        return send_file(
            io.BytesIO(response.content),
            mimetype='image/png',
            as_attachment=True,
            download_name='meme.png'
        )
    except Exception as e:
        logger.error(f"Error downloading meme: {e}")
        return "Failed to download meme", 500
def get_templates():
    try:
        response = requests.get(f"{MEME_API_URL}/templates")
        response.raise_for_status()
        templates = response.json()

        # Add num_fields to each template based on example.text length
        for template in templates:
            try:
                template['num_fields'] = len(template.get("example", {}).get("text", []))
            except Exception:
                template['num_fields'] = 2  # fallback default

        return templates

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch templates: {str(e)}")
        return []


def format_text(text):
    """Format text for meme URL according to API requirements."""
    if not isinstance(text, str):
        return "_"
        
    replacements = [
        (' ', '_'),
        ('-', '--'),
        ('_', '__'),
        ('?', '~q'),
        ('%', '~p'),
        ('#', '~h'),
        ('/', '~s'),
        ('\\', '~b'),
        ('"', "''")
    ]
    
    formatted_text = text
    for old, new in replacements:
        formatted_text = formatted_text.replace(old, new)
        
    return formatted_text or "_"

@app.route("/")
def gallery():
    templates = get_templates()
    return render_template("gallery.html", templates=templates)

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    template_id = request.form.get('template') or request.args.get('template_id') or 'aag'
    meme_url = None
    templates = get_templates()

    # Lookup num_fields from template list
    num_fields = 2  # default
    for t in templates:
        if t["id"] == template_id:
            num_fields = t.get("num_fields", 2)
            break

    if request.method == "POST":
        texts = request.form.getlist("texts")
        formatted_lines = [format_text(t.strip()) for t in texts if t.strip()]
        meme_url = f"{MEME_API_URL}/images/{template_id}/" + "/".join(formatted_lines) + ".png"

    return render_template(
        "generate.html",
        template_id=template_id,
        meme_url=meme_url,
        timestamp=int(datetime.now().timestamp()),
        templates=templates,
        num_fields=num_fields
    )

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True)
