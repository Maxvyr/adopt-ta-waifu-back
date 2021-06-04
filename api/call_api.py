from api.yandere_api import call_yandere_api
from api.danbooru_api import call_danbooru_api
from api.konachan_api import call_konochan_api


# call gen mix 3 api
def call_global():
    yandere_receive = call_yandere_api()
    danbooru_receive = call_danbooru_api()
    konachan_receive = call_konochan_api()



    return call_yandere_api()


# call yandere spec
def call_yandere():
    return call_yandere_api()


# call gelboru spec
def call_danbooru():
    return call_danbooru_api()


# call konochan spec
def call_konochan():
    return call_konochan_api()
