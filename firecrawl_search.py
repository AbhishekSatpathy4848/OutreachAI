import asyncio
import os
from firecrawl import AsyncFirecrawlApp, JsonConfig
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class YoutubeData(BaseModel):
    all_creator_links: list[str]
    email: str
    channel_name: str
    total_subscribers: int
    total_views: int
    total_videos: int
    link: str
    location: str
    description: str

async def scrapeWebsiteWithSchema(url, schema: BaseModel):
    
    app = AsyncFirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    response = await app.scrape_url(
        url=url,		
        formats=['json'],
        only_main_content=True,
        json_options=JsonConfig(
            schema=schema,
        )   
    )

    return response.json

async def scrapeWebsiteWithPrompt(url, prompt):
    
    app = AsyncFirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    response = await app.scrape_url(
        url=url,		
        formats=['json'],
        only_main_content=True,
        json_options=JsonConfig(
            prompt=prompt,
        )   
    )

    return response.json



if __name__ == "__main__":
    response = asyncio.run(scrapeWebsiteWithSchema("https://www.youtube.com/channel/UCY6N8zZhs2V7gNTUxPuKWoQ/about", YoutubeData))
    print(response)