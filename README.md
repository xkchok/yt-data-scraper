# YouTube Data Scraper

A Python script collection that extracts data from YouTube using Playwright. The scripts support processing both videos and channels, saving data in CSV and JSON formats.

## Features

### Video Scraper (`video.py`)
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

### Channel Scraper (`channel.py`)
- Extracts channel information:
  - Channel description
  - Social media links (with resolved redirect URLs)
  - Location
  - Join date
  - Subscriber count
  - Video count
  - View count
- Saves data in JSON format

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

### Video Scraper
1. Add your video IDs to the `video_ids` list in `video.py`:
```python
video_ids = [
    'c2tuxS3Pcto',  # Example video ID
    'kxs9Su_mbpU',  # Another video ID
    'mvkbCZfwWzA'   # Another video ID
]
```

2. Run the script:
```bash
uv run video.py
```

The video scraper will:
- Create a timestamped CSV file for the data
- Process each video and save its data immediately
- Track processed videos in `processed_videos.txt`
- Skip any previously processed videos

### Channel Scraper
1. Edit the channel URLs in `channel.py`:
```python
channels = [
    "https://www.youtube.com/@The_FirstTake",
    # Add more channels here
]
```

2. Run the script:
```bash
uv run channel.py
```

The channel scraper will:
- Visit each channel's "About" page
- Extract available information
- Save the data to a JSON file

## Output Files

### Video Scraper
- `video_data_[timestamp].csv`: Contains the extracted video data in CSV format
- `processed_videos.txt`: Tracks which videos have been processed and when

### Channel Scraper
- `channel_data_[timestamp].json`: Contains the extracted channel data with this structure:
```json
{
  "scrape_time": "2024-03-21T12:34:56.789012",
  "channels": [
    {
      "channel_name": "ChannelName",
      "url": "https://youtube.com/@ChannelName",
      "description": "Channel description...",
      "social_links": [
        {
          "title": "Link title",
          "text": "Link text",
          "url": "Actual URL (not YouTube redirect)"
        }
      ],
      "subscribers": "1.2M subscribers",
      "views": "100M views",
      "country": "Country name",
      "joined": "Joined date"
    }
  ]
}
```

## Notes

### Video Scraper
- Videos are processed one at a time to avoid rate limiting
- Failed videos won't be marked as processed
- All text fields are cleaned and formatted for CSV compatibility

### Channel Scraper
- Some channels may have different amounts of information available

## Error Handling

Both scripts include error handling for:
- Network issues
- Missing elements
- Loading failures
- File writing errors

Failed items will be reported but won't stop the scripts from processing other items.

## Contributing

Feel free to submit issues and enhancement requests!
