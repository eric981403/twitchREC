def lineNotify(token, msg):
    #line伺服器位址
    url = "https://notify-api.line.me/api/notify"
    #token認證用
    headers = {
        "Authorization": "Bearer " + token
    }
    #宣告一個物件，裡面存放要傳送的訊息
    payload = {'message': msg}
    #將headers和data傳送至url，也就是將token和訊息傳送至line伺服器
    r = requests.post(url, headers=headers, data=payload)
    #status_code為requests除錯用，回傳錯誤代碼，不用理會
    return r.status_code