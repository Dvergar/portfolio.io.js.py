"""Usage:
    generate.py createproject <name> [--dst <path>]
    generate.py build <path>

-h --help    show this

"""
import os
from distutils.dir_util import copy_tree
import shutil

import yaml
from docopt import docopt
from jinja2 import Template, Environment, FileSystemLoader

arguments = docopt(__doc__, argv=None, help=True, version=None, options_first=False)
print arguments


SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))


if arguments['createproject']:
    name = arguments['<name>']
    path = arguments['<path>']

    if path is None:
        path = ''
    path = os.path.join(path, name)

    if not os.path.exists(path):
        os.makedirs(path)

    # MAKE DEFAULT PROJECT FROM SAMPLE FILES
    shutil.copy(os.path.join(SCRIPT_PATH, 'sample','settings.yaml'), path)
    shutil.copy(os.path.join(SCRIPT_PATH, 'sample','games.yaml'), path)


if arguments['build']:
    FILE_PATH = arguments['<path>']
    PATH, _ = os.path.split(FILE_PATH)
    ABS_PATH = os.path.join(SCRIPT_PATH, PATH)

    # LOAD USER PROJECT FILES
    datas_types = {}
    for f in os.listdir(FILE_PATH):
        file_name = os.path.splitext(f)[0]
        file_ext = os.path.splitext(f)[-1]

        # FILES TO IGNORE
        if not os.path.isfile(os.path.join(FILE_PATH, f)):
            continue
        if not file_ext == '.yaml':
            continue

        # SETTING FILE
        if file_name == 'settings':
            with open(os.path.join(FILE_PATH, f), 'r') as stream:
                settings = yaml.load(stream)
            continue

        # ITEM FILES
        with open(os.path.join(FILE_PATH, f), 'r') as stream:
            datas_types[file_name] = yaml.load(stream)


    # CREATE EXPORT PATH
    EXPORT_PATH = os.path.join(FILE_PATH, 'export')
    if not os.path.exists(EXPORT_PATH):
        os.mkdir(EXPORT_PATH)
        copy_tree(os.path.join(SCRIPT_PATH, "datas"), os.path.join(EXPORT_PATH, "datas"))

    # RENDER TEMPLATE
    env = Environment(loader=FileSystemLoader(ABS_PATH))
    tpl = env.get_template("template.html")
    output = tpl.render(
        datas_types=datas_types, settings=settings)

    # GENERATE INDEX.HTML
    with open(os.path.join(EXPORT_PATH, "index.html"), "wb") as fh:
        fh.write(output.encode('utf-8'))
