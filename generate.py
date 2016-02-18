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
import re
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

try: from jinja2 import Template, Environment, FileSystemLoader, meta, contextfunction, contextfilter
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


# COLOR MANIPULATION HELPERS
def brighten(color_hex, amount):
    color = spectra.html(color_hex)
    return color.brighten(amount).hexcode

def darken(color_hex, amount):
    color = spectra.html(color_hex)
    return color.darken(amount).hexcode


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

        # SETTING FILE
        if file_name == 'settings.yaml':
            with open(os.path.join(FILE_PATH, file_name), 'r') as stream:
                settings = yaml.load(stream)
            
            THEME_PATH = os.path.join(ABS_PATH, "themes", settings['theme'])
            theme_path_validation(THEME_PATH)

            # LOAD PALETTE
            ## SKELETON
            with open(os.path.join(THEME_PATH, "palette.yaml"), 'r') as stream:
                palette = yaml.load(stream)

            ## THEME FALLBACK
            if settings.get('palette') is None:
                with open(os.path.join(THEME_PATH, "theme.yaml"), 'r') as stream:
                    theme = yaml.load(stream)
                settings["palette"] = theme["palette"]
                print(settings['palette'])

            ## PATH VALIDATION
            PALETTE_PATH = os.path.join(THEME_PATH, "palettes", settings['palette'])
            palette_path_validation(PALETTE_PATH)

            ## UPDATE PALETTE
            with open(os.path.join(PALETTE_PATH, "palette.yaml"), 'r') as stream:
                theme_palette = yaml.load(stream)
                # print(palette)
                palette.update(theme_palette)

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

    # PALETTE SKELETON NON-SEXY PARSER
    new_palette = {}

    for color_name, modifier_combo in palette.items():
        parsed_modifier_combo = modifier_combo.rsplit('|')
        parsed_modifier_combo = list(reversed(parsed_modifier_combo))
        
        left = parsed_modifier_combo[0]
        m = re.match('(brighten|darken)\((\d*)\)', left)
        # IF THAT'S NOT A MOD IT'S A RAW COLOR
        if m is None:
            raw_color = left
            new_palette[color_name] = raw_color
            continue

        # IF COLOR MODIFIER
        modifier = left
        ## IF DIRECT REFERENCE TO ROOT COLOR
        if len(parsed_modifier_combo) == 1:
            color_ref_name = None
        else:
            color_ref_name = parsed_modifier_combo[1]

        palette[color_name] = [color_ref_name, modifier]


    def push_color(color_name):
        color_ref_name, modifier = palette[color_name]
        m = re.match('(brighten|darken)\((\d*)\)', modifier)

        mod_type = m.group(1)
        mod_amount = int(m.group(2))

        if color_ref_name is None:
            color_ref_name = "root"
            new_palette["root"] = "#F0F0F0"

        color_ref = new_palette.get(color_ref_name)
        if color_ref is None:
            push_color(color_ref_name)

        # Grabbing again because could have been built from push_color above
        color_ref = new_palette.get(color_ref_name)
        if mod_type == "brighten":
            new_color = brighten(color_ref, mod_amount)
        elif mod_type == "darken":
            new_color = darken(color_ref, mod_amount)

        new_palette[color_name] = new_color


    for color_name in palette:
        if new_palette.get(color_name) is None:
            push_color(color_name)

    palette = new_palette

    # CREATE EXPORT PATH & COPY DATA FILES
    EXPORT_PATH = os.path.join(FILE_PATH, 'export')
    if not os.path.exists(EXPORT_PATH):
        os.mkdir(EXPORT_PATH)
        copy_tree(os.path.join(SCRIPT_PATH, "datas"), os.path.join(EXPORT_PATH, "datas"))

    # COPY CSS THEME FILE TO PROJECT
    shutil.copy(os.path.join(THEME_PATH, 'style.css'), os.path.join(EXPORT_PATH, "datas"))

    # JINJA RENDERING
    env = Environment(loader=FileSystemLoader(THEME_PATH))

    env.filters['brighten'] = brighten
    env.filters['darken'] = darken

    # debug_template = env.from_string("{{ wot|darken(4) }} {{'blue'|brighten(10)}}")
    # print(debug_template.render({'wot':'red'}))

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

