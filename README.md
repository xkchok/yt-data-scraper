# YouTube Video Data Extractor

A Python script that extracts metadata and comments from YouTube videos using Playwright. The script supports processing multiple videos and saves the data in CSV format.

## Features

- Extracts video metadata:
  - Title
  - Description
  - Channel name
  - View count
  - Like count
  - Upload date
  - Duration
  - Keywords
  - And more...
- Captures top 5 comments for each video
- Supports processing multiple videos
- Tracks processed videos to avoid duplicates
- CSV output compatible with Excel

## Requirements

- Python 3.7+
- Playwright
- A stable internet connection

## Installation

1. Clone the repository:
```bash
git clone https://github.com/xkchok/yt-video-extractor.git
cd yt-video-extractor
```

2. Create and activate a virtual environment:
```bash
pip install uv
uv sync
```

3. Install dependencies:
```bash
uv add playwright
uvx playwright install chromium
```

## Usage

1. Add your video IDs to the `video_ids` list in `main.py`:
```python
video_ids = [
    'c2tuxS3Pcto',  # Example video ID
    'kxs9Su_mbpU',  # Another video ID
    'mvkbCZfwWzA'   # Another video ID
]
```

2. Run the script:
```bash
uv run main.py
```

The script will:
- Create a timestamped CSV file for the data
- Process each video and save its data immediately
- Track processed videos in `processed_videos.txt`
- Skip any previously processed videos

## Output Files

- `youtube_data_[timestamp].csv`: Contains the extracted data in CSV format
- `processed_videos.txt`: Tracks which videos have been processed and when

## Notes

- The script uses async/await for better performance
- Videos are processed one at a time to avoid rate limiting
- Failed videos won't be marked as processed
- CSV files use UTF-8 with BOM encoding for Excel compatibility
- All text fields are cleaned and formatted for CSV compatibility

## Error Handling

The script includes error handling for:
- Network issues
- Missing video elements
- Comment loading failures
- File writing errors

Failed videos will be reported but won't stop the script from processing other videos.

## Contributing

Feel free to submit issues and enhancement requests!
