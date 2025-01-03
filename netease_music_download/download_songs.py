import requests  # 数据请求模块 第三方模块 pip install requests
import re  # 正则表达式模块 内置模块 不需要安装
import os  # 文件操作模块

filename = './music/'

if not os.path.exists(filename): # 如果没有这个文件夹则自动创建
    os.mkdir(filename)

# 如果想要爬取其他的榜单的歌曲内容，只要更改请求url中的id

url = 'https://music.163.com/discover/toplist?id=180106'
# headers请求头 就是用伪装python代码的 把python代码伪装成浏览器对于服务器发送请求
# 服务器接收到请求之后，会给我们返回响应数据(response)
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
}
response = requests.get(url=url, headers=headers)
#print(response.text)获取网页源代码
# 正则表达式提取出来的一个内容 返回是列表 里面每一个元素都是元组
html_data = re.findall('<li><a href="/song\?id=(\d+)">(.*?)</a>',response.text)
for num_id, title in html_data:
   # http://music.163.com/song/media/outer/url?id=436346833.mp3
   music_url = f'http://music.163.com/song/media/outer/url?id={num_id}.mp3'
   # 对于音乐播放地址发送请求 获取二进制数据内容
   music_content = requests.get(url=music_url, headers=headers).content
   with open(filename +title +'.mp3', mode='wb') as f:
        f.write(music_content)
   print(num_id, title)
