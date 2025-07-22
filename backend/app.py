from flask import Flask, request, jsonify, send_file
import requests
import json
import os
import subprocess
import re
import tempfile
import uuid
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

app = Flask(__name__)

# Create directories
WORK_DIR = Path("/app/work")
OUTPUT_DIR = Path("/app/output")
WORK_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

def extract_code_only(response_text):
    if "```" in response_text:
        parts = response_text.split("```")
        for part in parts[1::2]:  # Get odd indices (code blocks)
            code = part.replace("python", "").strip()
            if code and "class" in code and "Scene" in code:
                return code
    return response_text.strip()

def auto_patch_manim_code(code):
    if "from manim import" not in code and "import manim" not in code:
        code = "from manim import *\n\n" + code
    return code

def extract_scene_name(code):
    match = re.search(r'class\s+(\w+)\s*\(Scene\):', code)
    return match.group(1) if match else "MainScene"

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Manim API is running"}), 200

@app.route('/render', methods=['POST'])
def render_animation():
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Missing 'query' in request body"}), 400
        
        query = data.get('query')
        job_id = str(uuid.uuid4())[:8]
        
        print(f"[{job_id}] Processing query: {query}")
        
        # Call OpenRouter API
        print(f"[{job_id}] Calling OpenRouter API...")
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "moonshotai/kimi-k2:free",
                "messages": [{
                    "role": "user",
                    "content": f"""
Create a complete Manim Community Edition script for: {query}

Requirements:
- Use only "from manim import *"
- Create a single Scene class
- Use only basic Manim objects (Square, Circle, Text, etc.)
- Keep animations simple (Create, FadeIn, FadeOut, Transform)
- No external dependencies
- No deprecated methods
- Output ONLY Python code, no explanations

Example format:
from manim import *

class MainScene(Scene):
    def construct(self):
        # Your animation code here
        self.wait()
"""
                }]
            },
            timeout=30
        )
        
        if response.status_code != 200:
            return jsonify({"error": f"API error: {response.status_code}"}), 500
            
        api_response = response.json()
        raw_code = api_response['choices'][0]['message']['content']
        
        # Clean and prepare code
        clean_code = extract_code_only(raw_code)
        clean_code = auto_patch_manim_code(clean_code)
        scene_name = extract_scene_name(clean_code)
        
        print(f"[{job_id}] Scene name: {scene_name}")
        
        # Create temporary files
        work_path = WORK_DIR / f"scene_{job_id}.py"
        
        with open(work_path, 'w') as f:
            f.write(clean_code)
        
        print(f"[{job_id}] Running Manim...")
        
        # Fixed command - use proper Manim command structure
        cmd = [
            "timeout", "120",
            "manim", "render",
            str(work_path),
            scene_name,
            "-q", "m",  # Medium quality (separate flags)
            "--format", "mp4",
            "--output_file", f"{job_id}.mp4"
        ]
        
        result = subprocess.run(
            cmd,
            cwd=str(OUTPUT_DIR),
            capture_output=True,
            text=True,
            timeout=130  # Slightly longer than the timeout command
        )
        
        # Clean up source file
        work_path.unlink(missing_ok=True)
        
        if result.returncode != 0:
            print(f"[{job_id}] Manim error: {result.stderr}")
            return jsonify({
                "error": "Manim rendering failed",
                "details": result.stderr,
                "code": clean_code
            }), 500
        
        # Find output file
        output_file = OUTPUT_DIR / f"{job_id}.mp4"
        if not output_file.exists():
            # Try to find any mp4 file created
            mp4_files = list(OUTPUT_DIR.glob("*.mp4"))
            if mp4_files:
                output_file = mp4_files[-1]  # Get the most recent one
            else:
                return jsonify({"error": "No output file generated"}), 500
        
        print(f"[{job_id}] Success! Output: {output_file}")
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "download_url": f"/download/{job_id}",
            "message": "Animation rendered successfully"
        }), 200
        
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Rendering timeout (2 minutes)"}), 408
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/download/<job_id>', methods=['GET'])
def download_file(job_id):
    try:
        output_file = OUTPUT_DIR / f"{job_id}.mp4"
        if output_file.exists():
            return send_file(str(output_file), as_attachment=True)
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Manim API server...")
    print(f"Work directory: {WORK_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    app.run(host='0.0.0.0', port=5000, debug=False)