import os
import requests
from dotenv import load_dotenv

load_dotenv()

def google_search(query, num_results=5):
    """
    Perform a Google Custom Search and return results.
    """
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cse_id = os.getenv("CSE_ID")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": cse_id,
        "num": num_results,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    items = response.json().get("items", [])
    return [(item.get("title"), item.get("snippet"), item.get("link")) for item in items]

    
if __name__ == "__main__":
    query = input("Enter your search query: ")
    try:
        results = google_search(query)
        print(results)
    except Exception as e:
        print(f"Error: {e}")
