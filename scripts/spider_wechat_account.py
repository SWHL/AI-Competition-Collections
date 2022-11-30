# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
# modified from https://zhuanlan.zhihu.com/p/48402858
import argparse
import random
import time
from datetime import datetime
from typing import List, Union

import requests
from fake_useragent import UserAgent


class SpiderArticleWeChat(object):
    def __init__(self, cookie, token) -> None:
        self.URL = "https://mp.weixin.qq.com/cgi-bin/appmsg"
        self.others_key_words = ['赛题总结', '竞赛总结', '比赛总结', '图数据',
                                 '风险趋势预测', '异常行为分析', '关联融合计算', '容量预测']
        self.nlp_key_words = ['NLP', '情感识别', 'BERT', '问题匹配']

        self.md_dict = {
            0: '../NLP.md',
            1: '../Others.md',
        }

        self.account_fakeid = {
            'Coggle数据科学': 'MzIwNDA5NDYzNA==',
            '一碗数据汤': 'MzI5ODQxMTk5MQ=='
        }

        self.headers = {
            "Cookie": cookie,
            "User-Agent": str(str(UserAgent().random))
        }
        self.params = {
            "action": "list_ex",
            "begin": "0",
            "count": "5",
            "fakeid": self.account_fakeid['Coggle数据科学'],
            "type": "9",
            "token": token,
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1"
        }

    def __call__(self, begin: str = '0',):
        self.params["begin"] = str(begin)
        cur_date = datetime.strftime(datetime.now(), '%Y-%m-%d')

        is_valid_article = False
        for one_account, fake_id in self.account_fakeid.items():
            self._random_sleep()

            self.params['fakeid'] = fake_id
            msg = self._get_url_response()

            if "app_msg_list" in msg:
                for item in msg["app_msg_list"]:
                    article_date = self._get_time(item['create_time'])
                    title, link = item.get('title'), item.get('link')

                    # 根据title来决定写入哪个md
                    idx = self._which_data(title)
                    if idx is None:
                        continue

                    # 读取指定md文件的已有数据
                    md_path = self.md_dict[idx]
                    already_data = self.read_txt(md_path)

                    # 按 --- 来切分为两部分
                    splid_idx = already_data.index('---')
                    head = already_data[:splid_idx+1]
                    left = already_data[splid_idx+1:]

                    # 当前抓取到的文章没有出现在已有列表中
                    if not self.is_appear(title, left):
                        competition_info = f'#### [【{cur_date}】{title}]({link})'

                        head.append(competition_info)
                        self.write_txt(md_path, head + left)
                        is_valid_article = True

        if is_valid_article:
            return True
        return False

    def _get_url_response(self,):
        resp = requests.get(self.URL,
                            headers=self.headers,
                            params=self.params,
                            verify=False)
        msg = resp.json()
        return msg

    def _random_sleep(self, sleep_second: int = 10):
        time.sleep(random.randint(1, sleep_second))

    def _get_time(self, seconds_str):
        create_time = datetime.fromtimestamp(float(seconds_str))
        article_date = datetime.strftime(create_time, '%Y-%m-%d')
        return article_date

    def _which_data(self, title: str) -> int:
        if self.is_contain_str(title, self.others_key_words):
            return 1
        elif self.is_contain_str(title, self.nlp_key_words):
            return 0
        else:
            return None

    def read_md_data_split(self, md_path):
        already_data = self.read_txt(md_path)
        idx = already_data.index('---')
        first, second = already_data[:idx+1], already_data[idx+1:]
        return first, second

    @staticmethod
    def read_txt(txt_path: str) -> list:
        with open(txt_path, 'r', encoding='utf-8') as f:
            data = list(map(lambda x: x.rstrip('\n'), f))
        return data

    @staticmethod
    def write_txt(save_path: str, content: list, mode='w'):
        if isinstance(content, str):
            content = [content]
        with open(save_path, mode, encoding='utf-8') as f:
            for value in content:
                f.write(f'{value}\n')

    @staticmethod
    def is_contain_str(src_text: Union[str, List],
                       given_str_list: Union[str, List],) -> bool:
        for one_value in given_str_list:
            if src_text.__contains__(one_value):
                return True
        return False

    @staticmethod
    def is_appear(title, left):
        for one in left:
            if title in one:
                return True
        return False


def main(args):
    spider = SpiderArticleWeChat(args.cookie, args.token)
    res = spider()
    if res:
        print(1)
    else:
        print(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cookie', type=str, required=True)
    parser.add_argument('--token', type=int, required=True)
    args = parser.parse_args()
    main(args)
