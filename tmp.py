# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from bs4 import BeautifulSoup


def read_txt(txt_path: str) -> list:
    if not isinstance(txt_path, str):
        txt_path = str(txt_path)

    with open(txt_path, 'r', encoding='utf-8') as f:
        data = list(map(lambda x: x.rstrip('\n'), f))
    return data


def write_txt(save_path: str, content: list, mode='w'):
    if not isinstance(save_path, str):
        save_path = str(save_path)

    if isinstance(content, str):
        content = [content]
    with open(save_path, mode, encoding='utf-8') as f:
        for value in content:
            f.write(f'{value}\n')


soup = BeautifulSoup(open('1.html', encoding='utf-8'), features="lxml")

output_list = []
trs = list(soup.body.tbody.find_all('tr'))
for tr in trs:
    td_list = list(filter(lambda x: x != '\n', tr.contents))
    for td in td_list:
        contents = td.contents
        for con in contents:
            if con == '\n':
                continue

            if isinstance(con, str):
                output_list.append(con)
            else:
                url = con.attrs['href']
                text = con.string.split('\n')
                text = list(map(lambda x: x.strip(), text))
                text = ' '.join(text)
                output_list.append(f'{text}\t{url}')

n = len(output_list)
i = 0
result = {}

title_idx_list = [i for i, v in enumerate(output_list) if 2 < len(v) < 16 and not v.startswith('20')]
result = {output_list[i]: [] for i in title_idx_list}
del result[' | ']

meet_idx = 0
while i < n - 1:
    if i in title_idx_list:
        meed_idx = i
        i += 1
        continue

    if meed_idx == 148:
        i += 1
        continue

    cur_cont = output_list[i]
    next_cont = output_list[i + 1]
    if next_cont.startswith('20'):
        # 与上一行合并
        split_line = output_list[i].split('\t')
        new_line = '\t'.join(split_line + [next_cont])
        result[output_list[meed_idx]].append(new_line)
    else:
        # 比赛帖子
        result[output_list[meed_idx]].append(output_list[i])

    i += 1

root_path = 'CV'
# 将result内容写入到对应md中
for k, v in result.items():
    md_path = f'{root_path}/{k}.md'
    md_content = []
    for one_info in v:
        split_part = one_info.split('\t')
        if len(split_part) <= 1:
            continue

        if len(split_part) > 3:
            split_part = split_part[:2]

        try:
            name, url, date = split_part
        except ValueError:
            name, url = split_part
            date = '-'

        content = f'- [【{date}】{name}]({url})'
        md_content.append(content)
    write_txt(md_path, md_content)
print('ok')


# with open('1.txt', 'w', encoding='utf-8') as f:
#     for v in output_list:
#         f.write(f'{v}\n')
