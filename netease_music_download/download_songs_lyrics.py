#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import os
import json,re

# JSON链接
# json_url = "https://api.injahow.cn/meting/?type=playlist&id=9313871605"

playlist_input = input("请输入网易云音乐歌单ID或者url：")

if playlist_input == '':
    print("必须输入歌单ID")
    exit()

# Check if the input matches the URL pattern
url_pattern = r"https://music\.163\.com/#/playlist\?id=(\d+)"
match = re.match(url_pattern, playlist_input)

if match:
    # Extract the playlist ID from the URL
    playlist = match.group(1)
else:
    # Use the input number directly
    playlist = playlist_input

json_url = "https://api.injahow.cn/meting/?type=playlist&id=" + playlist

# 下载路径
# download_path = "./s"
print(r"默认下载路径 ./music_lyrics")
download_path = "./music_lyrics"

if download_path == '':
    download_path = r"./music_lyrics"

# 创建下载路径
os.makedirs(download_path, exist_ok=True)


def download_song(url, song_path):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length'))
    downloaded_size = 0

    with open(song_path, "wb") as song_file:
        for data in response.iter_content(chunk_size=4096):
            downloaded_size += len(data)
            song_file.write(data)
            progress = downloaded_size / total_size * 100
            print(f"正在下载 {song_path}，进度：{progress:.2f}%\r", end="")

    print(f"下载完成 {song_path}")


def safe_filename(filename):
    # 将特殊字符（/）改成（-）
    return filename.replace("/", "_")


# 发送GET请求获取JSON数据
response = requests.get(json_url)
data = json.loads(response.text)

# 遍历每首歌曲
for song in data:
    # 歌曲信息
    name = song["name"]
    artist = song["artist"]
    url = song["url"]
    lrc = song["lrc"]

    # 歌曲文件名和路径
    song_filename = f"{safe_filename(name)} - {safe_filename(artist)}.mp3"
    song_path = os.path.join(download_path, song_filename)

    # 下载歌曲
    # download_song(url, song_path)

    print(lrc)
    lrc_filename = f"{safe_filename(name)} - {safe_filename(artist)}.lrc"
    lrc_path = os.path.join(download_path, lrc_filename)

    # Check if the file already exists
    if not os.path.exists(lrc_path):
        lrc_response = requests.get(lrc)
        print(f"download {lrc_filename}")
        with open(lrc_path, "wb") as lrc_file:
            lrc_file.write(lrc_response.content)
    else:
        print(f"{lrc_filename} already exists. Skipping download.")

print("Download done.")
a = input()
