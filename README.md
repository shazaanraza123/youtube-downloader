# YouTube Downloader

A web application that allows you to download YouTube videos as MP4 or MP3 files with high quality.

## Features

- Download YouTube videos in high quality MP4 format
- Download YouTube audio in MP3 format
- Modern dark-themed UI
- Easy to use interface
- Supports high resolution videos (up to 4K)
- High quality audio (up to 320kbps)

## Requirements

- Python 3.8 or higher
- FFmpeg (for high quality video downloads)
- Requirements listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/youtube-downloader.git
cd youtube-downloader
```

2. Install FFmpeg:
- Windows: Download from https://github.com/BtbN/FFmpeg-Builds/releases
- Linux: `sudo apt-get install ffmpeg`
- Mac: `brew install ffmpeg`

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

## Usage

1. Open the application in your web browser (default: http://localhost:5000)
2. Paste a YouTube URL into the input field
3. Select your desired format (MP4 or MP3)
4. Click "Download" and wait for the process to complete
5. The file will automatically download when ready

## Deployment

The application is deployed on Netlify and can be accessed at [your-app-url].

## Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for personal use only. Please respect YouTube's terms of service and content creators' rights. 