# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from datetime import datetime
from pathlib import Path

import yaml


class ConvertMDToHugo():
    def __init__(self):
        self.root_dir = Path(__file__).resolve().parent.parent
        self.save_dir = self.root_dir / 'content'

        self.cur_date = datetime.strftime(datetime.now(), '%Y-%m-%d')

        cur_dir = Path(__file__).resolve().parent
        config = self.read_yaml(cur_dir / 'convert.yaml')

        global_config = config.get('Global')
        self.author = global_config.get('Author')
        self.author_email = global_config.get('AuthorEmail')
        self.children = global_config.get('Children')

        self.home_config = config.get('Home')
        self.cv_config = config.get('CV')
        self.type_list = [
            config.get('NLP'),
            config.get('Others'),
            config.get('Speech'),
            config.get('Interview')
        ]

    def __call__(self,):
        self.convert_cv()
        for one_type in self.type_list:
            self.convert_one_type(one_type)
        self.create_home_index_md()

    def convert_one_type(self, config):
        title = config.get('title')
        menu_title = config.get('menuTitle')
        weight = config.get('weight')
        badge_list = config.get('badge_list', None)

        md_content = [
            '---',
            f'title: "{title}"',
            f'menuTitle: "{menu_title}"',
            f'date: {self.cur_date}',
            'draft: false',
            f'weight: {weight}',
            'LastModifierDisplayName: "SWHL"',
            'LastModifierEmail: "liekkaskono@163.com"',
            '---',
            ' ',
            '> 从他人比赛经验中，总是可以学到很多东西',
            ' ',
        ]

        if badge_list:
            for badge in badge_list:
                badge_shortcut = f'{{{{% badge style="info" icon=" " title=" " %}}}}{badge}{{{{% /badge %}}}}'
                md_content.append(badge_shortcut)
            md_content.append(' ')
        md_content.extend(['---', ' '])

        ori_md_path = self.root_dir / f'{menu_title}.md'
        ori_md_data = self.read_txt(ori_md_path)

        short_line_idx = ori_md_data.index('---')
        ori_md_data = ori_md_data[short_line_idx + 1:]
        ori_md_data = [v.replace('###', '######') if v == '### 友情链接' else v
                       for v in ori_md_data]

        save_md_dir = self.save_dir / menu_title
        self.mkdir(save_md_dir)
        save_md_path = save_md_dir / '_index.md'

        md_content.extend(ori_md_data)
        self.write_txt(save_md_path, md_content)

    def convert_cv(self,):
        cur_cv_dir = self.root_dir / 'CV'
        save_cv_dir = self.save_dir / 'CV'
        self.mkdir(save_cv_dir)

        cv_weight_dict = self.cv_config.get('cv_weight_dict')

        cv_list = list(cur_cv_dir.iterdir())
        for cv_path in cv_list:
            md_name = cv_path.stem
            md_content = self.read_txt(cv_path)

            # 定义前缀
            prefix_list = [
                '---',
                f'title: "{md_name}"',
                f'date: {self.cur_date}',
                'draft: false',
                f'weight: {cv_weight_dict[md_name]}',
                f'LastModifierDisplayName: "{self.author}"',
                f'LastModifierEmail: "{self.author_email}"',
                '---',
                ' '
            ]

            prefix_list.extend(md_content)
            save_path = save_cv_dir / f'{md_name}.md'
            self.write_txt(save_path, prefix_list)

        self.create_cv_index_md(save_cv_dir / '_index.md')

    def create_cv_index_md(self, save_path: str):
        title = self.cv_config.get('title')
        weight = self.cv_config.get('weight')

        prefix_content = [
            '---',
            f'title: "{title}"',
            'menuTitle: "CV"',
            f'weight: {weight}',
            '---',
            ' ',
            self.children
        ]
        self.write_txt(str(save_path), prefix_content)

    def create_home_index_md(self):
        archetype = self.home_config.get('archetype')
        title = self.home_config.get('title')
        start_key = self.home_config.get('start_key')
        end_key = self.home_config.get('end_key')

        prefix_content = [
            '---',
            f'archetype: "{archetype}"',
            f'title: "{title}"',
            '---',
            ' ',
            self.children,
            ' '
        ]

        readme_path = self.root_dir / 'README.md'
        ori_readme = self.read_txt(readme_path)

        # 找到竞赛公众号的索引
        start_idx, end_idx = 0, 0
        for i, v in enumerate(ori_readme):
            if start_key in v:
                start_idx = i

            if end_key in v:
                end_idx = i
        home_content = ori_readme[start_idx:end_idx + 1]
        home_content = [v.replace('###', '######') if '###' in v else v
                        for v in home_content]
        prefix_content.extend(home_content)

        save_path = self.save_dir / '_index.md'
        self.write_txt(save_path, prefix_content)

    @staticmethod
    def mkdir(dir_path):
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def read_txt(txt_path: str) -> list:
        if not isinstance(txt_path, str):
            txt_path = str(txt_path)

        with open(txt_path, 'r', encoding='utf-8') as f:
            data = list(map(lambda x: x.rstrip('\n'), f))
        return data

    @staticmethod
    def write_txt(save_path: str, content: list, mode='w'):
        if not isinstance(save_path, str):
            save_path = str(save_path)

        if isinstance(content, str):
            content = [content]
        with open(save_path, mode, encoding='utf-8') as f:
            for value in content:
                f.write(f'{value}\n')

    @staticmethod
    def read_yaml(yaml_path):
        with open(yaml_path, 'rb') as f:
            data = yaml.load(f, Loader=yaml.Loader)
        return data


if __name__ == '__main__':
    converter = ConvertMDToHugo()
    converter()
