# portfolio.io.js.py

The shortest path to build your portfolio.

## Make your portfolio
### Generate project source
Run `generate.py create myportfolio`

A folder named `myportfolio` has been created with a sample project inside.  
Any `.yaml` file inside that folder will be considered as a section of your portfolio.

The sample `design.yaml` should contain something like:

```yaml
Wooba:
    description: "Lorem ipsum dolor sit amet, eu has purto everti, ea possit albucius duo, ius ne magna consequat. In quaeque euismod eos, eos elit maluisset scribentur eu."
    image: "http://lorempixel.com/400/250/abstract/1"
    labels:
        - "Colourful"
        - "Abstract"
        - "Collaboration"
```

..and is quite self-explanatory.

The name of this file will also be the name of the section in the menu of the generated page, here `DESIGN`.

Rename, duplicate and change appropriate fields.

### Build project
Run `generate.py build myportfolio`

An `export` folder has been created inside your `myportfolio` project.  

**Open `index.html` and host it !**

## Customize your portfolio
### settings.yaml
Open `settings.yaml` inside your `myportfolio` project and edit it.

```yaml
# Page title
title: "Dummy's Portfolio"
# Header == title variable if not set
header: "Dummy's works"
# Used after the header text and as a favicon
logo_image: "sample.png"
# Name of the theme used
theme: 'moo'
# If palette is not defined here, will use the default one from theme.yaml
# palette: 'grayscale'

# Service name is based on this list (without the 'fa-' prefix): http://fontawesome.io/icons/#brand
social:
    github: "https://github.com/Dvergar/"
    twitter: "https://twitter.com/caribouloche"
```

### Theming

Focus is on easy theming from only changing color palette to making your own template.
#### palette.yaml
You'll find a list of palettes in the `palettes` folder.

The easiest styling customization you can do is setting **one** color in a custom palette like:

```yaml
website_background: "red"
```