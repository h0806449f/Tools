import lark_oapi as lark
from lark_oapi.api.im.v1 import *

# 會回傳 Lark Bot 所在的 Lark 群, Lark 群 ID

APP_ID = "cli_a838d1fd2bb89010"
APP_SECRET = "q99CuUzZE5jZRQLnU4ZX0gQXyaQBMmRg"

client = lark.Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()

request = ListChatRequest.builder().page_size(50).build()
response = client.im.v1.chat.list(request)

if response.success() and response.data and response.data.items:
    for chat in response.data.items:
        print(chat.name, chat.chat_id)
else:
    print("Failed to list chats")
    print("Code:", response.code)
    print("Msg:", response.msg)
    print("Log ID:", response.get_log_id())
