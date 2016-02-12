"""Usage:
    generate.py makeproject <name> [--dst <path>]
    generate.py build <path>

-h --help    show this

"""
import os
from distutils.dir_util import copy_tree

import yaml
from docopt import docopt
from jinja2 import Template, Environment, FileSystemLoader

arguments = docopt(__doc__, argv=None, help=True, version=None, options_first=False)
print arguments


if arguments['makeproject']:
    name = arguments['<name>']
    path = arguments['<path>']

    if path is None:
        path = ''
    path = os.path.join(path, name)

    if not os.path.exists(path):
        os.makedirs(path)

if arguments['build']:
    path = arguments['<path>']

    datas_types = {}
    for f in os.listdir(path):
        file_name = os.path.splitext(f)[0]
        file_ext = os.path.splitext(f)[-1]

        if not os.path.isfile(os.path.join(path, f)):
            continue
        if not file_ext == '.yaml':
            continue

        if file_name == 'settings':
            with open(os.path.join(path, f), 'r') as stream:
                settings = yaml.load(stream)
            continue

        with open(os.path.join(path, f), 'r') as stream:
            datas_types[file_name] = yaml.load(stream)

    env = Environment(loader=FileSystemLoader(""))
    tpl = env.get_template("template.html")
    output = tpl.render(
        datas_types=datas_types, settings=settings)

    export_path = os.path.join(path, 'export')
    if not os.path.exists(export_path):
        os.mkdir(export_path)
    copy_tree("datas", os.path.join(export_path, "datas"))

    with open(os.path.join(export_path, "index.html"), "wb") as fh:
        fh.write(output.encode('utf-8'))
