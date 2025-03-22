import requests
import json
import time

def get_unsung_heroine_data(page_title):
    """Retrieves data from Wikipedia API for a given page title (Unsung Heroines)."""
    headers = {
        'User-Agent': 'TheUnsungHeroines/1.0 (your.email@example.com)'
    }
    url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts|pageimages|info&titles={page_title}&exintro=true&explaintext=true&pithumbsize=300&inprop=url"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        page = next(iter(data['query']['pages'].values()))
        if page.get('missing'):
            print(f"Warning: Page '{page_title}' not found.")
            return None
        return {
            'title': page.get('title'),
            'extract': page.get('extract'),
            'image': page.get('thumbnail', {}).get('source'),
            'full_url': page.get('fullurl')
        }
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None
    except KeyError:
        print(f"KeyError: Unexpected API response format.")
        return None
    except Exception as e:
        print(f"An unexpected error occured: {e}")
        return None

def get_unsung_heroines_from_category(category_title):
    """Gets a list of women page titles from a wikipedia category (Unsung Heroines)."""
    headers = {
        'User-Agent': 'TheUnsungHeroines/1.0 (your.email@example.com)'
    }
    url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=categorymembers&cmtitle=Category:{category_title}&cmlimit=500"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        women_titles = [member['title'] for member in data['query']['categorymembers']]
        return women_titles
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None
    except KeyError:
        print(f"KeyError: Unexpected API response format.")
        return None
    except Exception as e:
        print(f"An unexpected error occured: {e}")
        return None

# List of categories to scrape for "The Unsung Heroines" (focusing on categories with individual women)
unsung_heroines_categories = [
    'Women scientists',
    'Women physicians',
    'Lesbian scientists',
    'Jewish women scientists',
]

all_unsung_heroines_data = []

for category_title in unsung_heroines_categories:
    women_titles = get_unsung_heroines_from_category(category_title)
    if women_titles:
        for title in women_titles:
            woman_data = get_unsung_heroine_data(title)
            if woman_data:
                all_unsung_heroines_data.append(woman_data)
            time.sleep(2)  # Respectful delay.
    else:
        print(f"Failed to retrieve women titles for {category_title}.")

with open('unsung_heroines_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_unsung_heroines_data, f, ensure_ascii=False, indent=4)
print("Data saved to unsung_heroines_data.json")