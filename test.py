import json

# Replace 'your_json_file.json' with the path to your JSON file
with open('output.json', 'r') as f:
    data = json.load(f)

# Loop through the entries in the 'live_tv' key
for entry in data['live_tv']:
    # Print the title of the entry
    print('Title:', entry['title'])
    # Print the description of the entry
    print('Description:', entry['description'])
    # Print the start time of the entry
    print('Start Time:', entry['start_time'])
    # Print a separator to make the output more readable
    print('-' * 50)
