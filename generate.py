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
import shutil
from collections import OrderedDict

# TODO REQUIREMENTS.TXT !?

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

try: import yamlordereddictloader
except ImportError: pip.main(["install", "yamlordereddictloader"])


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


# MARKDOWN P STRIPPER
def markdown_parse(string, strip=False):
    md_string = markdown.markdown(string)
    
    if strip:
        p, np = '<p>', '</p>'
        return md_string[len(p):-len(np)]
    else:
        return md_string

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
    PROJECT_PATH = arguments['<project-path>']

    # LOAD USER PROJECT FILES
    reserved_files = ["settings.yaml"]

    sections = {}
    for file_name in os.listdir(PROJECT_PATH):
        file_root = os.path.splitext(file_name)[0]
        file_ext = os.path.splitext(file_name)[-1]

        # IGNORE DIRECTORIES
        if not os.path.isfile(os.path.join(PROJECT_PATH, file_name)):
            continue

        # IGNORE NON YAML FILES
        if not file_ext == '.yaml':
            continue

        # IGNORE RESERVED FILES
        if file_name in reserved_files:
            continue

        # ENTRY FILES
        with open(os.path.join(PROJECT_PATH, file_name), 'r') as stream:
            yaml_entries = yaml.load(stream, Loader=yamlordereddictloader.Loader)

            # MARKDOWN PARSING
            for entry_name, entry_obj in yaml_entries.items():
                entry_obj['description'] = markdown_parse(entry_obj['description'])

                for i in range(len(entry_obj['labels'])):
                    entry_obj['labels'][i] = markdown_parse(entry_obj['labels'][i], strip=True)

            sections[file_root] = yaml_entries
    sections = OrderedDict(sorted(sections.items()))

    # SETTING FILE
    with open(os.path.join(PROJECT_PATH, "settings.yaml"), 'r') as stream:
        settings = yaml.load(stream, Loader=yamlordereddictloader.Loader)

    # MENU ORDER
    if settings.get('menu_order') is not None:
        new_sections = OrderedDict({})
        for entry in settings.get('menu_order'):
            new_sections[entry] = sections[entry]
        sections = new_sections

    THEME_PATH = os.path.join(SCRIPT_PATH, "themes", settings['theme'])
    theme_path_validation(THEME_PATH)

    # LOAD PALETTE
    ## SKELETON
    with open(os.path.join(THEME_PATH, "palette.yaml"), 'r') as stream:
        skel_palette = yaml.load(stream, Loader=yamlordereddictloader.Loader)

    ## THEME FALLBACK
    if settings.get('palette') is None:
        with open(os.path.join(THEME_PATH, "theme.yaml"), 'r') as stream:
            theme = yaml.load(stream, Loader=yamlordereddictloader.Loader)
        settings["palette"] = theme["palette"]
        print(type(settings['palette']))

    if settings["palette"] != "SKELETON": ## SKELETON BEING RESERVED FOR GRAYSCALE PALETTE
        ## PATH VALIDATION
        PALETTE_PATH = os.path.join(THEME_PATH, "palettes", settings['palette'])
        palette_path_validation(PALETTE_PATH)

        ## UPDATE PALETTE
        with open(os.path.join(PALETTE_PATH, "palette.yaml"), 'r') as stream:
            theme_palette = yaml.load(stream, Loader=yamlordereddictloader.Loader)

            if theme_palette is not None:
                skel_palette.update(theme_palette)

    palette = skel_palette

    # PALETTE SKELETON NON-SEXY PARSER
    new_palette = {}

    for color_name, modifier_combo in palette.items():
        parsed_modifier_combo = modifier_combo.rsplit('|')
        parsed_modifier_combo = list(reversed(parsed_modifier_combo))
        
        left = parsed_modifier_combo[0]
        m = re.match('(brighten|darken)\((\d*)\)', left)

        color_ref_wo_mod = left in palette.keys()

        # IF THAT'S NOT A MOD AND NOT A REF ONLY COLOR, IT'S A RAW COLOR
        if m is None and not color_ref_wo_mod:
            raw_color = left
            new_palette[color_name] = raw_color
            continue

        # IF COLOR MODIFIER
        modifier = left
        ## IF DIRECT REFERENCE TO ROOT COLOR
        if len(parsed_modifier_combo) == 1 and m is not None:
            color_ref_name = None
        # IF REFERENCE TO COLOR WITHOUT MODIFIER
        elif color_ref_wo_mod:
            color_ref_name = parsed_modifier_combo[0]
            modifier = None
        else:
            color_ref_name = parsed_modifier_combo[1]

        palette[color_name] = [color_ref_name, modifier]


    def push_color(color_name):
        color_value, modifier = palette[color_name]

        # EXTRACT MOD DATAS
        if modifier is not None:
            m = re.match('(brighten|darken)\((\d*)\)', modifier)
            mod_type = m.group(1)
            mod_amount = int(m.group(2))

        color_ref_name = color_value

        # ROOT COLOR CASE
        if color_ref_name is None:
            color_ref_name = "root"
            new_palette["root"] = "#F0F0F0"  # FAKE REF
        # RAW COLOR + MOD CASE
        elif color_ref_name not in palette.keys():
            new_palette[color_value] = color_value  # FAKE REF

        # IF REFERENCED COLOR NOT PROCESSED YET
        color_ref = new_palette.get(color_ref_name)
        if color_ref is None:
            push_color(color_ref_name)

        # Grabbing again because could have been built from push_color above
        color_ref = new_palette.get(color_ref_name)
        if modifier is None:
            new_color_ref = color_ref
        elif mod_type == "brighten":
            new_color_ref = brighten(color_ref, mod_amount)
        elif mod_type == "darken":
            new_color_ref = darken(color_ref, mod_amount)

        new_palette[color_name] = new_color_ref


    for color_name in palette:
        if new_palette.get(color_name) is None:
            push_color(color_name)

    palette = new_palette

    # MERGING ALL CSS
    with open(os.path.join(THEME_PATH, "style.css"), 'r') as stream:
        css = stream.read()

    CSS_FULL_PATH = os.path.join(PALETTE_PATH, "style.css")
    if os.path.isfile(CSS_FULL_PATH):
        with open(CSS_FULL_PATH, 'r') as stream:
            css += "\n/* Palette specific css below */\n\n"
            css += stream.read()

    # CREATE EXPORT PATH & COPY DATA FILES
    EXPORT_PATH = os.path.join(os.getcwd(), arguments['<project-path>'], 'export')

    if not os.path.exists(EXPORT_PATH):
        os.mkdir(EXPORT_PATH)
        shutil.copytree(os.path.join(SCRIPT_PATH, "datas"), os.path.join(EXPORT_PATH, "datas"))

    # COPY CSS THEME FILE TO PROJECT
    shutil.copy(os.path.join(THEME_PATH, 'style.css'), os.path.join(EXPORT_PATH, "datas"))

    # LOGO STUFF
    if settings.get('logo_image') is not None:
        ## COPY LOGO IMAGE TO PROJECT
        shutil.copy(os.path.join(PROJECT_PATH, settings['logo_image']), os.path.join(EXPORT_PATH, "datas"))

        ## LOGO PATH UPDATE
        if os.path.isfile(os.path.join(PROJECT_PATH, settings.get('logo_image'))):
            settings['logo_image'] = 'datas/' + settings['logo_image']

    # JINJA RENDERING
    env = Environment(loader=FileSystemLoader(THEME_PATH))

    env.filters['brighten'] = brighten
    env.filters['darken'] = darken

    tpl_html = env.get_template("template.html")
    tpl_css = env.from_string(css)
    
    html_output = tpl_html.render(sections=sections, settings=settings, palette=palette)
    css_output = tpl_css.render(palette=palette)

    # GENERATE INDEX.HTML
    INDEX_FULL_PATH = os.path.join(EXPORT_PATH, "index.html")
    with open(INDEX_FULL_PATH, "wb") as fh:
        fh.write(html_output.encode('utf-8'))

    # GENERATE STYLE.CSS
    STYLE_FULL_PATH = os.path.join(EXPORT_PATH, "datas", "style.css")
    with open(STYLE_FULL_PATH, "wb") as fh:
        fh.write(css_output.encode('utf-8'))

    print("Project generated at:", os.path.dirname(os.path.abspath(INDEX_FULL_PATH)))

