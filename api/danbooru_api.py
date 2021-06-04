import json
import requests


def call_danbooru_api():
    url = "https://danbooru.donmai.us/posts.json"
    title = "Danbooru"

    data = requests.get(url)
    posts_receive = json.loads(data.text)
    post_return = []

    for post in posts_receive:
        post_return.append({
            "sample": post["large_file_url"],
            "file": post["file_url"],
            "author": post["tag_string_artist"],
            "preview_img": post["preview_file_url"]
        })

    return {
        "title": title,
        "fields": post_return
    }

