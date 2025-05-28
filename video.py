from playwright.async_api import async_playwright
import csv
from datetime import datetime
import asyncio
import os

def clean_text(text):
    """Clean text for CSV output by replacing newlines and handling special characters."""
    if not text:
        return ""
    # Replace newlines with spaces
    text = text.replace('\n', ' ').replace('\r', ' ')
    # Replace multiple spaces with single space
    text = ' '.join(text.split())
    return text

async def extract_meta_tags(page):
    # First get meta tags
    meta_data = await page.evaluate("""
        () => {
            const data = {};
            const metas = document.getElementsByTagName('meta');
            
            // Helper function to get meta content
            const getMeta = (attr, value) => {
                const meta = Array.from(metas).find(m => m.getAttribute(attr) === value);
                return meta ? meta.getAttribute('content').trim() : '';
            };

            // Helper function to get all matching meta tags
            const getAllMeta = (attr, value) => {
                return Array.from(metas)
                    .filter(m => m.getAttribute(attr) === value)
                    .map(m => ({
                        type: m.getAttribute('content'),
                        count: document.querySelector(`meta[itemprop="userInteractionCount"][content="${m.nextElementSibling?.getAttribute('content')}"]`)?.getAttribute('content')
                    }));
            };
            
            data.title = getMeta('name', 'title') || getMeta('property', 'og:title');
            data.description = getMeta('name', 'description') || getMeta('property', 'og:description');
            data.keywords = getMeta('name', 'keywords');
            data.url = getMeta('property', 'og:url');
            data.image = getMeta('property', 'og:image');
            data.duration = getMeta('itemprop', 'duration');
            data.isFamilyFriendly = getMeta('itemprop', 'isFamilyFriendly');
            data.datePublished = getMeta('itemprop', 'datePublished');
            data.uploadDate = getMeta('itemprop', 'uploadDate');
            data.genre = getMeta('itemprop', 'genre');

            // Get all interaction types and their counts
            const interactions = getAllMeta('itemprop', 'interactionType');
            interactions.forEach(interaction => {
                if (interaction.type === 'https://schema.org/LikeAction') {
                    data.likeCount = interaction.count;
                } else if (interaction.type === 'https://schema.org/WatchAction') {
                    data.viewCount = interaction.count;
                }
            });
            
            return data;
        }
    """)

    # Now get the channel name from the page
    channel_name = await page.evaluate("""
        () => {
            const channelElement = document.querySelector('#owner #channel-name a');
            return channelElement ? channelElement.textContent.trim() : '';
        }
    """)
    
    # Clean all text fields
    for key, value in meta_data.items():
        if isinstance(value, str):
            meta_data[key] = clean_text(value)
    
    # Update the channel name in our data
    meta_data['channelName'] = clean_text(channel_name)
    
    return meta_data

async def extract_comments(page):
    try:
        # Scroll multiple times to ensure comments load
        for _ in range(3):
            await page.evaluate("window.scrollTo(0, window.scrollY + window.innerHeight)")
            await page.wait_for_timeout(1000)

        # Wait for comments section
        await page.wait_for_selector("#comments", timeout=5000)
        
        # Additional scroll to comments
        await page.evaluate("""
            () => {
                const comments = document.querySelector("#comments");
                if (comments) comments.scrollIntoView();
            }
        """)
        
        # Wait longer for comments to load
        await page.wait_for_timeout(5000)
        
        # Extract top 5 comments with more specific selector
        comments = await page.evaluate("""
            () => {
                const commentElements = document.querySelectorAll("ytd-comment-thread-renderer #content-text");
                return Array.from(commentElements).slice(0, 5).map(comment => comment.textContent.trim());
            }
        """)
        
        # Clean comments
        return [clean_text(comment) for comment in (comments if comments else [])]
    except Exception as e:
        print(f"Error getting comments: {str(e)}")
        return []

async def process_video(page, video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"\nProcessing video: {url}")
    
    await page.goto(url)
    # Wait for the channel name to be visible
    await page.wait_for_selector('#owner #channel-name a', timeout=10000)
    
    # Get meta data
    meta_data = await extract_meta_tags(page)
    
    # Get comments
    comments = await extract_comments(page)
    
    # Add comments to meta data
    for i, comment in enumerate(comments, 1):
        meta_data[f'comment_{i}'] = comment
    
    return meta_data

def get_all_fields(data_list):
    """Get all unique fields from a list of dictionaries."""
    fieldnames = set()
    for data in data_list:
        fieldnames.update(data.keys())
    return sorted(list(fieldnames))

def append_to_csv(data, filename, fieldnames=None):
    """Append a single row to the CSV file, creating it if it doesn't exist."""
    file_exists = os.path.exists(filename)
    
    if not fieldnames:
        fieldnames = get_all_fields([data])
    
    with open(filename, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        
        # Write header only if file is new
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(data)

def mark_video_as_processed(video_id, processed_file='processed_videos.txt'):
    """Mark a video as processed by appending its ID to a file."""
    with open(processed_file, 'a', encoding='utf-8') as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{video_id},{timestamp}\n")

def get_processed_videos(processed_file='processed_videos.txt'):
    """Get list of already processed video IDs."""
    if not os.path.exists(processed_file):
        return set()
    
    processed = set()
    with open(processed_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                video_id = line.strip().split(',')[0]
                processed.add(video_id)
    return processed

async def main():
    # List of video IDs to process
    video_ids = [
        'c2tuxS3Pcto',
        'kxs9Su_mbpU',
        'mvkbCZfwWzA'
    ]
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"video_data_{timestamp}.csv"
    
    # Get already processed videos
    processed_videos = get_processed_videos()
    
    # Filter out already processed videos
    videos_to_process = [vid for vid in video_ids if vid not in processed_videos]
    
    if not videos_to_process:
        print("All videos have already been processed!")
        return
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        
        for video_id in videos_to_process:
            try:
                data = await process_video(page, video_id)
                
                # Immediately write to CSV
                append_to_csv(data, csv_filename)
                print(f"Data for video {video_id} written to {csv_filename}")
                
                # Mark as processed
                mark_video_as_processed(video_id)
                print(f"Video {video_id} marked as processed")
                
            except Exception as e:
                print(f"Error processing video {video_id}: {str(e)}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
