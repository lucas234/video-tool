# @Time    : 2021/4/29 17:39
# @Author  : lucas
# @File    : search_download.py
# @Project : pyqt5
# @Software: PyCharm
import requests
import os
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor as Pool
from functools import partial
from pathlib import Path
import json
from utils import str_2_date, store_data, memorize, downloads_dir

# https://realpython.com/python-concurrency/
# 屏蔽warning信息
requests.packages.urllib3.disable_warnings()
ROOT_DIR = downloads_dir()


class SearchResults(object):

    def __init__(self, wd):
        self.wd = wd
        self.query_string = {"wd": wd}
        self.headers = {'Content-Type': 'application/json'}
        self.url = "http://cj.bajiecaiji.com/inc/feifei3bjm3u8/index.php"
        # http://cj.1886zy.co/inc/feifei3/index.php?wd=哪吒
        # http://www.123ku.com/inc/feifei/index.php?wd=哪吒

    @property
    def results(self):
        return self.get_results(self.get_json())

    @memorize(duration=300000)
    def get_json(self):
        response = requests.request("GET", self.url, headers=self.headers, params=self.query_string)
        if response.status_code == 200:
            return response.json()

    @staticmethod
    def get_results(json_data):
        results = []
        if not json_data or json_data == "null":
            return []
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        for data in json_data['data']:
            episodes = dict()
            episodes["id"] = data["vod_id"]
            episodes["name"] = data["vod_name"]
            episodes["type"] = data["list_name"]
            episodes["date"] = str_2_date(data["vod_addtime"])
            episodes["m3u8_links"] = data["vod_url"].split()
            results.append(episodes)
        return results


class DownloadM3u8(object):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/69.0.3497.92 Safari/537.36"}
    def __init__(self, name, download_path=ROOT_DIR):
        self.name = name
        self.download_path = download_path

    def get_ts_urls(self, url: str) -> list:
        urls = []
        prefix = url.rsplit("/", 1)[0] + "/"
        content = requests.get(url, headers=self.headers).text
        # 是否存在第二层
        if "EXT-X-STREAM-INF" in content:
            lines = content.split("\n")
            for index, line in enumerate(lines):
                if ".m3u8" in line:
                    second_url = urljoin(prefix, line)
                    prefix = second_url.rsplit("/", 1)[0] + "/"
                    content = requests.get(second_url, headers=self.headers).text
        for i, line in enumerate(content.split("\n")):
            if line and not line.startswith("#EXT"):
                if line.startswith("http"):
                    # urls.append({"name": str(i)+line.split("/")[-1], "url": line})
                    urls.append({"name": f"{str(i):0>6}", "url": line})
                else:
                    # urls.append({"name": str(i)+line, "url": urljoin(prefix, line)})
                    urls.append({"name": f"{str(i):0>6}", "url": urljoin(prefix, line)})
            if "#EXT-X-KEY" in line:
                pass
        return urls

    def download(self, fragment: dict, episodes: str) -> bool:
        filename, url = fragment.values()
        # episodes_dir = root_dir.joinpath(self.name, episodes)
        # episodes_dir.mkdir(parents=True,exist_ok=True)
        file_path = self.episodes_dir.joinpath(filename)
        response = requests.get(url, stream=True, verify=False)
        file_size = int(response.headers['Content-Length'])
        if os.path.exists(file_path):
            downloaded_size = os.path.getsize(file_path)
        else:
            downloaded_size = 0
        if downloaded_size >= file_size:
            print(f"{file_path.name}已经完成下载")
            return True
        self.headers.update({'Range': f'bytes={downloaded_size}-'})
        r = requests.get(url, stream=True, verify=False, headers=self.headers)
        with open(file_path, "ab") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    downloaded_size += len(chunk)
                    f.write(chunk)
                    f.flush()

    def concurrent_download(self, max_workers: int, url: str, episodes: str) -> None:
        pool = Pool(max_workers)
        # futures = []
        # for x in range(100):
        #     futures.append(pool.submit(test, x))
        # for x in as_completed(futures):
        #     print(x.result())
        results = []
        urls = self.get_ts_urls(url)
        self.episodes_dir = self.download_path.joinpath(self.name, episodes)
        self.episodes_dir.mkdir(parents=True,exist_ok=True)
        init_num = len(list(self.episodes_dir.iterdir()))
        init_num = init_num - 3 if init_num >= 3 else init_num
        # 保存到数据库
        store_data(self.name, episodes, url, init_num, len(urls), True)
        for result in pool.map(partial(self.download, episodes=episodes), urls[init_num:]):
            results.append(result)
            if not result:
                yield 1


if __name__ == "__main__":
    pass
    # 测试搜索
    # print(SearchResults("哪吒").results)
    # print(SearchResults("山海情").get_json())
    #测试下载
    # 山海情 https://v5.szjal.cn/20210112/uEqxa53j/index.m3u8  https://v5.szjal.cn/20210112/ebYB5eFk/index.m3u8
    # url = "https://n1.szjal.cn/20210402/SSYsYCRM/index.m3u8" # 哪吒
    url = "https://v5.szjal.cn/20210112/ebYB5eFk/index.m3u8"
    d = DownloadM3u8("山海情", ROOT_DIR)
    for i in d.concurrent_download(4, url, "第2集"):
        print(i)
