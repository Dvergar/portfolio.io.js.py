# TODO +10 -10 from css
# Check http://stackoverflow.com/questions/8260490/how-to-get-list-of-all-variables-in-jinja-2-templates
# or maybe just a python file search
# JUST MAKE A THEME FOLDER AND NO GLOBAL PALETTE : palette variable names are user-defined


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


# ERROR & VALIDATION HANDLERS
# THEME VALIDATION
def theme_path_validation(THEME_PATH):
    if not os.path.exists(THEME_PATH):
        print("Theme '" + settings['theme'] + "' doesn't exist. Please set a valid theme name.")
        exit()
    else:
        print("Using theme:", settings['theme'])

# PALETTE VALIDATION
def palette_path_validation(PALETTE_PATH):
    if not os.path.exists(PALETTE_PATH):
        print("Palette '" + settings['palette'] + "' doesn't exist. Please set a valid palette name.")
        exit()
    else:
        print("Using palette:", settings['palette'])


# GENERATOR
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
    for file_name in os.listdir(FILE_PATH):
        file_root = os.path.splitext(file_name)[0]
        file_ext = os.path.splitext(file_name)[-1]

        # IGNORE DIRECTORIES
        if not os.path.isfile(os.path.join(FILE_PATH, file_name)):
            continue

        # CSS STYLING FILE
        if file_name == 'style.css':
            print("woothoo")

            continue

        # SETTING FILE
        if file_name == 'settings.yaml':
            with open(os.path.join(FILE_PATH, file_name), 'r') as stream:
                settings = yaml.load(stream)
            
            THEME_PATH = os.path.join(ABS_PATH, "themes", settings['theme'])
            theme_path_validation(THEME_PATH)

            # THEME DEFAULT PALETTE FALLBACK
            if settings.get('palette') is None:
                with open(os.path.join(THEME_PATH, "theme.yaml"), 'r') as stream:
                    theme = yaml.load(stream)
                settings["palette"] = theme["palette"]


            PALETTE_PATH = os.path.join(ABS_PATH, "palettes", settings['palette'])
            palette_path_validation(PALETTE_PATH)

            continue

        # IGNORE NON YAML FILES
        if not file_ext == '.yaml':
            continue

        # ITEM FILES
        with open(os.path.join(FILE_PATH, file_name), 'r') as stream:
            yaml_items = yaml.load(stream)

            # MARKDOWN PARSING
            for item_name, item_obj in yaml_items.items():
                markdown_descr = markdown.markdown(item_obj['description'])

                # REMOVE <p></p> wrap
                p, np = '<p>', '</p>'
                markdown_descr_clean = markdown_descr[len(p):-len(np)]

                item_obj['description'] = markdown_descr_clean

            datas_types[file_root] = yaml_items

    # LOAD PALETTE
    with open(os.path.join(PALETTE_PATH, "palette.yaml"), 'r') as stream:
        palette = yaml.load(stream)

    for i in range(1, 7):
        color_name = 'color' + str(i)
        hex_color = palette.get(color_name)

        if hex_color is None:
            if i == 1:
                palette[color_name] = "#D1D1D1"
            else:
                prev_hex_color = palette['color' + str(i-1)]
                color = spectra.html(prev_hex_color)
                palette[color_name] = color.darken(16).hexcode
        else:
            modifier = None
            split_hex_color = hex_color.split("+")
            print(split_hex_color)
            if len(split_hex_color) > 1:
                modifier = "+"
                ref_color_name, amount = split_hex_color
                print(ref_color_name)
                print(amount)
                ref_color = spectra.html(palette[ref_color_name])
                palette[color_name] = ref_color.darken(int(amount)).hexcode

    print(palette)

    # box_background_color = palette.get('box_background')
    # if box_background_color is None:
    #     # GENERATE box_background
    #     color = spectra.html(palette['website_background'])
    #     palette['box_background'] = color.darken(18).hexcode

    # headers_color = palette.get('headers')
    # if headers_color is None:
    #     # GENERATE headers
    #     color = spectra.html(palette['website_background'])
    #     palette['headers'] = color.darken(18).hexcode

    # box_headers_color = palette.get('box_headers')
    # if box_headers_color is None:
    #     # GENERATE box_headers
    #     color = spectra.html(palette['box_background'])
    #     palette['box_headers'] = color.darken(16).hexcode

    #     # GENERATE box_description
    #     color = spectra.html(palette['box_background']).to("lab")
    #     lab = list(color.values)
    #     lab[0] = 0
    #     color = spectra.lab(*lab)
    #     palette['box_description'] = color.hexcode

    # labels_color = palette.get('labels')
    # if labels_color is None:
    #     # GENERATE labels
    #     palette['labels'] = palette['box_headers']

    # CREATE EXPORT PATH & COPY DATA FILES
    EXPORT_PATH = os.path.join(FILE_PATH, 'export')
    if not os.path.exists(EXPORT_PATH):
        os.mkdir(EXPORT_PATH)
        copy_tree(os.path.join(SCRIPT_PATH, "datas"), os.path.join(EXPORT_PATH, "datas"))

    # COPY CSS THEME FILE TO PROJECT
    shutil.copy(os.path.join(THEME_PATH, 'style.css'), os.path.join(EXPORT_PATH, "datas"))

    # JINJA RENDERING
    env = Environment(loader=FileSystemLoader(THEME_PATH))
    tpl = env.get_template("template.html")
    css = env.get_template("style.css")
    tpl_output = tpl.render(datas_types=datas_types, settings=settings, palette=palette)
    css_output = css.render(palette=palette)

    # GENERATE INDEX.HTML
    INDEX_FULL_PATH = os.path.join(EXPORT_PATH, "index.html")
    with open(INDEX_FULL_PATH, "wb") as fh:
        fh.write(tpl_output.encode('utf-8'))

    # GENERATE STYLE.CSS
    STYLE_FULL_PATH = os.path.join(EXPORT_PATH, "datas", "style.css")
    with open(STYLE_FULL_PATH, "wb") as fh:
        fh.write(css_output.encode('utf-8'))

    print("Project generated at:", os.path.dirname(os.path.abspath(INDEX_FULL_PATH)))

