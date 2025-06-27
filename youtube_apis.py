import os
from googleapiclient.discovery import build
from dotenv import load_dotenv
from collections import Counter
from prompt_llms import prompt_nova_lite 
import json

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY_2")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def search_videos_for_channels(query, max_results=50):
    """Search for videos first, then extract unique channels that create content about the topic"""
    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)
        
        # Search for videos related to the topic
        search_response = youtube.search().list(
            q=query,
            type="video",
            part="snippet",
            maxResults=max_results,
            order="relevance",
            videoDefinition="any",
            videoDuration="any"
        ).execute()

        # Extract channel IDs and count video frequency per channel
        channel_frequency = Counter()
        channel_info = {}
        
        for item in search_response['items']:
            channel_id = item['snippet']['channelId']
            channel_title = item['snippet']['channelTitle']
            
            channel_frequency[channel_id] += 1
            if channel_id not in channel_info:
                channel_info[channel_id] = {
                    'title': channel_title,
                    'sample_video_titles': []
                }
            
            # Store sample video titles for context
            if len(channel_info[channel_id]['sample_video_titles']) < 3:
                channel_info[channel_id]['sample_video_titles'].append(item['snippet']['title'])
        
        # Sort channels by frequency (channels with more relevant videos appear first)
        sorted_channels = channel_frequency.most_common()
        
        return sorted_channels, channel_info
    
    except Exception as e:
        print(f"Error searching for videos: {e}")
        return [], {}

def search_channels_directly(query, max_results=10):
    """Direct channel search as backup method"""
    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)
        
        search_response = youtube.search().list(
            q=query,
            type="channel",
            part="snippet",
            maxResults=max_results,
            order="relevance"
        ).execute()

        channels = []
        for item in search_response['items']:
            channels.append((item['snippet']['channelId'], 1))  # Format to match video search
        
        return channels
    
    except Exception as e:
        print(f"Error in direct channel search: {e}")
        return []

def get_channel_details(channel_id):
    """Get detailed information about a channel including recent videos"""
    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)
        
        # Get channel details
        channel_response = youtube.channels().list(
            id=channel_id,
            part="snippet,statistics,brandingSettings"
        ).execute()

        if not channel_response['items']:
            return None
        
        item = channel_response['items'][0]
        
        # Get recent videos to understand channel content
        videos_response = youtube.search().list(
            channelId=channel_id,
            type="video",
            part="snippet",
            maxResults=5,
            order="date"
        ).execute()
        
        recent_videos = [video['snippet']['title'] for video in videos_response['items']]
        
        # Extract channel information
        title = item['snippet']['title']
        description = item['snippet'].get('description', 'No description available')
        subscriber_count = item['statistics'].get('subscriberCount', 'Hidden')
        video_count = item['statistics'].get('videoCount', '0')
        
        # Handle custom URL
        custom_url = ''
        if 'brandingSettings' in item and 'channel' in item['brandingSettings']:
            custom_url = item['brandingSettings']['channel'].get('customUrl', '')
        
        # Create the about URL
        if custom_url:
            about_url = f"https://www.youtube.com/@{custom_url.lstrip('@')}/about"
        else:
            about_url = f"https://www.youtube.com/channel/{channel_id}/about"
        
        return {
            "channel_name": title,
            "description": description,
            "subscriber_count": format_subscriber_count(subscriber_count),
            "video_count": video_count,
            "about_url": about_url,
            "channel_url": f"https://www.youtube.com/channel/{channel_id}",
            "recent_videos": recent_videos
        }
    
    except Exception as e:
        print(f"Error getting channel details for {channel_id}: {e}")
        return None

def format_subscriber_count(count):
    """Format subscriber count for better readability"""
    if count == 'Hidden':
        return 'Hidden'
    
    try:
        count = int(count)
        if count >= 1000000:
            return f"{count/1000000:.1f}M"
        elif count >= 1000:
            return f"{count/1000:.1f}K"
        else:
            return str(count)
    except:
        return count
    

