from pytube import YouTube
import urllib.request
import urllib.error
import ssl

def on_progress(stream, chunk, bytes_remaining):
    """Callback function to display download progress."""
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100
    print(f"Download progress: {percentage:.2f}%")

def create_context():
    """Create an SSL context that ignores certificate validation."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def download_audio():
    """Test function to download audio from a YouTube video."""
    try:
        # Test URL - Feel free to change this to any YouTube video URL
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        print(f"Attempting to download from: {url}")

        # Configure custom opener with headers and SSL context
        ctx = create_context()
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'),
            ('Accept-Language', 'en-US,en;q=0.9'),
            ('Accept-Encoding', 'gzip, deflate, br'),
            ('Connection', 'keep-alive'),
            ('Upgrade-Insecure-Requests', '1'),
            ('Sec-Fetch-Site', 'none'),
            ('Sec-Fetch-Mode', 'navigate'),
            ('Sec-Fetch-User', '?1'),
            ('Sec-Fetch-Dest', 'document'),
            ('sec-ch-ua', '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"'),
            ('sec-ch-ua-mobile', '?0'),
            ('sec-ch-ua-platform', '"Windows"')
        ]
        urllib.request.install_opener(opener)

        # Create YouTube object with specific configuration
        yt = YouTube(
            url,
            on_progress_callback=on_progress,
            use_oauth=False,
            allow_oauth_cache=False
        )

        # Force initialization of video information
        try:
            title = yt.title  # This will force video info to be loaded
            print(f"\nVideo Title: {title}")
            print(f"Video Length: {yt.length} seconds")
            print(f"View Count: {yt.views}")
        except Exception as e:
            print(f"Error getting video info: {str(e)}")
            return

        # Get available streams
        print("\nAvailable audio streams:")
        audio_streams = yt.streams.filter(only_audio=True)
        
        if not audio_streams:
            print("No audio streams found!")
            return
            
        for stream in audio_streams:
            print(f"Stream: {stream}")

        # Get the highest quality audio stream
        audio_stream = audio_streams.order_by('abr').desc().first()
        if not audio_stream:
            print("Could not find suitable audio stream!")
            return
            
        print(f"\nSelected stream: {audio_stream}")

        # Download the audio
        print("\nStarting download...")
        output_file = audio_stream.download(
            output_path="downloads",
            filename=f"audio.mp3"  # Using a simple filename to avoid encoding issues
        )
        print(f"\nDownload completed! File saved as: {output_file}")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print(f"Error type: {type(e)}")
        if isinstance(e, urllib.error.HTTPError):
            print(f"HTTP Error Code: {e.code}")
            print(f"HTTP Error Reason: {e.reason}")
            print(f"HTTP Error Headers: {e.headers}")

if __name__ == "__main__":
    # Create downloads directory if it doesn't exist
    import os
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    print("Starting pytube test...")
    download_audio() 