import re
import json

filename = "playlist.m3u"

# Initialize the data structures for the sections
vod = {"series": [], "movies": []}
live_tv = {}

# Parse the M3U file and group the entries into the sections
with open(filename, "r") as f:
    current_group = None
    for line in f:
        line = line.strip()
        if line.startswith("#EXTINF"):
            url = next(f).strip()
            # Extract the metadata attributes from the line using regex
            metadata = re.findall(r'tvg-(id|name|logo)="(.*?)"', line)
            if "/series/" in url:
                vod["series"].append({
                    "tvg-id": metadata[0][1],
                    "tvg-name": metadata[1][1],
                    "tvg-logo": metadata[2][1],
                    "url": url
                })
            elif "/movie/" in url:
                vod["movies"].append({
                    "tvg-id": metadata[0][1],
                    "tvg-name": metadata[1][1],
                    "tvg-logo": metadata[2][1],
                    "url": url
                })
            else:
                group_title = re.search(r'group-title="(.*?)"', line).group(1)
                if group_title not in live_tv:
                    live_tv[group_title] = []
                live_tv[group_title].append({
                    "tvg-id": metadata[0][1],
                    "tvg-name": metadata[1][1],
                    "tvg-logo": metadata[2][1],
                    "url": url
                })
        elif line.startswith("#EXTGRP"):
            current_group = line.split(":")[1]
            live_tv[current_group] = []

# Output the grouped data to a JSON file
output_data = {"vod": vod, "live_tv": live_tv}
with open("output.json", "w") as f:
    json.dump(output_data, f)

print("Output saved to output.json")
