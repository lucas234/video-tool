# coding=utf-8
# @Time    : 2021/4/26 15:13
# @Author  : lucas
# @File    : utils.py
# @Project : pyqt
# @Software: PyCharm
from functools import wraps
from pathlib import Path
from datetime import datetime, timedelta
from urllib.request import urlopen
import time
import re
import os
import shutil
import sqlite3
import hashlib
import pickle
import json


def timer(func):
    @wraps(func)
    def _time(*args):
        start = time.time()
        result = func(*args)
        print(f"func: {func.__name__} runs for {time.time() - start}s.")
        return result

    return _time


class Constant(object):
    # m3u8 播放器
    PLAYERS = {
        "VLC": r"C:\Users\liul8\Downloads\vlc-3.0.12-win32\vlc-3.0.12\vlc.exe",
        "6029解析": "https://www.dplayer.tv/?url=",
        "默认解析": "https://api.69ne.com/?url=",
        "思古解析": "https://api.sigujx.com/?url=",
        "BL解析": "https://vip.bljiex.com/?v=",
        "万能解析": "https://www.cuan.la/?url=",
        "IK解析": "https://vip.ikjiexi.top/?url=",
        "17kyun解析": "http://17kyun.com/api.php?url=",
        "V6解析": "https://api.v6.chat/?url=",
        "免费云解析": "https://jx.ergan.top/?url=",
        "步步高解析": "http://jx.yparse.com/?url=",
        "66解析接口": "https://vip.66parse.club/?url=",
        "简傲云解析": "https://vip.mcyanyu.com/?url=",
        "猫视频解析": "https://maosp.me:7788/1/?url=",
        "OK解析": "https://okjx.cc/?url=",
    }


class DBConnectors(object):
    def __init__(self, sqlite):
        self.conn = sqlite3.connect(sqlite, check_same_thread=False)
        self.cursor = self.conn.cursor()

    @timer
    def query(self, _sql):
        self.cursor.execute(_sql)
        # row = self.cursor.fetchone()
        # results = []
        # while row:
        #     results.append(row)
        #     row = self.cursor.fetchone()
        # return results
        return [result for result in self.cursor]

    @timer
    def execute(self, _sql):
        """insert,update,delete some data"""
        try:
            count = self.cursor.execute(_sql).rowcount
            self.conn.commit()
            print('Rows inserted/updated/deleted: ' + str(count))
        except Exception as e:
            print(e)
            self.conn.rollback()

    def close(self):
        self.conn.close()


