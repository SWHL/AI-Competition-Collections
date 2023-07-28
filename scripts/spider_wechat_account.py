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
import yaml
from fake_useragent import UserAgent


class SpiderArticleWeChat(object):
    def __init__(self, cookie, token) -> None:
        self.args = self.read_yaml("args.yaml")

        self.URL = self.args["URL"]
        self.nlp_keywords = self.args["Type"]["NLP"]["keywords"]
        self.nlp_invaild_keywords = self.args["Type"]["NLP"]["invalid_keywords"]

        self.others_keywords = self.args["Type"]["Others"]["keywords"]
        self.others_invalid_keywords = self.args["Type"]["Others"]["invalid_keywords"]
        self.interview_keywords = self.args["Type"]["Interview"]["keywords"]

        self.md_dict = {
            0: self.args["Type"]["NLP"]["md_path"],
            1: self.args["Type"]["Others"]["md_path"],
            2: self.args["Type"]["Interview"]["md_path"],
        }

        self.account_fakeid = self.args["FakeID"]

        self.headers = {"Cookie": cookie, "User-Agent": str(str(UserAgent().random))}
        self.params = {
            "action": "list_ex",
            "begin": "0",
            "count": "5",
            "fakeid": "MzIwNDA5NDYzNA==",
            "type": "9",
            "token": token,
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1",
        }
        self.cur_date = datetime.strftime(datetime.now(), "%Y-%m-%d")
        self.have_valid_nums = 0

    def __call__(self, spider_pages=3):
        begin_list = [str(i) for i in range(0, spider_pages * 5, 5)]

        for one_account, fake_id in self.account_fakeid.items():
            self.params["fakeid"] = fake_id

            spider_content_list = []
            for begin in begin_list:
                self._random_sleep()

                self.params["begin"] = begin
                msg_list = self._get_url_response()

                if msg_list:
                    spider_content_list.extend(msg_list)
            self.process_content(spider_content_list)

        if self.have_valid_nums > 0:
            return True
        return False

    def process_content(self, content_list):
        for one_line in content_list:
            create_time, title, link = one_line

            # 根据title来决定写入哪个md
            idx = self._which_data(title)
            if idx is None:
                continue

            # 读取指定md文件的已有数据
            md_path = self.md_dict[idx]
            already_data = self.read_txt(md_path)

            # 按 --- 来切分为两部分
            splid_idx = already_data.index("---")
            head = already_data[: splid_idx + 1]
            left = already_data[splid_idx + 1 :]

            # 当前抓取到的文章没有出现在已有列表中
            if not self.is_appear(title, left):
                competition_info = f"- [【{self.cur_date}】{title}]({link})"

                head.append(competition_info)
                self.write_txt(md_path, head + left)
                self.have_valid_nums += 1

    def _get_url_response(
        self,
    ):
        resp = requests.get(
            self.URL,
            headers=self.headers,
            params=self.params,
            verify=False,
            timeout=60,
        )
        msg = resp.json()
        if "app_msg_list" in msg:
            res = []
            for item in msg["app_msg_list"]:
                create_time = self._get_time(item["create_time"])
                title, link = item.get("title"), item.get("link")
                res.append([create_time, title, link])
            return res
        return None

    def _random_sleep(self, sleep_second: int = 10):
        time.sleep(random.randint(1, sleep_second))

    def _get_time(self, seconds_str):
        create_time = datetime.fromtimestamp(float(seconds_str))
        article_date = datetime.strftime(create_time, "%Y-%m-%d")
        return article_date

    def _which_data(self, title: str) -> int:
        if not self.is_contain_str(
            title, self.nlp_invaild_keywords
        ) and self.is_contain_str(title, self.nlp_keywords):
            return 0

        if not self.is_contain_str(
            title, self.others_invalid_keywords
        ) and self.is_contain_str(title, self.others_keywords):
            return 1

        if self.is_contain_str(title, self.interview_keywords):
            return 2
        return None

    def read_md_data_split(self, md_path):
        already_data = self.read_txt(md_path)
        idx = already_data.index("---")
        first, second = already_data[: idx + 1], already_data[idx + 1 :]
        return first, second

    @staticmethod
    def read_txt(txt_path: str) -> list:
        with open(txt_path, "r", encoding="utf-8") as f:
            data = list(map(lambda x: x.rstrip("\n"), f))
        return data

    @staticmethod
    def write_txt(save_path: str, content: list, mode="w"):
        if isinstance(content, str):
            content = [content]
        with open(save_path, mode, encoding="utf-8") as f:
            for value in content:
                f.write(f"{value}\n")

    @staticmethod
    def is_contain_str(
        sentence: str,
        key_words: Union[str, List],
    ) -> bool:
        """sentences中是否包含key_words中任意一个"""
        sentence = sentence.lower()
        return any(i.lower() in sentence for i in key_words)

    @staticmethod
    def is_appear(key_word: str, sentence_list: List) -> bool:
        """key_word是否在sentence_list中出现过"""
        key_word = key_word.lower()
        return any(key_word in sentence.lower() for sentence in sentence_list)

    @staticmethod
    def read_yaml(yaml_path):
        with open(yaml_path, "rb") as f:
            data = yaml.load(f, Loader=yaml.Loader)
        return data


def main(args):
    spider = SpiderArticleWeChat(args.cookie, args.token)
    res = spider()
    if res:
        print(1)
    else:
        print(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cookie",
        type=str,
        default="""RK=49MwDvMBSK; ptcz=a23d9b1a2561d2e360381c6184a138f490764fa976bc0544743b1edd3d2ce9e0; ua_id=kzAc4J4XjeTMP6UDAAAAAPsMj9BTC19udOss8TlZJCQ=; wxuin=59623090480645; mm_lang=zh_CN; pgv_pvid=1789084112; ts_uid=6233800786; __root_domain_v=.weixin.qq.com; _qddaz=QD.750560569830378; o_cookie=1226778264; fqm_pvqid=0b780fa5-8d7f-498d-9d51-2dfc09511b15; tvfe_boss_uuid=e5ba87a04633837f; pac_uid=1_1226778264; ts_refer=file.daihuo.qq.com/; rewardsn=; wxtokenkey=777; uuid=39f6acbff0e36567e57b212ee0173e18; rand_info=CAESIJzKJ9OVYDeaOu1EzR0chjzbAEDW9Rt5VF/r/f2pc5gr; slave_bizuin=3874891165; data_bizuin=3874891165; bizuin=3874891165; data_ticket=1Q0O6iXjsF4T4f66PTSAfUcnZKs6utij9NnJdLQmr+9NMA5UA2QCPWd8gvX5g/9E; slave_sid=bWZ6V3p6MU5YSjJyMXlLM0xKbEoxa1p0RG9OVEhXd0JZNlJ1VDNTMHpsZ2Z6eWlEQVJocGV2djZQRWpiR0d2eEhVbUJTX0dja0VQcnI2R3dsTERRdjBtWG01ZHZaWWNKZnFsY0JkbjVzZ0cxbkthcXVpcFBIZjE3anNQZ2NuQk5FVExwRUx4ekdsQTZod3l0; slave_user=gh_c4775c62f354; xid=f4cdbc87f7040878e01ed75b9f8a0421; _clck=3874891165|1|fdo|0; _clsk=1wl6i4k|1690549248546|15|1|mp.weixin.qq.com/weheat-agent/payload/record""",
    )
    parser.add_argument("--token", type=int, default=1848909564)
    args = parser.parse_args()
    main(args)
