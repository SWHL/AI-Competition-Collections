# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
# modified from https://zhuanlan.zhihu.com/p/48402858
import argparse
import random
import time
from datetime import datetime

import requests
from fake_useragent import UserAgent


def read_txt(txt_path: str) -> list:
    with open(txt_path, 'r', encoding='utf-8') as f:
        data = list(map(lambda x: x.rstrip('\n'), f))
    return data


def write_txt(save_path: str, content: list, mode='w'):
    if isinstance(content, str):
        content = [content]
    with open(save_path, mode, encoding='utf-8') as f:
        for value in content:
            f.write(f'{value}\n')


class SpiderArticleWeChat(object):
    def __init__(self, fake_id, cookie, token) -> None:
        self.URL = "https://mp.weixin.qq.com/cgi-bin/appmsg"
        self.headers = {
            "Cookie": cookie,
            "User-Agent": str(str(UserAgent().random))
        }
        self.params = {
            "action": "list_ex",
            "begin": "0",
            "count": "5",
            "fakeid": fake_id,
            "type": "9",
            "token": token,
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1"
        }
        self.key_word_list = ['赛题总结', '竞赛总结']

    def __call__(self, begin: str = '0', md_path: str = '../Others.md'):
        self.params["begin"] = str(begin)
        cur_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
        time.sleep(random.randint(1, 10))

        resp = requests.get(self.URL,
                            headers=self.headers,
                            params=self.params,
                            verify=False)

        msg = resp.json()
        self.final_result = []
        if "app_msg_list" in msg:
            for item in msg["app_msg_list"]:
                create_time = datetime.fromtimestamp(float(item['create_time']))
                article_date = datetime.strftime(create_time, '%Y-%m-%d')

                title = item['title']
                link = item['link']
                if cur_date == article_date and self.have_article(title):
                    self.final_result.append(f'#### [【{cur_date}】{title}]({link})')
        self.write_to_md(md_path)

    def have_article(self, cur_title: str) -> bool:
        for one_key in self.key_word_list:
            if one_key in cur_title:
                return True
        return False

    def write_to_md(self, md_path: str):
        already_data = read_txt(md_path)
        idx = already_data.index('---')
        first, second = already_data[:idx+1], already_data[idx+1:]
        if self.final_result:
            for v in self.final_result:
                first.append(v)
            new_data_list = first + second
            write_txt(md_path, new_data_list)


def main(args):
    spider = SpiderArticleWeChat(args.fake_id, args.cookie, args.token)
    spider()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fake_id', type=str, default='MzIwNDA5NDYzNA==')
    parser.add_argument('--cookie', type=str, required=True)
    parser.add_argument('--token', type=int, required=True)
    args = parser.parse_args()

    main(args)
