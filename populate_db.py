import hashlib
import json
import os

# collects all the concatenated images and sticks the metadata into a json file, to be loaded by a server for serving
# it up!

db = {}
if os.path.exists('db.json'):
    with open('db.json', 'r') as f:
        db = json.load(f)

# for jpg in images/, add a reference to it in the db by filename, and load the title from images/<id>.txt
for jpg in os.listdir('images'):
    if jpg.endswith('.jpg'):
        id = jpg.split('.')[0]
        if not os.path.exists(os.path.join('sd_output', id + '.txt')):
            continue
        with open(os.path.join('sd_output', id + '.txt'), 'r') as f:
            title = f.read()
        tmp = '/r/pics/' + id
        # create a 16 character hash from tmp
        hash = hashlib.md5(tmp.encode('utf-8')).hexdigest()[:16]
        db[hash] = {
            'title': title,
            'original_filename': os.path.join('images', jpg),
            'sd_filename': os.path.join('sd_output', id + '.png'),
            'concat_filename': os.path.join('concat', id + '.jpg'),
            'text_filename': os.path.join('sd_output', id + '.txt'),
            'score': 0,
            'funny': 0,
            'junk': 0,
            'reddit_id': id
        }

with open('db.json', 'w') as f:
    json.dump(db, f)