import requests
import json
import os

def get_newspaper_image_urls(query, start_year=1860, end_year=1930, items=[]):
    '''
    Searches Chronicling America for newspaper pages matching the query.
    Retrieves thumbnail and full JP2 image URLs for analysis.
    Handles pagination.
    '''
    base_url = f"https://chroniclingamerica.loc.gov/search/pages/results/?proxtext={query}&dateFilterType=yearRange&date1={start_year}&date2={end_year}&rows=100&format=json"
    current_url = base_url
    while current_url:
        try:
            params = {"fo": "json", "at": "results,pagination"}
            call = requests.get(current_url, params=params)
            call.raise_for_status()  # Raise error for bad responses
            data = call.json()
            results = data['results']
            for result in results:
                if "newspaper" in result.get("original_format", []):
                    # Thumbnail URL
                    thumbnail = result.get("image_url", [])[-1] if result.get("image_url") else None
                    # Construct full JP2 URL if lccn, date, edition, sequence available
                    jp2 = None
                    if "lccn" in result and "date" in result and "edition" in result and "sequence" in result:
                        jp2 = f"https://chroniclingamerica.loc.gov/lccn/{result['lccn']}/{result['date']}/ed-{result['edition']}/seq-{result['sequence']}.jp2"
                    items.append({"thumbnail": thumbnail, "jp2": jp2, "item_url": result.get("id")})
            if data["pagination"].get("next"):
                current_url = data["pagination"]["next"]
                print("Getting next page: {0}".format(current_url))
            else:
                current_url = None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            break
    return items

def analyze_image(image_url, save_dir='images'):
    '''
    Downloads the image for analysis and performs basic checks (e.g., size).
    For advanced analysis, use external tools like OCR (pytesseract) or view_image.
    '''
    if not image_url:
        return "No image URL available."
    os.makedirs(save_dir, exist_ok=True)
    filename = image_url.split('/')[-1]
    filepath = os.path.join(save_dir, filename)
    try:
        response = requests.get(image_url if image_url.startswith('http') else f"https:{image_url}", stream=True)
        response.raise_for_status()
        with open(filepath, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=128):
                fd.write(chunk)
        print(f"Downloaded {filename} for analysis.")
        # Basic analysis example (file size)
        size = os.path.getsize(filepath)
        return f"Image analyzed: Size {size} bytes. (Extend with OCR/view_image for text extraction.)"
    except requests.exceptions.RequestException as e:
        return f"Error analyzing image: {e}"

# Example usage for E.H. Jennings research
query = "e h jennings"
image_data = get_newspaper_image_urls(query)
print(f"Found {len(image_data)} newspaper pages.")

# Analyze the first full JP2 if available
if image_data:
    first_jp2 = image_data[0].get("jp2")
    if first_jp2:
        analysis_result = analyze_image(first_jp2)
        print(analysis_result)
    else:
        print("No JP2 available for first result; try thumbnail.")
        analysis_result = analyze_image(image_data[0].get("thumbnail"))
        print(analysis_result)
