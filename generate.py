import os

import yaml
from jinja2 import Template, Environment, FileSystemLoader


datas_types = {}
for f in os.listdir("datas"):

    file_name = os.path.splitext(f)[0]
    with open(os.path.join('datas', f), 'r') as stream:
	    datas = yaml.load(stream)
    datas_types[file_name] = datas

print datas_types

env = Environment(loader=FileSystemLoader(""))
tpl = env.get_template("template.html")
output = tpl.render(
    datas_types=datas_types)

path = os.path.join("index.html")
with open(path, "wb") as fh:
    fh.write(output.encode('utf-8'))