from flask import Flask, render_template, request
import requests
from datetime import datetime
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MEME_API_URL="https://api.memegen.link"

def get_templates():
    try:
        response = requests.get(
            f"{MEME_API_URL}/templates",
        )
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch templates: {str(e)}")
        return []
    except ValueError as e:  
        logger.error(f"Invalid response from API: {str(e)}")
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

@app.route("/generate/<template_id>", methods=["GET", "POST"])
def generate(template_id):
    meme_url = None
    templates = get_templates()  
    
    if request.method == "POST":
        top = request.form.get("top_text", "").strip()
        bottom = request.form.get("bottom_text", "").strip()

        top_encoded = format_text(top)
        bottom_encoded = format_text(bottom)

        meme_url = (
            f"{MEME_API_URL}/images/{template_id}/"
            f"{top_encoded}/{bottom_encoded}.png"
        )

    return render_template(
        "generate.html",
        template_id=template_id,
        meme_url=meme_url,
        timestamp=int(datetime.now().timestamp()),
        templates=templates  
    )

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True)