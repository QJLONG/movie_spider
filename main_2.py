# 目标网站：https://www.shukeju.org/kanvodplay/386176-3-1/
# 操作步骤：
# 1.获取网页源代码，从中获取第一层m3u8文件URL
# 2.下载第一层m3u8文件
# 3.下载所有ts文件
# 4.获取key
# 5.对所有ts文件解密
# 6.合并所有ts文件为MP4文件
# 7.添加图形界面，并设置下载列表

import requests
import re
import asyncio
import aiohttp
import aiofiles
from Crypto.Cipher import AES
import os
from lxml import etree
# from concurrent.futures import ThreadPoolExecutor
from tkinter import *
from tkinter import ttk


def first_m3u8_url(total_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/108.0.0.0 Safari/537.36 "
    }
    resp = requests.get(total_url, headers=headers)
    resp.encoding = "utf-8"
    # 获取m3u8文件的URL
    re_item = re.compile(r',"url":"(?P<url>.*?)",', re.S)
    m3u8_url = re_item.findall(resp.text)[-1]
    m3u8_url = m3u8_url.replace(r"\/", "/")
    # 获取名字
    tree = etree.HTML(resp.text)
    temp = tree.xpath('//*[@id="mq"]/ul/li[1]/text()')[0]
    # print(temp)
    name = temp.split(" - ")[-1]
    return m3u8_url, name


def down_m3u8(m3u8_url, path):  #path:.\\第一集\\temp.m3u8
    temp_path = path.replace("\\temp.m3u8", "")
    mkdir_cmd = f"mkdir {temp_path}"
    os.system(mkdir_cmd)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/108.0.0.0 Safari/537.36 "
    }
    resp = requests.get(m3u8_url, headers=headers)
    with open(path, mode="wb") as f:
        f.write(resp.content)
    # print("m3u8文件下载完毕！")


async def aio_dow(path, ts_url, session):       # path:.\\第一集\\
    try:
        ts_name = ts_url.split("/")[-1]
        async with session.get(ts_url) as resp:
            async with aiofiles.open(path + ts_name, mode="wb") as f:
                await f.write(await resp.content.read())
                # print(ts_name, "下载完成！")
    except Exception as e:
        # print(ts_url)
        print(e)


async def dow_ts(m3u8_path):     # path:.\\第一集\\temp.m3u8
    tasks = []
    timeout = aiohttp.ClientTimeout(total=60*2, sock_read=60)
    temp_path = m3u8_path.replace("temp.m3u8", "")
    async with aiohttp.ClientSession(timeout=timeout) as session:
        with open(m3u8_path, mode="r", encoding="utf-8") as f:
            for line in f:
                if not line.startswith("https"):
                    continue
                else:
                    ts_url = line.strip()
                    # print(temp_path)
                    tasks.append(asyncio.create_task(aio_dow(temp_path, ts_url, session)))
            await asyncio.wait(tasks)


async def aio_dec(ts_path, key):   # ts_path:.\\第一集\\ts_name
    aes = AES.new(key=key, mode=AES.MODE_CBC, IV=b"0000000000000000")
    async with aiofiles.open(ts_path, mode="rb") as f1, \
        aiofiles.open(ts_path.replace(".ts", "_dec.ts"), mode="wb") as f2:
        bs = await f1.read()
        await f2.write(aes.decrypt(bs))
        print(ts_path, "处理完毕！！")


async def dec_ts(path, key):    # path:.\\第一集\\temp.m3u8
    tasks = []
    temp_path = path.replace("temp.m3u8", "")
    async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
        async for line in f:
            line = line.strip()
            if not line.startswith("https"):
                continue
            else:
                ts_url = line
                # ts_path:.\\第一集\\ts_name
                ts_path = temp_path + ts_url.split("/")[-1]
                task = asyncio.create_task(aio_dec(ts_path, key=key))
                tasks.append(task)
        await asyncio.wait(tasks)


def get_key(m3u8_path):
    with open(m3u8_path, mode="r", encoding="utf-8") as f:
        re_item = re.compile(r'URI="(?P<url>.*?)"', re.S)
        key_url = re_item.search(f.read()).group("url")
    resp = requests.get(key_url)
    return resp.content


def merge_ts(m3u8_path, movie_name):    # m3u8_path:.\\第一集\\temp.m3u8
    # 存放每组的文件名
    name_lists = [[]]
    temp_path = m3u8_path.replace("temp.m3u8", "")  # temp_path:.\\第一集\\
    # 用来存放每组合成的结果的名字，方便做最终合并
    results = []
    i = 0
    with open(m3u8_path, mode="r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("https"):
                continue
            else:
                if i >= 99:
                    i = 0
                    name_lists.append([])
                name_lists[-1].append(temp_path + line.split("/")[-1].replace(".ts", "_dec.ts"))
                i += 1
    # 将每组合并成一个mp4文件
    j = 1
    for names in name_lists:
        temp_str = "+".join(names)
        cmd = f"copy /b {temp_str} {temp_path}result_{j}.mp4"
        # print(cmd)
        results.append(f"{temp_path}result_{j}.mp4")
        os.system(cmd)
        j += 1
    # print(results)
    # 对每组的结果做最终合并
    temp_str = "+".join(results)
    cmd = f"copy /b {temp_str} {movie_name}.mp4"
    os.system(cmd)
    print(f"{movie_name}.mp4 合并完成！")
    # 清除所有中间数据
    os.system(f"rmdir /q /s {temp_path}")


def down(url):
    # 获取网页源代码并获取第一层m3u8文件URL
    # movie_name:第1集, m3u8_url:https://hnzy.bfvvs.com/play/Pdy96YEd/index.m3u8
    m3u8_url, movie_name = first_m3u8_url(url)
    # 下载m3u8文件
    m3u8_path = f".\\{movie_name}\\temp.m3u8"
    down_m3u8(m3u8_url, m3u8_path)
    # 异步下载所有ts文件
    loop = asyncio.get_event_loop()
    loop.run_until_complete(dow_ts(m3u8_path))
    # 获取key
    key = get_key(m3u8_path)
    loop2 = asyncio.get_event_loop()
    loop2.run_until_complete(dec_ts(m3u8_path, key))
    print("解密完成！！！")
    loop.close()
    loop2.close()
    # 合并所有ts文件为MP4文件
    merge_ts(m3u8_path, movie_name)



def mainGUI():
    win = Tk()
    win.geometry("600x400+600+300")
    win.title("点燃我，温暖你下载")
    win.mainloop()





if __name__ == '__main__':
    temp_url = "https://www.shukeju.org/kanvodplay/386176-3-36/"
    # down(temp_url)
    # main()  
    mainGUI()