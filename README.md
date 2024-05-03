# Ancalentari Twitch Stream Recorder
This script allows you to record twitch streams live to .mp4 files.  
It is an improved version of [junian's twitch-recorder](https://gist.github.com/junian/b41dd8e544bf0e3980c971b0d015f5f6), migrated to [**helix**](https://dev.twitch.tv/docs/api) - the new twitch API. It uses OAuth2.
## Requirements
1. [python3.8](https://www.python.org/downloads/release/python-380/) or higher  
2. [streamlink](https://streamlink.github.io/)  
3. [ffmpeg](https://ffmpeg.org/)

## Setting up
1) 在與 `twitch-recorder.py` 相同的目錄中建立 `config.py` 檔案，其內容為:
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


`devicename` - 裝置名稱
去[twitchDevelopers](https://dev.twitch.tv/console/apps)註冊您的應用程式
`名稱` twitchREC(隨便取)
`OAuth 重新導向網址` http://localhost
`分類` Other
`生成用戶端ID`
`生成用戶端密碼`

`client_id` - 用戶端ID
`client_secret` - 用戶端密碼
`notify_token_start` - LineNotify 側錄開始的token
`notify_token_finish` - LineNotify 側錄完成的token
`notify_token_fix` - LineNotify 側錄修復的token
`notify_token_error` - LineNotify 側錄故障的token

## Docker compose
```
  chiao622:
    <<: *base
    environment:
      - displayname=阿寧
      - username=chiao622
#      - quality=720p
#      - refresh=600
```

## Docker
進入資料夾
```
cd T:\\twitchREC
```

docker build
```
docker build -t twitch-recorder:v1 .
```

run
```
docker-compose up -d
```

down
```
docker-compose down
```

restar
```
docker-compose restar
```



## Running script
The script will be logging to a console and to a file `twitch-recorder.log`
### On linux
Run the script
```shell script
python3.8 twitch-recorder.py
```
To record a specific streamer use `-u` or `--username`
```shell script
python3.8 twitch-recorder.py --username forsen
```
To specify quality use `-q` or `--quality`
```shell script
python3.8 twitch-recorder.py --quality 720p
```
To change default logging use `-l`, `--log` or `--logging`
```shell script
python3.8 twitch-recorder.py --log warn
```
To disable ffmpeg processing (fixing errors in recorded file) use `--disable-ffmpeg`
```shell script
python3.8 twitch-recorder.py --disable-ffmpeg
```
If you want to run the script as a job in the background and be able to close the terminal:
```shell script
nohup python3.8 twitch-recorder.py >/dev/null 2>&1 &
```
In order to kill the job, you first list them all:
```shell script
jobs
```
The output should show something like this:
```shell script
[1]+  Running                 nohup python3.8 twitch-recorder > /dev/null 2>&1 &
```
And now you can just kill the job:
```shell script
kill %1
```
### On Windows
You can run the scipt from `cmd` or [terminal](https://www.microsoft.com/en-us/p/windows-terminal/9n0dx20hk701?activetab=pivot:overviewtab), by simply going to the directory where the script is located at and using command:
```shell script
python twitch-recorder.py
```
The optional parameters should work exactly the same as on Linux.
