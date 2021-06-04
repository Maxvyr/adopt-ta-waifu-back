from api.yandere_api import call_yandere_api
from api.konachan_api import call_konochan_api


# call gen mix 3 api
def call_global():
    title = "all_waifu"
    yandere_receive = call_yandere_api().get("fields")
    konachan_receive = call_konochan_api().get("fields")
    waifu_posts = yandere_receive + konachan_receive
    print(waifu_posts)
    return {
        "title": title,
        "fields": waifu_posts
    }


# call yandere spec
def call_yandere():
    return call_yandere_api()


# call konochan spec
def call_konochan():
    return call_konochan_api()
