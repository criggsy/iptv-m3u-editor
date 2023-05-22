from flask import Flask, render_template, request
from db import db
from models import Entry, UniqueTvgType, UniqueGroupTitle
import requests
from requests.exceptions import ChunkedEncodingError
import re
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///m3u.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'  # Set the upload folder path
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Ensure the upload folder exists

# Initialize the db instance
db.init_app(app)

# Create the database tables
with app.app_context():
    from db import create_tables
    create_tables()


# Retry logic for ChunkedEncodingError
def retry_on_chunked_encoding_error(url):
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
        except ChunkedEncodingError as e:
            print(f"ChunkedEncodingError occurred. Retrying... ({retries+1}/{max_retries})")
            retries += 1

    raise Exception("Failed to download the M3U content.")

# Parse M3U content and extract entries
def parse_m3u_content(m3u_content):
    from models import Entry

    lines = m3u_content.splitlines()
    entries = []
    metadata_pattern = r'#EXTINF:-1 tvg-id="([^"]*)" tvg-name="([^"]*)" tvg-logo="([^"]*)" group-title="([^"]*)",(.*)'
    entry_data = {
        'tvg_id': '',
        'tvg_name': '',
        'tvg_logo': '',
        'group_title': '',
        'metadata_value': '',
        'channel_number': 0,
        'tvg_type': '',
        'url': ''
    }
    for line in lines:
        line = line.strip()
        if line.startswith('#EXTINF:-1'):
            entry_data['url'] = ""  # Reset the URL value for each entry
            match = re.match(metadata_pattern, line)
            if match:
                entry_data['tvg_id'] = match.group(1)
                entry_data['tvg_name'] = match.group(2)
                entry_data['tvg_logo'] = match.group(3)
                entry_data['group_title'] = match.group(4)
                entry_data['metadata_value'] = match.group(5)
            else:
                entry_data['metadata_value'] = ""  # Reset the metadata value if not found

        elif entry_data['metadata_value']:
            entry_data['url'] = line
            entry_data['channel_number'] += 1

            # Determine the TVG type based on the URL
            if '/series/' in entry_data['url'] and not entry_data['tvg_id']:
                entry_data['tvg_type'] = 'series'
            elif '/movie/' in entry_data['url'] and not entry_data['tvg_id']:
                entry_data['tvg_type'] = 'movie'
            else:
                entry_data['tvg_type'] = 'live'

            # Create an Entry object or data structure with the extracted data
            entry = Entry(
                channel_number=entry_data['channel_number'],
                metadata_value=entry_data['metadata_value'],
                url=entry_data['url'],
                tvg_id=entry_data['tvg_id'],
                tvg_name=entry_data['tvg_name'],
                tvg_logo=entry_data['tvg_logo'],
                group_title=entry_data['group_title'],
                tvg_type=entry_data['tvg_type']
            )
            entries.append(entry)

    return entries

# Define your routes here
@app.route('/', methods=['GET', 'POST'])
def index():
    from models import Entry, UniqueTvgType, UniqueGroupTitle
    db.create_all()
    if request.method == 'POST':
        m3u_url = request.form.get('m3u_url')
        if m3u_url:
            # Download the M3U content with retry logic
            m3u_content = retry_on_chunked_encoding_error(m3u_url)
        elif 'm3u_file' in request.files:
            m3u_file = request.files['m3u_file']
            if m3u_file.filename != '':
                # Read the contents of the uploaded file
                m3u_content = m3u_file.read().decode('utf-8')

        # Parse the M3U content and extract entries
        entries = parse_m3u_content(m3u_content)

        # Save the entries to the main Entry table
        db.session.bulk_save_objects(entries)
        db.session.commit()

        # Create a new table with unique entries in tvg_type field
        unique_tvg_types = set(entry.tvg_type for entry in entries)
        unique_tvg_type_entries = [UniqueTvgType(tvg_type=tvg_type) for tvg_type in unique_tvg_types]
        db.session.bulk_save_objects(unique_tvg_type_entries)
        db.session.commit()

        # Create a new table with unique entries in group_title field
        unique_group_titles = set(entry.group_title for entry in entries)
        unique_group_title_entries = [UniqueGroupTitle(group_title=group_title) for group_title in unique_group_titles]
        db.session.bulk_save_objects(unique_group_title_entries)
        db.session.commit()


        return 'Data imported successfully.'

    return render_template('index.html')


if __name__ == '__main__':
    app.run()
