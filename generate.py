"""
-------------------
Portfolio generator
-------------------

Usage:
    generate.py create <name> [--dst <project-path>]
    generate.py build <project-path>

-h --help    show this

'create' will make a folder called <name> with a 
    default project inside and should be run only once per project
'build' will generate an index.html from your
    project files and should be run after every change

"""
import os
import pip
from distutils.dir_util import copy_tree
import shutil

try: import yaml
except ImportError: pip.main(["install", "yaml"])

try: import spectra
except ImportError: pip.main(["install", "spectra"])

try: import markdown
except ImportError: pip.main(["install", "markdown"])

try: from docopt import docopt
except ImportError: pip.main(["install", "docopt"])

try: from jinja2 import Template, Environment, FileSystemLoader
except ImportError: pip.main(["install", "jinja2"])


SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
arguments = docopt(__doc__, argv=None, help=True, version=None, options_first=False)


if arguments['create']:
    name = arguments['<name>']
    path = arguments['<project-path>']

    if path is None:
        path = ''
    path = os.path.join(path, name)

    if not os.path.exists(path):
        os.makedirs(path)

    # MAKE DEFAULT PROJECT FROM SAMPLE FILES
    shutil.copy(os.path.join(SCRIPT_PATH, 'sample','settings.yaml'), path)
    shutil.copy(os.path.join(SCRIPT_PATH, 'sample','design.yaml'), path)
    shutil.copy(os.path.join(SCRIPT_PATH, 'sample','fashion.yaml'), path)


if arguments['build']:
    FILE_PATH = arguments['<project-path>']
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
            yaml_items = yaml.load(stream)

            # MARKDOWN PARSING
            for item_name, item_obj in yaml_items.items():
                markdown_descr = markdown.markdown(item_obj['description'])

                # REMOVE <p></p> wrap
                p, np = '<p>', '</p>'
                markdown_descr_clean = markdown_descr[len(p):-len(np)]

                item_obj['description'] = markdown_descr_clean

            datas_types[file_name] = yaml_items

    # LOAD PALETTE
    with open(os.path.join(SCRIPT_PATH, "palette.yaml"), 'r') as stream:
        palette = yaml.load(stream)

    box_background_color = palette.get('box_background')
    if box_background_color is None:
        # GENERATE box_background
        color = spectra.html(palette['website_background'])
        palette['box_background'] = color.darken(18).hexcode

    headers_color = palette.get('headers')
    if headers_color is None:
        # GENERATE headers
        color = spectra.html(palette['website_background'])
        palette['headers'] = color.darken(18).hexcode

    box_headers_color = palette.get('box_headers')
    if box_headers_color is None:
        # GENERATE box_headers
        color = spectra.html(palette['box_background'])
        palette['box_headers'] = color.darken(16).hexcode

        # GENERATE box_description
        color = spectra.html(palette['box_background']).to("lab")
        lab = list(color.values)
        lab[0] = 0
        color = spectra.lab(*lab)
        palette['box_description'] = color.hexcode

    labels_color = palette.get('labels')
    if labels_color is None:
        # GENERATE labels
        palette['labels'] = palette['box_headers']


    # CREATE EXPORT PATH
    EXPORT_PATH = os.path.join(FILE_PATH, 'export')
    if not os.path.exists(EXPORT_PATH):
        os.mkdir(EXPORT_PATH)
        copy_tree(os.path.join(SCRIPT_PATH, "datas"), os.path.join(EXPORT_PATH, "datas"))

    # RENDER TEMPLATE
    env = Environment(loader=FileSystemLoader(ABS_PATH))
    tpl = env.get_template("template.html")
    output = tpl.render(datas_types=datas_types, settings=settings, palette=palette)

    # GENERATE INDEX.HTML
    with open(os.path.join(EXPORT_PATH, "index.html"), "wb") as fh:
        fh.write(output.encode('utf-8'))
