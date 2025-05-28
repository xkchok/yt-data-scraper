from playwright.async_api import Playwright, async_playwright, Page
from urllib.parse import urlparse, parse_qs, unquote
import json
import asyncio
from typing import Dict, List
from datetime import datetime

# Icon to label mapping
ICON_LABEL_MAP = {
    "language": "channel_url",
    "privacy_public": "country",
    "info_outline": "joined",
    "person_radar": "subscribers",
    "my_videos": "videos",
    "trending_up": "views"
}

async def get_description(page: Page) -> str:
    """Extract channel description."""
    description = await page.locator("#description-container").text_content()
    return description.strip() if description else "Not found"

async def get_social_links(page: Page) -> List[Dict[str, str]]:
    """Extract social links from the channel."""
    social_links = []
    containers = page.locator(".yt-channel-external-link-view-model-wiz__container")
    
    # Get all containers first
    all_containers = await containers.all()
    for container in all_containers:
        # Get title
        title = await container.locator("span").first.text_content()
        
        # Get link info
        anchor = container.locator("a")
        link_text = await anchor.text_content()
        redirect_url = await anchor.get_attribute("href")
        
        # Extract real URL from YouTube redirect
        parsed_url = urlparse(redirect_url)
        real_url = parse_qs(parsed_url.query).get("q", [""])[0]
        real_url = unquote(real_url)
        
        social_links.append({
            'title': title.strip(),
            'text': link_text.strip(),
            'url': real_url
        })
    
    return social_links

async def get_channel_info(page: Page) -> Dict[str, str]:
    """Extract channel information from visible rows."""
    channel_info = {}
    visible_rows = page.locator("ytd-about-channel-renderer tr.description-item:not([hidden])")
    
    # Get all rows first
    all_rows = await visible_rows.all()
    for row in all_rows:
        # Get the icon type
        icon = await row.locator("yt-icon").get_attribute("icon")
        
        # Get the data text
        text = await row.locator("td").nth(1).text_content()
        
        if icon and text:
            label = ICON_LABEL_MAP.get(icon, icon)  # fallback to raw icon name
            channel_info[label] = text.strip()
    
    return channel_info

def save_to_json(data: List[Dict], filename: str = None):
    """Save channel data to JSON file with timestamp."""
    if filename is None:
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"channel_data_{timestamp}.json"
    
    # Add timestamp to the data
    output_data = {
        "scrape_time": datetime.now().isoformat(),
        "channels": data
    }
    
    # Write to JSON file with proper formatting and encoding
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Data saved to {filename}")

async def scrape_channel(playwright: Playwright, url: str) -> Dict:
    """Main function to scrape channel data."""
    browser = await playwright.chromium.launch()
    context = await browser.new_context()
    page = await context.new_page()
    
    try:
        # Navigate to the channel's about page
        if not url.endswith('/about'):
            url = url.rstrip('/') + '/about'
        await page.goto(url)
        
        # Wait for and get channel name
        await page.wait_for_selector("ytd-engagement-panel-title-header-renderer #title-text")
        channel_name = await page.locator("ytd-engagement-panel-title-header-renderer #title-text").text_content()
        channel_name = channel_name.strip() if channel_name else "Not found"
        
        # Get all channel data
        channel_data = {
            'channel_name': channel_name,
            'url': url,
            'description': await get_description(page),
            'social_links': await get_social_links(page)
        }
        channel_data.update(await get_channel_info(page))
        
        return channel_data
    
    except Exception as e:
        print(f"Error scraping channel {url}: {str(e)}")
        return None
    finally:
        # Close browser
        await context.close()
        await browser.close()

async def main():
    # List of channels to scrape
    channels = [
        "https://www.youtube.com/@The_FirstTake",
        "https://www.youtube.com/@aimersmej",
        "https://www.youtube.com/channel/UC5CwaMl1eIgY8h02uZw7u8A",
        # Add more channels here
    ]
    
    async with async_playwright() as playwright:
        # Scrape all channels
        tasks = [scrape_channel(playwright, url) for url in channels]
        results = await asyncio.gather(*tasks)
        
        # Filter out None results (failed scrapes)
        channel_data = [data for data in results if data is not None]
        
        # Save to JSON
        save_to_json(channel_data)

if __name__ == "__main__":
    asyncio.run(main())
