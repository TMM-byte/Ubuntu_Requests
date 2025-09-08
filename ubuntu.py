import requests
import os
from urllib.parse import urlparse
import hashlib
from mimetypes import guess_extension

def is_valid_image(response):
    content_type = response.headers.get("Content-Type", "")
    return content_type.startswith("image/")

def get_image_extension(content_type):
    ext = guess_extension(content_type.split(";")[0])
    return ext if ext else ".jpg"

def hash_content(content):
    return hashlib.sha256(content).hexdigest()

def image_already_downloaded(image_hash, hash_set):
    return image_hash in hash_set

def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")
    
    # Get URL(s) from user
    urls_input = input("Please enter image URL(s), separated by commas: ")
    urls = [url.strip() for url in urls_input.split(",") if url.strip()]
    
    try:
        # Create directory if it doesn't exist
        os.makedirs("Fetched_Images", exist_ok=True)
        
        # Track downloaded image hashes
        downloaded_hashes = set()
        
        for url in urls:
            try:
                # Fetch the image
                response = requests.get(url, timeout=10)
                response.raise_for_status()  # Raise exception for bad status codes
                
                # Check if response is an image
                if not is_valid_image(response):
                    print(f"✗ Skipped (Not an image): {url}")
                    continue
                
                # Check for duplicate image
                image_hash = hash_content(response.content)
                if image_already_downloaded(image_hash, downloaded_hashes):
                    print(f"✗ Skipped (Duplicate image): {url}")
                    continue
                
                # Extract filename from URL or generate one
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                
                if not filename or '.' not in filename:
                    filename = f"image_{image_hash[:8]}{get_image_extension(response.headers.get('Content-Type', ''))}"
                    
                # Save the image
                filepath = os.path.join("Fetched_Images", filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                    
                downloaded_hashes.add(image_hash)
                print(f"✓ Successfully fetched: {filename}")
                print(f"✓ Image saved to {filepath}")
            
            except requests.exceptions.RequestException as e:
                print(f"✗ Connection error: {url} → {e}")
            except Exception as e:
                print(f"✗ An error occurred: {url} → {e}")
        
        print("\nConnection strengthened. Community enriched.")
        
    except Exception as e:
        print(f"✗ Setup error: {e}")

if __name__ == "__main__":
    main()
