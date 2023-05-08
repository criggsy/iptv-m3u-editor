import requests
import json
from requests.exceptions import ChunkedEncodingError

url = "http://ios.exodus-1.rocks:8080/get.php?username=crigs&password=tdsryrhq&output=ts&type=m3u_plus"
filename = "playlist.m3u"

# Download the M3U file with retry in case of incomplete read
max_retries = 5
retry_count = 0

while retry_count < max_retries:
    try:
        response = requests.get(url, stream=True)
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print("Playlist downloaded as", filename)
        break
    except ChunkedEncodingError:
        retry_count += 1
        print("Failed to download playlist, retrying...")

if retry_count == max_retries:
    print("Failed to download playlist after", max_retries, "attempts.")
    exit()

# Initialize the data structures for the sections
vod = {"series": [], "movies": []}
live_tv = {}

# Parse the M3U file and group the entries into the sections
with open(filename, "r") as f:
    current_group = None
    for line in f:
        line = line.strip()
        if line.startswith("#EXTINF"):
            metadata = line.split(",")
            if "/series/" in metadata[1]:
                vod["series"].append({"name": metadata[1], "url": next(f).strip()})
            elif "/movie/" in metadata[1]:
                vod["movies"].append({"name": metadata[1], "url": next(f).strip()})
        elif line.startswith("#EXTGRP"):
            current_group = line.split(":")[1]
            live_tv[current_group] = []
        elif line.startswith("#EXTINF") and "group-title" in line:
            # Extract the group title from the line
            group_title = line.split('group-title="')[1].split('"')[0]
            # If the group title is new, create a new list for it
            if group_title not in live_tv:
                live_tv[group_title] = []
            # Add the channel URL to the list for the group title
            live_tv[group_title].append(next(f).strip())

# Output the grouped data to a JSON file
output_data = {"vod": vod, "live_tv": live_tv}
with open("output.json", "w") as f:
    json.dump(output_data, f)

print("Output saved to output.json")
