from flask import Flask, render_template, request, redirect
import math
import re

app = Flask(__name__)
from models import Entry
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///m3u.db'  # SQLite database URI
db = SQLAlchemy(app)



# Initialize the database
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    entries_per_page = 10  # Number of entries to display per page
    current_page = int(request.args.get('page', 1))  # Get the current page number from the query string
    
    if request.method == 'POST':
        # Process the form submission and save the modified entries
        for key, value in request.form.items():
            if key.startswith('metadata'):
                entry_id = int(key.split('metadata')[-1])
                entry = Entry.query.get(entry_id)
                entry.metadata_value = value.strip()
                entry.url = request.form.get('url' + str(entry_id), '').strip()
                entry.tvg_id = request.form.get('tvg-id' + str(entry_id), '').strip()
                entry.tvg_name = request.form.get('tvg-name' + str(entry_id), '').strip()
                entry.tvg_logo = request.form.get('tvg-logo' + str(entry_id), '').strip()
                entry.group_title = request.form.get('group-title' + str(entry_id), '').strip()
        
        db.session.commit()
        
        return redirect('/?page=' + str(current_page))  # Redirect back to the current page after saving

    else:
        # Check if entries exist in the database
        if Entry.query.count() == 0:
    # Read the M3U file and save entries to the database
            with open('/home/crigs/GitHub/iptv-m3u-editor/playlist.m3u', 'r') as file:
                lines = file.readlines()
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

                        # Save the entry
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

                # Save all the entries
                db.session.bulk_save_objects(entries)
                db.session.commit()


        # Read the entries from the database and perform pagination
        total_entries = Entry.query.count()
        total_pages = math.ceil(total_entries / entries_per_page)
        start_index = (current_page - 1) * entries_per_page
        entries = Entry.query.order_by(Entry.id).offset(start_index).limit(entries_per_page).all()

        return render_template('index.html', entries=entries, current_page=current_page, total_pages=total_pages)

if __name__ == '__main__':
    app.run()




#/home/crigs/GitHub/iptv-m3u-editor/playlist.m3u