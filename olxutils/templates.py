# -*- coding: utf-8 -*-

import os
import fnmatch
import codecs

from jinja2 import (Environment, ChoiceLoader, PackageLoader, FileSystemLoader)

from . import helpers


class OLXTemplates(object):
    """
    Renders OLX templates.

    """
    OLX_DIRS = [
        ("static/markdown", "md"),
        ("static/presentation", "html"),
        ("about", "html"),
        ("chapter", "xml"),
        ("course", "xml"),
        ("discussion", "xml"),
        ("html", "html"),
        ("html", "xml"),
        ("info", "html"),
        ("policies", "json"),
        ("problem", "xml"),
        ("sequential", "xml"),
        ("tabs", "xml"),
        ("vertical", "xml"),
        ("video", "xml"),
    ]

    DEFAULT_FILTERS = [
        "unicode",
        "trim",
    ]

    env = None

    def __init__(self, context):
        self.env = Environment(
            loader=ChoiceLoader(
                PackageLoader(__name__, 'templates'),
                FileSystemLoader('.'),
            )
        )

        self.env.globals["helpers"] = helpers

    def render(self):
        templates = ['course.xml']
        for directory, filetype in self.OLX_DIRS:
            templates.extend(self._find_templates(directory, filetype))

        self._render_templates(templates)

    def _find_templates(self, directory, filetype):
        matches = []
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, '*.' + filetype):
                matches.append(os.path.join(root, filename))
        return matches

    def _render_templates(self, templates):
        for filename in templates:
            template = self.env.get_template(filename)
            basename = os.path.basename(filename)
            context = {"filename": os.path.splitext(basename)[0]}
            rendered = template.render(**context)

            # Remove symlink
            if os.path.islink(filename):
                os.unlink(filename)

            with codecs.open(filename, 'w', 'utf-8') as f:
                f.write(rendered)
