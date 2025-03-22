import os
import yt_dlp
from io import BytesIO
from flask import Flask, render_template, request, send_file, send_from_directory, jsonify
import re
import logging
import unicodedata
import shutil

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def check_ffmpeg():
    """Check if FFmpeg is available in the system."""
    return shutil.which('ffmpeg') is not None

def sanitize_filename(filename):
    """Sanitize the filename to remove invalid characters and normalize Unicode."""
    # Normalize Unicode characters
    filename = unicodedata.normalize('NFKD', filename)
    # Remove invalid characters but keep Unicode
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces and special characters with underscores
    filename = re.sub(r'[\s\-]+', '_', filename)
    # Remove any non-ASCII characters
    filename = re.sub(r'[^\x00-\x7F]+', '', filename)
    # Remove consecutive underscores
    filename = re.sub(r'_+', '_', filename)
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    # Limit length
    return filename[:200] if filename else 'media'

@app.route("/")
def index():
    """Render the homepage with the form for the user to input the YouTube URL."""
    return render_template("index.html")

@app.route("/favicon.ico")
def favicon():
    """Return the favicon for the app."""
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )

@app.route("/download", methods=["POST"])
def download_media():
    """Handle the YouTube URL submission, download media, and send it back as a file."""
    try:
        url = request.form.get("youtube_url")
        format_type = request.form.get("format", "audio")  # Default to audio if not specified
        
        if not url:
            return jsonify({"error": "No URL provided"}), 400

        logger.info(f"Processing URL: {url} for format: {format_type}")

        # Create a timestamp-based unique identifier
        import time
        timestamp = int(time.time())

        # Configure yt-dlp options based on format type
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
        }

        if format_type == "audio":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'outtmpl': {
                    'default': f'downloads/%(title)s_{timestamp}.%(ext)s'
                }
            })
        else:  # video
            # Check if FFmpeg is available
            has_ffmpeg = check_ffmpeg()
            logger.info(f"FFmpeg available: {has_ffmpeg}")

            if has_ffmpeg:
                # If FFmpeg is available, use simpler format selection with better compatibility
                ydl_opts.update({
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/mp4',
                    'merge_output_format': 'mp4',
                    'postprocessor_args': {
                        'ffmpeg': [
                            '-c:v', 'copy',       # Just copy the video stream
                            '-c:a', 'aac',        # Convert audio to AAC
                            '-b:a', '192k',       # Audio bitrate
                            '-movflags', '+faststart'
                        ],
                    },
                    'prefer_ffmpeg': True,
                    # Add encoding options
                    'writethumbnail': False,
                    'ignoreerrors': True,
                    'no_color': True,
                    'encoding': 'utf-8',
                    'windowsfilenames': True,     # Use Windows-compatible filenames
                    'restrictfilenames': True,    # Restrict filenames to ASCII characters
                    'nooverwrites': True,        # Don't overwrite files
                })
            else:
                # If FFmpeg is not available, get the best quality combined format
                ydl_opts.update({
                    'format': 'best[ext=mp4]/mp4',
                    'ignoreerrors': True,
                    'no_color': True,
                    'encoding': 'utf-8',
                    'windowsfilenames': True,
                    'restrictfilenames': True,
                    'nooverwrites': True
                })
            
            # Update output template to be more restrictive
            ydl_opts['outtmpl'] = {
                'default': f'downloads/video_{timestamp}.%(ext)s'  # Simplified filename
            }

        # Get video info first
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Extract video information
                logger.info("Extracting video information...")
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    logger.error("Could not fetch video information")
                    return jsonify({"error": "Could not fetch video information"}), 400

                logger.debug(f"Video info: {info}")

                # Get video title and sanitize it more strictly
                title = None
                if isinstance(info, dict):
                    title = info.get('title', '').encode('ascii', 'ignore').decode()  # Force ASCII
                    logger.info(f"Found title: {title}")
                
                if not title or not isinstance(title, str):
                    title = f'video_{timestamp}'
                    logger.warning(f"Using default title: {title}")

                safe_title = sanitize_filename(title)
                logger.info(f"Sanitized title: {safe_title}")

                # Download the file
                logger.info("Starting download...")
                try:
                    ydl.download([url])
                except Exception as e:
                    logger.error(f"Download failed: {str(e)}")
                    return jsonify({"error": "Failed to download video. Please try a different format or video."}), 400
                
                # Find the downloaded file using timestamp
                downloaded_file = None
                expected_prefix = f"{safe_title}_{timestamp}"
                logger.info(f"Looking for file with prefix: {expected_prefix}")
                
                for file in os.listdir('downloads'):
                    logger.debug(f"Checking file: {file}")
                    if str(timestamp) in file:
                        downloaded_file = os.path.join('downloads', file)
                        logger.info(f"Found downloaded file: {downloaded_file}")
                        break

                if not downloaded_file or not os.path.exists(downloaded_file):
                    logger.error("Failed to find downloaded file")
                    return jsonify({"error": "Failed to download media"}), 400
                
                # Get the file extension
                _, ext = os.path.splitext(downloaded_file)
                ext = ext.lstrip('.')  # Remove the leading dot
                logger.info(f"File extension: {ext}")
                
                # Read the file and send it
                with open(downloaded_file, 'rb') as f:
                    media_data = f.read()
                
                # Clean up the file
                try:
                    os.remove(downloaded_file)
                    logger.info("Temporary file removed successfully")
                except Exception as e:
                    logger.error(f"Error removing temporary file: {e}")
                
                # Create response
                buffer = BytesIO(media_data)
                buffer.seek(0)
                
                # Use a simple filename for download
                download_filename = f"{safe_title}.{ext}"
                logger.info(f"Sending file as: {download_filename}")
                
                mime_type = 'audio/mp3' if format_type == 'audio' else 'video/mp4'
                return send_file(
                    buffer,
                    as_attachment=True,
                    download_name=download_filename,
                    mimetype=mime_type
                )
                
            except Exception as e:
                logger.error(f"Download error: {str(e)}", exc_info=True)
                return jsonify({"error": f"Error downloading media: {str(e)}"}), 400

    except Exception as e:
        logger.error(f"General error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    # Create necessary directories
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Set Flask logger to debug
    app.logger.setLevel(logging.DEBUG)
    
    # Check FFmpeg availability at startup
    has_ffmpeg = check_ffmpeg()
    logger.info(f"FFmpeg available: {has_ffmpeg}")
    if not has_ffmpeg:
        logger.warning("FFmpeg is not installed. Video quality may be limited. To get best quality, please install FFmpeg.")
    
    app.run(debug=True)