def str_2_date(date_str):
    """2021-01-24 20:35:39"""
    if not date_str:
        return ""
    return datetime.strptime(date_str.split(".")[0], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")


def str_2_time(date_str):
    """2021-01-24 20:35:39"""
    if not date_str:
        return None
    return datetime.strptime(date_str.split(".")[0], "%Y-%m-%d %H:%M:%S")


_cache = {}


def memorize(duration=-1):
    con = DBConnectors("video_tool.db")

    def _set_db(sig, data, args):
        print(f"the id is: {sig}")
        data = json.dumps(data)
        query_sql = f"select data, createDate, updateDate, expire from resource where sig='{sig}'"
        insert_sql = f"insert into resource(name, sig, data, expire) values('{args.wd}', '{sig}', '{data}', '{duration}')"
        update_sql = f"update resource set data='{data}',updateDate='{datetime.now()}',expire='{duration}' where sig='{sig}'"
        result = con.query(query_sql)
        if result:
            con.execute(update_sql)
        else:
            con.execute(insert_sql)

    def _get_db(sig):
        sql = f"select data, createDate, updateDate, expire from resource where sig='{sig}'"
        result = con.query(sql)
        print("从数据库中取")
        if result:
            data, create_date, update_date, expire = result[0]
            if duration == -1:  # 永不过期
                return data
            start_time = update_date if update_date else create_date
            now = datetime.now()
            sec = int(expire.split()[0]) * 24 * 60 * 60 if 'd' in expire else int(expire)
            if not str_2_time(start_time) + timedelta(seconds=sec) <= now:
                return data

    def _get_cache(key):
        # 从内存中读取
        if key in _cache:
            if _is_obsolete(_cache[key], duration):
                print("从临时缓存读取")
                return _cache[key]['value']
        # 从数据库中读取
        db_data = _get_db(key)
        if db_data:
            return db_data

    def _set_cache(key, data, args):
        # 保存在缓存中
        _cache[key] = {
            'value': data,
            'time': time.time()}
        # 保存到数据库
        _set_db(key, data, args)

    def _is_obsolete(entry, duration_):
        """是否过期"""
        if duration_ == -1:  # 永不过期
            return True
        return time.time() - entry['time'] <= duration_

    def _compute_key(function, args, kw):
        """序列化并求其哈希值"""
        key = pickle.dumps((function.__name__, args[0].wd, kw))
        return hashlib.sha1(key).hexdigest()

    def _memoize(function):

        @wraps(function)
        def __memoize(*args, **kw):
            key = _compute_key(function, args, kw)
            # 是否存在临时缓存中
            cache_data = _get_cache(key)
            if cache_data:
                return cache_data
            print("执行函数读取")
            result = function(*args, **kw)
            # 存储结果到内存存、数据库中
            _set_cache(key, result, *args)
            return result
        return __memoize
    return _memoize


def singleton(cls):
    _instance = {}

    @wraps(cls)
    def _singleton(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return _singleton


def get_icon_dir(icon):
    return str(Path(__file__).parent.joinpath("assets", icon))


def downloads_dir():
    return Path('~').expanduser().joinpath("Downloads")


@timer
def is_valid_m3u8_url(url):
    """通过urllib 校验，可能会多耗费时间"""
    try:
        urlopen(url)
    except Exception as e:
        print(f"Not a real URL, msg: {e}")
        return False
    return True if "m3u8" in url else False


@timer
def is_m3u8_url(url):
    """通过正则表达式，比较快速校验"""
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)\.m3u8$', re.IGNORECASE)
    return True if url and regex.search(url) else False

@timer
def merge_file2(path_, filename, format="mp4"):
    r"""
      copy /b d:\ts_files\*.ts  d:\fnew.ts
    """
    print("开始合并...")
    path_ = Path(path_)
    merged_file = path_.joinpath(f"{filename}.{format}")
    fragments_path = path_.joinpath(filename)
    os.chdir(fragments_path)
    os.system(f'copy /b * "{merged_file}"')
    print("结束合并...")
    shutil.rmtree(fragments_path)


def file_walker(_download_path):
    file_list = []
    for root, dirs, files in os.walk(_download_path):  # generator
        for file in files:
            _path = os.path.join(root, file)
            file_list.append(_path)
    return file_list

@timer
def merge_file(path_, filename, format="mp4"):
    path_ = Path(path_)
    fragments_path = path_.joinpath(filename)
    file_list = file_walker(fragments_path)
    file_path = path_.joinpath(f"{filename}.{format}")
    with open(file_path, 'wb+') as fw:
        for i in range(len(file_list)):
            fw.write(open(file_list[i], 'rb').read())
    shutil.rmtree(fragments_path)


def get_db():
    return DBConnectors("video_tool.db")


def store_data(name=None, episode=None, url=None, downloaded=None, total=None, begin=False):
    insert_sql = f"insert into downloadList(name,episode,url,downloaded,total) " \
                 f"values('{name}','{episode}','{url}','{downloaded}','{total}')"
    query_sql = f"select downloaded, total from downloadList where url='{url}'"
    con = get_db()
    result = con.query(query_sql)
    if result:
        if begin:
            update_sql = f"update downloadList set downloaded='{downloaded}' where url='{url}'"
        else:
            update_sql = f"update downloadList set downloaded='{downloaded+result[0][0]}' where url='{url}'"
        print("更新了数据")
        con.execute(update_sql)
    else:
        print("插入了数据")
        con.execute(insert_sql)


def get_download_list():
    print("从数据库读取下载列表")
    res = get_db().query("select episode,downloaded,total,url from downloadList")
    return {i[3]: [i[0], i[1] * 100 // i[2]] for i in res}


def get_download_dir():
    print("从数据库读取下载路径")
    res = get_db().query("select path from setting")
    return Path(res[0][0]) if res else downloads_dir()


def get_process(url):
    print("从数据库读取下载进度")
    res = get_db().query(f"select downloaded,total,status from downloadList where url='{url}'")
    if res:
        return res[0][0], res[0][1], res[0][2]


def init_db():
    download_list = """
                create table IF NOT EXISTS downloadList(
                    id integer PRIMARY KEY autoincrement,
                    name varchar,
                    episode varchar,
                    url varchar,
                    downloaded integer default (0),
                    total integer,
                    status integer default (0),
                    createDate datetime default (datetime('now', 'localtime')),
                    updateDate datetime
                );"""
    resource = """
                create table IF NOT EXISTS resource(
                    id integer PRIMARY KEY autoincrement,
                    name varchar not null,
                    data JSON,
                    sig varchar UNIQUE,
                    expire varchar default ('1 d'),
                    isActive bool default (1),
                    createDate datetime default (datetime('now', 'localtime')),
                    updateDate datetime
                );"""
    setting = """
                create table IF NOT EXISTS setting(
                    id integer PRIMARY KEY autoincrement,
                    modes integer,
                    path varchar,
                    concurrencyNum integer,
                    themeStyle varchar,
                    createDate datetime default (datetime('now', 'localtime')),
                    updateDate datetime
                );"""
    insert_setting = f"insert into setting(modes, path, concurrencyNum, themeStyle) values(0, '{downloads_dir()}', 8, 'Fusion')"
    con = get_db()
    con.execute(resource)
    con.execute(setting)
    con.execute(download_list)
    if not con.query("select * from setting"):
        con.execute(insert_setting)

    # 将所有正在下载的任务状态改为1暂定（0->1）
    data = con.query("select id from downloadList where status=0")
    if data:
        sql = f"update downloadList set status=1 where id in ({','.join(str(i[0]) for i in data)})"
        con.execute(sql)


@memorize(300000)
def a_hard_function(a):
    print("getting result")
    from time import sleep
    sleep(2)
    return a


if __name__ == "__main__":
    sq = "insert into resource(name,data) values('哪吒', '12123213')"
    # s = get_db()
    # init_db()
    # s.execute(sq)
    # print(s.query("select * from downloadList"))
    # data = s.query("select id from downloadList where status=2")
    # print(data)
    # print(s.execute("delete from downloadList where id in (4,5,6,7,8,9,10,11)"))
    # print(s.execute("update downloadList set downloaded=200 where id =12"))
    # print(get_download_list())

    # p = Path(__file__).parent
    # merge_file(p, "第13集")
    # merge_file2(p, "第13集")

    # a_hard_function("山海情")
    # a_hard_function("山海情")
    # a_hard_function("山海情")

    # print(is_valid_m3u8_url(""))
    # print(is_valid_m3u8_url('http://foobar.dk'))
    # print(is_valid_m3u8_url('http://chyd-sn.wasu.tv/tbvideo/20141108/a5715565-44de-43ff-864d-2e8c5011e361.m3u8'))
    # print(is_m3u8_url('https://foobar.dk'))
    # print(is_m3u8_url('https://chyd-sn.wasu.tv/tbvideo/20141108/a5715565-44de-43ff-864d-2e8c5011e361.m3u8'))
