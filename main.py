from flask import Flask, request, jsonify
import yt_dlp
import subprocess
import os
import uuid

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "YouTube Shorts API is running!"})

@app.route('/download-and-cut', methods=['POST'])
def download_and_cut():
    data = request.json
    url = data.get('url')
    start_time = data.get('start_time', '0')
    duration = data.get('duration', '60')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    video_id = str(uuid.uuid4())
    output_path = f"/tmp/{video_id}.mp4"
    short_path = f"/tmp/{video_id}_short.mp4"
    
    try:
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': output_path,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        subprocess.run([
            'ffmpeg', '-i', output_path,
            '-ss', start_time,
            '-t', duration,
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            short_path
        ], check=True)
        
        os.remove(output_path)
        
        return jsonify({
            "success": True,
            "video_path": short_path,
            "video_id": video_id
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
