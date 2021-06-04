import json
import requests


def call_yandere_api():
    url = "https://yande.re/post.json"
    title = "Yandere"

    data = requests.get(url)
    posts_receive = json.loads(data.text)
    post_return = []

    for post in posts_receive:
        post_return.append({
            "sample": post["sample_url"],
            "file": post["file_url"],
            "author": post["author"],
            "preview_img": post["preview_url"]
        })

    return {
        "title": title,
        "fields": post_return
    }

