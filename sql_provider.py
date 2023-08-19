import os
from string import Template


class SQLProvider:
    def __init__(self, file_path):
        self._scripts = {}
        for file in os.listdir(file_path):
            self._scripts[file] = Template(open(f'{file_path}/{file}').read())
    #         Template - substitute - подставляет параметры вместо знаков $$

    def get(self, name, **kwargs):
        _str = self._scripts.get(name, '').substitute(**kwargs)
        _a = _str.encode('cp1251', 'replace')
        return _a.decode('utf-8', 'replace')
