from flask import Flask, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
app = Flask(__name__)

def extract_code_only(response_text):
    """
    Extract clean Python code from markdown-style response.
    Removes triple backticks and optional 'python' tag.
    """
    if "```" in response_text:
        code = response_text.split("```")[1]
        code = code.replace("python", "").strip()
    else:
        code = response_text.strip()
    return code

def auto_patch_manim_code(code):
    """
    Ensures required Manim imports are present.
    """
    if "from manim import" not in code:
        code = "from manim import *\n\n" + code
    return code

@app.route('/', methods=['POST'])
def home():
    data = request.get_json()
    query = data.get('query')

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "tngtech/deepseek-r1t2-chimera:free",
                "messages": [
                    {
                        "role": "user",
                      "content": f"""
You are a highly experienced Manim Community Edition (v0.19+) developer.

Given the following user request, generate a **single, complete, executable Python Manim script**.

### INSTRUCTIONS:
- Output **only valid Python code**, no markdown, no text.
- Always include required imports, like `from manim import *`.
- If using constants like `DEG`, `PI`, or `TAU`, **import or define them explicitly** (e.g., `DEG = PI / 180`).
- Avoid guessing logic using things like `str(obj.color)` — use direct object references (e.g., known variable names).
- Ensure every variable is defined before it is used.
- The final script should run successfully with: `manim -pql file.py SceneName`.

### USER REQUEST:
{query}
"""

                    }
                ],
            })
        )

        response.raise_for_status()
        api_response = response.json()
        raw_code = api_response['choices'][0]['message']['content']

        clean_code = extract_code_only(raw_code)
        clean_code = auto_patch_manim_code(clean_code)

        output_filename = "manim_code.py"
        with open(output_filename, 'w') as f:
            f.write(clean_code)

        return jsonify({
            "status": "success",
            "message": f"Manim code saved to {output_filename}",
            "file": output_filename
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    except KeyError as e:
        return jsonify({
            "status": "error",
            "message": f"Unexpected API response format: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
