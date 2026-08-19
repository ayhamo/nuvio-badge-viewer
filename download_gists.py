import os
import json
import base64
import urllib.request
import urllib.parse
import urllib.error
import re
import time
from http.client import RemoteDisconnected

# ---------------------------------------------------------
# ⚙️ SETTINGS
# ---------------------------------------------------------
USERNAME = "darpit33"

# Modify these to match where you will upload your backup repository!
# This allows the script to generate valid absolute URLs for Nuvio.
MY_GITHUB_USERNAME = "ayhamo" 
MY_REPO_NAME = "nuvio-badge-viewer"
BRANCH = "main"

CUSTOM_IMAGE_BASE_URL = f"https://raw.githubusercontent.com/{MY_GITHUB_USERNAME}/{MY_REPO_NAME}/{BRANCH}/gif-backup"
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(BASE_DIR, "json-backup")
JSON_LOCAL_DIR = os.path.join(BASE_DIR, "json-local")
GIF_BASE_DIR = os.path.join(BASE_DIR, "gif-backup")

os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(JSON_LOCAL_DIR, exist_ok=True)
os.makedirs(GIF_BASE_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://catbox.moe/",
    "Connection": "keep-alive"
}

def sanitize_filename(name):
    clean = re.sub(r'[\\/*?:"<>|]', "", str(name)).strip()
    return clean if clean else "unnamed"

def sanitize_url(url):
    if not url or not isinstance(url, str):
        return ""
    url = url.strip()
    
    unquoted = urllib.parse.unquote(url)
    parsed = urllib.parse.urlsplit(unquoted)
    if not parsed.scheme or not parsed.netloc:
        return ""
    
    clean_path = urllib.parse.quote(parsed.path, safe="/:@&+$,~-_")
    clean_query = urllib.parse.quote(parsed.query, safe="=&?/:@+$~-_")
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, clean_path, clean_query, parsed.fragment))

def save_image(img_str, destination_without_ext):
    img_str = img_str.strip()
    
    # 1. Base64 Data URI
    if img_str.startswith("data:"):
        match = re.match(r"^data:(image\/[a-zA-Z0-9\+\-]+)?;base64,(.*)$", img_str, re.IGNORECASE | re.DOTALL)
        if not match:
            raise ValueError("Malformed base64 data URI")
        
        mime_type, b64_data = match.groups()
        ext_map = {
            "image/png": ".png", "image/gif": ".gif",
            "image/jpeg": ".jpg", "image/webp": ".webp", "image/svg+xml": ".svg"
        }
        ext = ext_map.get(mime_type.lower() if mime_type else "", ".png")
        final_dest = f"{destination_without_ext}{ext}"
        
        with open(final_dest, "wb") as f:
            f.write(base64.b64decode(b64_data))
        return final_dest

    # 2. Remote HTTP/HTTPS URL
    clean_url = sanitize_url(img_str)
    if not clean_url:
        raise ValueError("Invalid URL format")
    
    try:
        parsed_url = urllib.parse.urlsplit(urllib.parse.unquote(clean_url))
        ext = os.path.splitext(parsed_url.path)[1]
        if not ext or len(ext) > 5:
            ext = ".gif"
    except Exception:
        ext = ".gif"
        
    final_dest = f"{destination_without_ext}{ext}"
    req = urllib.request.Request(clean_url, headers=HEADERS)
    
    max_retries = 4
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                with open(final_dest, "wb") as f:
                    f.write(resp.read())
            
            time.sleep(0.5) 
            return final_dest
        except (urllib.error.URLError, RemoteDisconnected, ConnectionResetError) as e:
            if attempt < max_retries - 1:
                print(f"    [Retry {attempt+1}] Connection dropped, waiting...")
                time.sleep(2 * (attempt + 1)) 
                continue
            raise e

def download_all_gists_and_gifs():
    api_url = f"https://api.github.com/users/{USERNAME}/gists"
    req = urllib.request.Request(api_url, headers=HEADERS)
    
    print(f"Fetching gists for @{USERNAME} from GitHub API...")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            gists = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error connecting to GitHub API: {e}")
        return

    total_json = 0
    total_saved_images = 0
    total_failed_links = 0

    for gist in gists:
        files = gist.get("files", {})
        for filename, file_info in files.items():
            if not filename.lower().endswith(".json"):
                continue

            raw_url = file_info.get("raw_url")
            if not raw_url:
                continue

            json_dest = os.path.join(JSON_DIR, filename)
            json_local_dest = os.path.join(JSON_LOCAL_DIR, filename)
            json_name_no_ext = os.path.splitext(filename)[0]
            gif_folder = os.path.join(GIF_BASE_DIR, json_name_no_ext)
            os.makedirs(gif_folder, exist_ok=True)

            print(f"\n========================================")
            print(f"Processing: {filename}")
            print(f"========================================")

            try:
                clean_raw_url = sanitize_url(raw_url)
                file_req = urllib.request.Request(clean_raw_url, headers=HEADERS)
                with urllib.request.urlopen(file_req, timeout=15) as file_resp:
                    content = file_resp.read().decode("utf-8")
                    data = json.loads(content)

                with open(json_dest, "w", encoding="utf-8") as out:
                    json.dump(data, out, indent=2)
                print(f"✓ Saved Original JSON: json-backup/{filename}")
                total_json += 1
            except Exception as ex:
                print(f"✗ Failed to download JSON {filename}: {ex}")
                continue

            filters = data.get("filters", [])
            for f in filters:
                img_url = f.get("imageURL", "")
                if not img_url or not isinstance(img_url, str) or not img_url.strip():
                    continue

                filter_name = sanitize_filename(f.get("name", "unnamed"))
                filter_id = sanitize_filename(f.get("id", "no-id"))
                dest_without_ext = os.path.join(gif_folder, f"{filter_name}_{filter_id}")

                try:
                    saved_path = save_image(img_url, dest_without_ext)
                    filename_saved = os.path.basename(saved_path)
                    
                    # 🔧 FIXED: Construct the full, safe internet URL for Nuvio
                    safe_path = urllib.parse.quote(f"{json_name_no_ext}/{filename_saved}")
                    f["imageURL"] = f"{CUSTOM_IMAGE_BASE_URL}/{safe_path}"
                    
                    print(f"  → Saved image: gif-backup/{json_name_no_ext}/{filename_saved}")
                    total_saved_images += 1
                except urllib.error.HTTPError as http_err:
                    print(f"  ✗ HTTP {http_err.code} for '{filter_name}': {img_url}")
                    total_failed_links += 1
                except Exception as ex:
                    print(f"  ✗ Error for '{filter_name}' ({img_url}): {ex}")
                    total_failed_links += 1

            try:
                with open(json_local_dest, "w", encoding="utf-8") as out:
                    json.dump(data, out, indent=2)
                print(f"✓ Saved Nuvio-ready JSON: json-local/{filename}")
            except Exception as ex:
                print(f"✗ Failed to save local JSON {filename}: {ex}")

    print(f"\n========================================")
    print(f"Finished!")
    print(f"• JSON files processed: {total_json}")
    print(f"• Images/GIFs successfully saved: {total_saved_images}")
    print(f"• Failed images: {total_failed_links}")
    print(f"========================================")

if __name__ == "__main__":
    download_all_gists_and_gifs()