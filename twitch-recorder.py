from datetime import datetime, timedelta, timezone
import enum
import getopt
import logging
import os
import shutil
import signal
import subprocess
import sys
import time

import requests

import config
# 設定時區為 UTC+8
tz_utc_8 = timezone(timedelta(hours=8))
# 簡寫時間格式
strftime = "%Y-%m-%d_%H:%M:%S"
disconnect_check = False
disconnect_time = 0

class TwitchResponseStatus(enum.Enum):
    ONLINE = 0
    OFFLINE = 1
    NOT_FOUND = 2
    UNAUTHORIZED = 3
    ERROR = 4


class TwitchRecorder:
    def __init__(self):
        # global configuration
        self.ffmpeg_path = "ffmpeg"
        self.disable_ffmpeg = False
        self.root_path = config.root_path

        # user configuration
        self.displayname = config.displayname
        self.refresh = config.refresh
        self.username = config.username
        self.quality = config.quality
        

        # twitch configuration
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.token_url = "https://id.twitch.tv/oauth2/token?client_id=" + self.client_id + "&client_secret=" \
                         + self.client_secret + "&grant_type=client_credentials"
        self.url = "https://api.twitch.tv/helix/streams"
        self.access_token = self.fetch_access_token()

    def fetch_access_token(self):
        token_response = requests.post(self.token_url, timeout=15)
        token_response.raise_for_status()
        token = token_response.json()
        return token["access_token"]

    def run(self):
        # path to recorded stream
        recorded_path = os.path.join(self.root_path, "recorded", self.username)
        # path to finished video, errors removed
        processed_path = os.path.join(self.root_path, "processed", self.username)

        # create directory for recordedPath and processedPath if not exist
        if os.path.isdir(recorded_path) is False:
            os.makedirs(recorded_path)
        if os.path.isdir(processed_path) is False:
            os.makedirs(processed_path)

        # make sure the interval to check user availability is not less than 15 seconds
        if self.refresh < 15:
            logging.warning("check interval should not be lower than 15 seconds")
            self.refresh = 15
            logging.info("system set check interval to 15 seconds")

        # fix videos from previous recording session
        # try:
        #     video_list = [f for f in os.listdir(recorded_path) if os.path.isfile(os.path.join(recorded_path, f))]
        #     if len(video_list) > 0:
        #         logging.info("processing previously recorded files")
        #     for f in video_list:
        #         recorded_filename = os.path.join(recorded_path, f)
        #         processed_filename = os.path.join(processed_path, f)
        #         self.process_recorded_file(recorded_filename, processed_filename)
        #     lineNotify(config.notify_token_fix, f'{config.devicename} {self.displayname} {self.username}\n[{datetime.now(tz_utc_8).strftime(strftime)}]\n{processed_filename[processed_filename.find(' - ')+23:]}')
        # except Exception as e:
        #     logging.error(e)

        logging.info("checking for %s %s every %s seconds, recording with %s quality\n",
                     self.displayname, self.username, self.refresh, self.quality)
        # lineNotify(config.notify_token_start, f'{config.devicename} [{datetime.now(tz_utc_8).strftime(strftime)}]\n{self.displayname} {self.username} 每{self.refresh}秒刷新, {self.quality}')
        self.loop_check(recorded_path, processed_path, disconnect_check, disconnect_time)

    def process_recorded_file(self, recorded_filename, processed_filename):
        if self.disable_ffmpeg:
            logging.info("moving: %s", recorded_filename)
            shutil.move(recorded_filename, processed_filename)
        else:
            logging.info("fixing %s", recorded_filename)
            self.ffmpeg_copy_and_fix_errors(recorded_filename, processed_filename)

    def ffmpeg_copy_and_fix_errors(self, recorded_filename, processed_filename):
        try:
            subprocess.call(
                [self.ffmpeg_path, "-err_detect", "ignore_err", "-i", recorded_filename, "-c", "copy",
                 processed_filename])
            os.remove(recorded_filename)
        except Exception as e:
            logging.error(e)

    def check_user(self):
        info = None
        status = TwitchResponseStatus.ERROR
        try:
            headers = {"Client-ID": self.client_id, "Authorization": "Bearer " + self.access_token}
            r = requests.get(self.url + "?user_login=" + self.username, headers=headers, timeout=30)
            r.raise_for_status()
            info = r.json()
            if info is None or not info["data"]:
                status = TwitchResponseStatus.OFFLINE
            else:
                status = TwitchResponseStatus.ONLINE
        except requests.exceptions.RequestException as e:

            if e.response:
                if e.response.status_code == 401:
                    status = TwitchResponseStatus.UNAUTHORIZED
                if e.response.status_code == 404:
                    status = TwitchResponseStatus.NOT_FOUND
        return status, info

    def loop_check(self, recorded_path, processed_path, disconnect_check, disconnect_time):
        while True:
            status, info = self.check_user()
            if status == TwitchResponseStatus.NOT_FOUND:
                logging.error("username not found, invalid username or typo")
                time.sleep(self.refresh)
            elif status == TwitchResponseStatus.ERROR:
                logging.error("%s unexpected error!!!!!!!!!!!!!!!!!!!!!!!!!",
                              datetime.now(tz_utc_8).strftime(strftime))
                lineNotify(config.notify_token_error,f'{config.devicename} {self.displayname} {self.username}\n[{datetime.now(tz_utc_8).strftime(strftime)}] unexpected error!!!!!!!!!!!!!!!!!!!!!!!!!')
                sys.exit()
                # time.sleep(300)
            elif status == TwitchResponseStatus.OFFLINE:
                logging.info("%s %s currently offline, checking again in %s seconds", self.displayname, self.username, self.refresh)
                video_list = [f for f in os.listdir(recorded_path) if os.path.isfile(os.path.join(recorded_path, f))]
                # 直播斷線後每15秒嘗試連線20次,再進行檔案搬家
                if disconnect_check == True:
                    disconnect_time += 1
                    logging.info(f'[{disconnect_time}/20] 斷線嘗試重新連線')
                    if disconnect_time >= 20:
                        disconnect_check = False 
                        disconnect_time = 0
                    time.sleep(15)
                elif disconnect_check == False:
                    if os.path.isdir(processed_path) is False:
                        os.makedirs(processed_path)
                    if (len(video_list) > 0):
                        logging.info("\n\nprocessing video file!!!!")
                    for f in video_list:
                        recorded_filename = os.path.join(recorded_path, f)
                        processed_filename = os.path.join(processed_path, f)
                        self.process_recorded_file(recorded_filename, processed_filename)
                        logging.info("processing is done, going back to checking...")
                    time.sleep(self.refresh)
                else:
                    time.sleep(self.refresh)
            elif status == TwitchResponseStatus.UNAUTHORIZED:
                logging.info("unauthorized, will attempt to log back in immediately")
                self.access_token = self.fetch_access_token()
                lineNotify(config.notify_token_error,f'{config.devicename} {datetime.now(tz_utc_8).strftime(strftime)} unauthorized, will attempt to log back in immediately!!!!!!!!!!!!!!!!!!!!!!!!!')
            elif status == TwitchResponseStatus.ONLINE:
                logging.info("%s %s online, stream recording in session", self.displayname, self.username)
                channels = info["data"]
                # for channelinfo in channels:
                #     logging.info(channelinfo)
                # {'id': '41215532999', 
                #  'user_id': '92069370', 
                #  'user_login': 'tonychachachacha', 
                #  'user_name': '基隆東', 
                #  'game_id': '488190', 
                #  'game_name': 'Poker', 
                #  'type': 'live', 
                #  'title': '林巴巴勒 我沒有傳影片 更不是他媽會員', 
                #  'viewer_count': 696, 
                #  'started_at': '2024-04-11T15:08:49Z', 
                #  'language': 'zh', 
                #  'thumbnail_url': 'https://static-cdn.jtvnw.net/previews-ttv/live_user_tonychachachacha-{width}x{height}.jpg', 
                #  'tag_ids': [], 
                #  'tags': ['中文'], 
                #  'is_mature': True}

                channel = next(iter(channels), None)
                lineNotify(config.notify_token_start, f'{config.devicename} {self.displayname} {self.username}\n[{datetime.now(tz_utc_8).strftime(strftime)}]\n{channel.get("title")} {self.quality}')
                
                filename = channel.get("user_name") + " - " + self.username + " - " + datetime.now(tz_utc_8).strftime(strftime) + " - " + channel.get("title") + ".mp4"

                # clean filename from unnecessary characters
                filename = "".join(x for x in filename if x.isalnum() or x in [" ", "-", "_", "."])

                recorded_filename = os.path.join(recorded_path, filename)
                processed_filename = os.path.join(processed_path, filename)

                # start streamlink process
                subprocess.call(
                    ["streamlink", "--twitch-disable-ads", "twitch.tv/" + self.username, self.quality,
                     "-o", recorded_filename])

                logging.info("recording stream is done")
                lineNotify(config.notify_token_finish, f'{config.devicename} {self.displayname} {self.username}\n[{datetime.now(tz_utc_8).strftime(strftime)}]\n{channel.get("title")}')
                # if os.path.exists(recorded_filename) is True:
                #     self.process_recorded_file(recorded_filename, processed_filename)
                # else:
                #     logging.info("skip fixing, file not found")
                # logging.info("processing is done, going back to checking...\n")
                # time.sleep(self.refresh)
                disconnect_check = True
                time.sleep(15)

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


def main(argv):
    twitch_recorder = TwitchRecorder()
    usage_message = "twitch-recorder.py -u <username> -q <quality>"
    logging.basicConfig(filename="twitch-recorder.log", level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())

    try:
        opts, args = getopt.getopt(argv, "hu:q:l:", ["username=", "quality=", "log=", "logging=", "disable-ffmpeg"])
    except getopt.GetoptError:
        print(usage_message)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print(usage_message)
            sys.exit()
        elif opt in ("-u", "--username"):
            twitch_recorder.username = arg
        elif opt in ("-q", "--quality"):
            twitch_recorder.quality = arg
        elif opt in ("-l", "--log", "--logging"):
            logging_level = getattr(logging, arg.upper(), None)
            if not isinstance(logging_level, int):
                raise ValueError("invalid log level: %s" % logging_level)
            logging.basicConfig(level=logging_level)
            logging.info("logging configured to %s", arg.upper())
        elif opt == "--disable-ffmpeg":
            twitch_recorder.disable_ffmpeg = True
            logging.info("ffmpeg disabled")

    twitch_recorder.run()


if __name__ == "__main__":
    main(sys.argv[1:])
