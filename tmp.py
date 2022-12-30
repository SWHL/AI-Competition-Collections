# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com

from bs4 import BeautifulSoup

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

with open('1.txt', 'w', encoding='utf-8') as f:
    for v in output_list:
        f.write(f'{v}\n')
