# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from datetime import datetime

def on_config(config, **kwargs):
    config.copyright = f"Copyright &copy; {datetime.now().year+1} Maintained by SWHL."
