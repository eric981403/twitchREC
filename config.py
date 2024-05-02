import os

root_path = os.getcwd()
# root_path = "C://"

REFRESH = 30
DISPLAYNAME = ""
USERNAME = "monpo147"
QUALITY = "best"
devicename = "[VN7]"


# twitchAPI
client_id = "p5c7jtietox7a9pfg0mpwhvp8hxtii"
client_secret = "zk4o7c9k6tefd7dzexk7lols8yistb"

# LINE Notify token 從開始側錄 傳送至twitchREC
notify_token_start = "miJXRe6H1jisSZ9MamVdxDlvfbBghjbosMZCzJfBQMn"
notify_token_finish = "xj29SDmvtozZSar2HdtjoZMw5kGt4hyfGhfFhLE0PdN"
notify_token_fix = "INXhXL5QCSZAqlntH62AomiyLavJyksSe7Un2DUMrLg"
notify_token_error = "lQS3CJNn1Z0TlFH1zVDLXADItSuX5uQg9duxCKIkR4a"

# docker compose
displayname = os.environ.get('displayname', DISPLAYNAME)    # - displayname=小米    
refresh = int(os.environ.get('refresh', REFRESH))           # - refresh=600
username = os.environ.get('username', USERNAME)             # - username=remiiouo
quality = os.environ.get('quality', QUALITY)                # - quality=480p