import yt_dlp
import os

def download_audio():
    """Test function to download audio from a YouTube video using yt-dlp."""
    try:
        # Test URL
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        print(f"Attempting to download from: {url}")

        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'verbose': True
        }

        # Download the audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("\nGetting video information...")
            info = ydl.extract_info(url, download=False)
            print(f"\nVideo Title: {info.get('title', 'N/A')}")
            print(f"Duration: {info.get('duration', 'N/A')} seconds")
            
            print("\nStarting download...")
            ydl.download([url])
            
        print("\nDownload completed!")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    # Create downloads directory if it doesn't exist
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    print("Starting yt-dlp test...")
    download_audio() 