def generate_related_queries(main_query, num_queries=3):
    """
    Generate related search queries for YouTube channel discovery using Gemini AI
    
    Args:
        main_query (str): The main topic/category to find related queries for
        num_queries (int): Number of related queries to generate (default: 3)
    
    Returns:
        list: List of related query strings
    """
    prompt = f"""
    Generate {num_queries} related search queries for finding YouTube channels about "{main_query}".
    
    Requirements:
    - Each query should be 2-4 words long
    - Focus on variations, synonyms, and related subtopics
    - Make them suitable for YouTube search
    - Include both beginner and advanced variations if applicable
    - Avoid repeating the exact same words
    
    Examples:
    - If main query is "weight loss", related queries could be: "fat loss", "cardio workout", "diet tips", "fitness transformation", "belly fat"
    - If main query is "yoga", related queries could be: "yoga flow", "morning yoga", "yoga poses", "mindfulness meditation", "stretching exercises"
    
    Please provide only the query terms, one per line, without numbers or bullet points.
    Main query: "{main_query}"
    """
    
    response = prompt_nova_lite(prompt)
    
    # Parse the response to extract individual queries
    queries = []
    for line in response.strip().split('\n'):
        line = line.strip()
        # Remove any numbering, bullets, or extra formatting
        line = line.lstrip('1234567890.- ').strip()
        if line:
            queries.append(line)
    
    # Return the requested number of queries
    return queries[:num_queries]

def search_for_channels(query, max_channels=10, verbose=False):
    """
    Search for YouTube channels based on a given query string.
    
    Args:
        query (str): The query string to search for channels
        max_channels (int): Maximum number of channels to return (default: 10)
        verbose (bool): Whether to print progress messages (default: False)
    
    Returns:
        list: List of channel information dictionaries
    """
    if verbose:
        print("YouTube Channel Search Tool")
        print("-" * 45)
    
    if not YOUTUBE_API_KEY:
        error_msg = "Error: YouTube API key not found. Please set YOUTUBE_API_KEY in your .env file."
        if verbose:
            print(error_msg)
        return []
    
    if verbose:
        print(f"\nSearching for channels that create '{query}' content...")
        print("=" * 60)
    
    all_channels = {}
    
    # Method 1: Search videos first (primary method)
    if verbose:
        print("🔍 Analyzing videos to find relevant channels...")
    sorted_channels, channel_info = search_videos_for_channels(query, 50)
    
    for channel_id, frequency in sorted_channels:
        if channel_id not in all_channels:
            all_channels[channel_id] = {
                'frequency': frequency,
                'sample_videos': channel_info[channel_id]['sample_video_titles']
            }
    
    # Method 2: Search related queries using Gemini
    if verbose:
        print("🤖 Generating related search topics...")
    related_queries = generate_related_queries(query, 3)  # Generate 3 related queries
    if verbose:
        print(f"🔍 Searching related topics: {', '.join(related_queries)}...")

    for related_query in related_queries:  # Limit to avoid API quota issues
        sorted_channels, channel_info = search_videos_for_channels(related_query, 30)
        for channel_id, frequency in sorted_channels[:10]:  # Top 10 from each related search
            if channel_id in all_channels:
                all_channels[channel_id]['frequency'] += frequency
            else:
                all_channels[channel_id] = {
                    'frequency': frequency,
                    'sample_videos': channel_info[channel_id]['sample_video_titles']
                }
    
    # Method 3: Direct channel search as backup
    if verbose:
        print("🔍 Adding channels with relevant names...")
    direct_channels = search_channels_directly(query, 15)
    for channel_id, _ in direct_channels:
        if channel_id not in all_channels:
            all_channels[channel_id] = {'frequency': 1, 'sample_videos': []}
    
    # Sort all channels by frequency (content relevance)
    final_channels = sorted(all_channels.items(), key=lambda x: x[1]['frequency'], reverse=True)
    
    if not final_channels:
        if verbose:
            print("No relevant channels found.")
        return []

    results = []
    for i, (channel_id, channel_data) in enumerate(final_channels[:max_channels], 1):
        details = get_channel_details(channel_id)
        if details:
            channel_json = {
                "channel_name": details['channel_name'],
                "relevance_score": channel_data['frequency'],
                "subscribers": details['subscriber_count'],
                "total_videos": details['video_count'],
                "sample_content": channel_data['sample_videos'][:2] if channel_data['sample_videos'] else [],
                "recent_videos": details['recent_videos'][:2] if details['recent_videos'] else [],
                "description": details['description'],
                "channel_url": details['channel_url'],
                "about_url": details['about_url']
            }
            results.append(channel_json)

    return results

if __name__ == "__main__":
    # Example usage for testing
    query = input("Enter the topic or category: ")
    max_channels = input("Enter max number of channels to show (default 10): ")
    
    try:
        max_channels = int(max_channels) if max_channels else 10
    except ValueError:
        max_channels = 10
    
    channels = search_for_channels(query, max_channels, verbose=True)
    print(json.dumps(channels, indent=2, ensure_ascii=False))