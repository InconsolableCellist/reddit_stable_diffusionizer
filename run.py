import base64
import pickle
import time
from random import random
import praw
import os
import requests
import cv2
import numpy as np

request_body = {
    "fn_index": 12,
    "data": [
        "example prompt",
        "",
        "None",
        "None",
        20,
        "Euler a",
        False,
        False,
        1,
        1,
        8.5,
        123456789,
        -1,
        0,
        0,
        0,
        False,
        512,
        512,
        False,
        False,
        0.7,
        "None",
        False,
        False,
        None,
        "",
        "Seed",
        "",
        "Steps",
        "",
        True,
        False,
        None
    ],
    "session_hash": "ypf9htfouk"
}

HOST = 'http://' + os.environ.get('HOSTNAME_AND_PORT') + '/api/predict/'

def update_from_reddit():
    USERNAME        = os.environ.get('REDDIT_USERNAME')
    PASSWORD        = os.environ.get('REDDIT_PASSWORD')
    CLIENT_SECRET   = os.environ.get('REDDIT_CLIENT_SECRET')
    CLIENT_ID       = os.environ.get('REDDIT_CLIENT_ID')

    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent='pics archiver 0.1',
        username=USERNAME,
        password=PASSWORD)
    subreddit = reddit.subreddit('funny')
    top_subreddit = subreddit.top('month', limit=1000)

    top_posts = []
    for submission in top_subreddit:
        top_posts.append(submission)

    return top_posts

def get_from_disk():
    with open('top_posts.pkl', 'rb') as f:
        top_posts = pickle.load(f)
    return top_posts

def write_to_disk(top_posts):
    with open('top_posts.pkl', 'wb') as f:
        pickle.dump(top_posts, f)

def generate_next_concat(post):
    if os.path.exists('concat/' + post.id + '.jpg'):
        return False

    request_body['data'][0] = post.title
    response = requests.post(HOST, json=request_body)

    data = response.json()['data']
    image_string = data[0][0].split(',')[1]

    with open('sd_output/' + post.id + '.png', 'wb') as f:
        f.write(base64.b64decode(image_string))
    print(f'Stable Diffusion generated. Wrote {post.id}.png')

    with open('sd_output/' + post.id + '.txt', 'w') as f:
        f.write(post.title)

    img1 = cv2.imread('images/' + post.id + '.jpg')
    img2 = cv2.imread('sd_output/' + post.id + '.png')

    try:
        # try resize img1 while maintaining aspect ratio
        h1, w1, _ = img1.shape
        h2, w2, _ = img2.shape
        if h1 > h2:
            w1 = int(w1 * h2 / h1)
            h1 = h2
            img1 = cv2.resize(img1, (w1, h1))
        elif w1 > w2:
            h1 = int(h1 * w2 / w1)
            w1 = w2
            img1 = cv2.resize(img1, (w1, h1))

        img2 = cv2.resize(img2, (512, 512))
        img3 = np.concatenate((img1, img2), axis=1)

        cv2.rectangle(img3, (0, img3.shape[0] - 50), (img3.shape[1], img3.shape[0]), (0, 0, 0), -1)
        cv2.putText(img3, post.title, (int(img3.shape[1] / 2) - int(len(post.title) * 10 / 2), img3.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imwrite('concat/' + post.id + '.jpg', img3)
        print(f'Saved concatenated version to {post.id}.jpg')
    except Exception as e:
        print(f'Failed to concatenate {post.id}.jpg')
        print(e)
        return False

    return True

def fetch_new_images(posts):
    print(f'Fetching any new images')
    for post in posts:
        print('.', end='', flush=True)
        if 'v.redd.it' not in post.url and not os.path.exists('images/' + post.id + '.jpg'):
            print('fetching ' + post.url)
            response = requests.get(post.url)
            with open('images/' + post.id + '.jpg', 'wb') as f:
                f.write(response.content)
            print(f'wrote {post.id}.jpg')
            time.sleep(random() * 2 + 1)

# posts = update_from_reddit()
# write_to_disk(posts)
posts = get_from_disk()
fetch_new_images(posts)

if not os.path.exists('images'):
    os.makedirs('images')
if not os.path.exists('sd_output'):
    os.makedirs('sd_output')
if not os.path.exists('concat'):
    os.makedirs('concat')

for post in posts:
    generate_next_concat(post)

print('Done')