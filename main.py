import argparse
import uvicorn
import requests
import os
import hashlib
import json
from fastapi import FastAPI, Request, Response

app = FastAPI()


ORIGIN_URL = ""
CACHE_DIR = ".cache"

def get_cache_filename(url):
    """
    Turn a URL (e.g., http://google.com/foo) into a safe filename 
    (e.g., a1b2c3d4e5f6.json) using MD5 hashing.
    """
    hash_object = hashlib.md5(url.encode())
    return os.path.join(CACHE_DIR, hash_object.hexdigest() + ".json")

@app.api_route("/{path:path}", methods=["GET"])
async def proxy(path: str, request: Request):
 
    target_url = f"{ORIGIN_URL}/{path}"
    
   
    cache_file = get_cache_filename(target_url)
    
   
    if os.path.exists(cache_file):
        print(f"✅ Cache HIT: {path}")
        
        # Read the file
        with open(cache_file, 'r') as f:
            cached_data = json.load(f)
            
        # Return the cached data with the HIT header
        return Response(
            content=cached_data['content'], 
            status_code=cached_data['status_code'], 
            headers=cached_data['headers']
        )

    # --- CACHE MISS LOGIC ---
    print(f"❌ Cache MISS: {target_url}")
    try:
        # Fetch from the REAL server
        resp = requests.get(target_url, params=request.query_params)
        
        # Clean up headers
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded_headers}
        
        # Add the Header indicating we went to the origin
        headers["X-Cache"] = "MISS"

        # SAVE TO CACHE
        cache_data = {
            "content": resp.text,
            "status_code": resp.status_code,
            "headers": headers
        }
        
        cache_data['headers']['X-Cache'] = "HIT" 
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)

        return Response(content=resp.content, status_code=resp.status_code, headers=headers)

    except Exception as e:
        return Response(content=f"Error: {str(e)}", status_code=500)

def main():
    global ORIGIN_URL
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, help="Port to run the server on")
    parser.add_argument('--origin', type=str, help="Origin URL to forward to")
    parser.add_argument('--clear-cache', action='store_true', help="Clear the cache")
    
    args = parser.parse_args()
    

    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


    if args.clear_cache:
        print(" Clearing cache...")
        for f in os.listdir(CACHE_DIR):
            file_path = os.path.join(CACHE_DIR, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print(" Cache cleared!")
        return

   
    if not args.port or not args.origin:
        parser.error("--port and --origin are required to start the server.")

    
    ORIGIN_URL = args.origin

    print(f" Caching Proxy started on port {args.port}")
    print(f" Cache folder: {os.path.abspath(CACHE_DIR)}")
    
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()