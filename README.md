# Ancalentari Twitch Stream Recorder
This script allows you to record twitch streams live to .mp4 files.  
It is an improved version of [junian's twitch-recorder](https://gist.github.com/junian/b41dd8e544bf0e3980c971b0d015f5f6), migrated to [**helix**](https://dev.twitch.tv/docs/api) - the new twitch API. It uses OAuth2.
## Requirements
1. [python3.8](https://www.python.org/downloads/release/python-380/) or higher  
2. [streamlink](https://streamlink.github.io/)  
3. [ffmpeg](https://ffmpeg.org/)

## Setting up
1) 去[twitchDevelopers](https://dev.twitch.tv/console/apps)註冊您的應用程式  
`名稱` twitchREC(隨便取)  
`OAuth 重新導向網址` http://localhost  
`分類` Other  
`生成用戶端ID`  
`生成用戶端密碼`  

2) 去[LINE Notify](https://notify-bot.line.me/zh_TW/)取得token  
[LINE Notify教學](https://steam.oxxostudio.tw/category/python/spider/line-notify.html)


3) 在與 `twitch-recorder.py` 相同的目錄中建立 `config.py` 檔案，其內容為:  
`client_id` - 用戶端ID  
`client_secret` - 用戶端密碼  
`notify_token_start` - LineNotify 側錄開始的token  
`notify_token_finish` - LineNotify 側錄完成的token  
`notify_token_fix` - LineNotify 側錄修復的token  
`notify_token_error` - LineNotify 側錄故障的token  
`devicename` - 裝置名稱  

```properties
import os

root_path = os.getcwd()

REFRESH = 30            # 預設刷新頻率
DISPLAYNAME = ""        # 預設中文名稱
USERNAME = "monpo147"   # 預設英文ID
QUALITY = "best"        # 預設解析度

devicename = "[G3]"    # 裝置名稱


# twitchAPI
client_id = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
client_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# LINE Notify token 從開始側錄 傳送至twitchREC
notify_token_start = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
notify_token_finish = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
notify_token_fix = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
notify_token_error = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# docker compose
displayname = os.environ.get('displayname', DISPLAYNAME)    # - displayname=小米    
refresh = int(os.environ.get('refresh', REFRESH))           # - refresh=600
username = os.environ.get('username', USERNAME)             # - username=remiiouo
quality = os.environ.get('quality', QUALITY)                # - quality=480p
```

4) 在與 `twitch-recorder.py` 相同的目錄中建立 `docker-compose.yml` 檔案，其內容為: 
`displayname` = 中文名稱  
`username` = 英文ID  
`quality` = 解析度  
`refresh` = 刷新頻率  

```
version: "3.9"

# 在此處設置全局日誌驅動程式
x-logging: &logging
  driver: "json-file"
  options:
    max-size: "3m" # 這裡設定最大大小為 5MB
    max-file: "2" # 這裡設定最大文件數為 3

x-base_service: &base
  image: twitch-recorder:v1
  # build: .
  command: python3 twitch-recorder.py
  restart: always
  # logging: *logging
  environment:
    - LC_ALL=C.UTF-8
  volumes:
    - .:/app
  # healthcheck:
  #   test: ["CMD", "supervisorctl", "status"]
  #   interval: 60s
  #   timeout: 3s
  #   retries: 1

services:
  dozzle:
    container_name: dozzle
    image: amir20/dozzle:latest
    restart: always
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    ports:
      - 8892:8080

  remiiouo:
    <<: *base
    environment:
      - displayname=小米
      - username=remiiouo

  abuy_:
    <<: *base
    environment:
      - displayname=小白
      - username=abuy_
  #     - quality=720p
  #     - refresh=600

  monpo147:
    <<: *base
    environment:
      - displayname=孟婆
      - username=monpo147

  qaws_1109:
    <<: *base
    environment:
      - displayname=凌晨
      - username=qaws_1109

# start cmd /k "cd twitch-stream-recorder-master && python twitch-recorder.py -u happlesim"
```

## 建置Docker環境  
`windows`  
1) 在 WSL 2 上開始使用 Docker 遠端容器 [wsl2安裝教學](https://learn.microsoft.com/zh-tw/windows/wsl/install)  
[安裝Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)  

2) 安裝wsl
您現在可以安裝使用單一命令執行 WSL 所需的所有項目。 以滑鼠右鍵按一下並選取 [以系統管理員身分執行]，在系統管理員模式中開啟 PowerShell 或 Windows 命令提示字元，輸入 `wsl --install` 命令，然後重新開機電腦。 (使用 `wsl --install` 命令安裝的新 Linux 安裝預設會設定為 WSL 2)  
```
wsl --install
```
3) 在 WSL 2 中執行的 Linux 發行版本設定使用者名稱和密碼。  



3) 設定wsl2 [wsl2設定教學](https://learn.microsoft.com/zh-tw/windows/wsl/tutorials/wsl-containers)  
啟動 Docker Desktop  
進入`Settings`  
______`Resources`  
________`WSL integration`  
__________ `Refetch`後 將`Ubuntu`開啟   


## 執行Docker
1) 進入資料夾
```
cd T:\\twitchREC
```

2) 編譯docker build
```
docker build -t twitch-recorder:v1 .
```

3)   
開始執行run
```
docker-compose up -d
```

中止執行down
```
docker-compose down
```

重新執行restar
```
docker-compose restar
```