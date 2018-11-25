# -*- coding: utf-8 -*-
""" Custom template helpers """

import os
import json
import textwrap
import markdown2
import codecs

from swiftclient.utils import generate_temp_url


def suffix(s):
    return u' ({})'.format(s) if s else u''


def date(d):
    return d.strftime('%Y-%m-%dT%H:%M:%SZ')


def markdown(content, extras=None):
    # Fix up whitespace.
    if content[0] == u"\n":
        content = content[1:]
    content = content.rstrip()
    content = textwrap.dedent(content)

    # Default extras
    if extras is None:
        extras = [
            "fenced-code-blocks",
            "footnotes",
            "tables",
            "use-file-vars"
        ]

    return markdown2.markdown(content, extras=extras)


def markdown_file(filename, extras=None):
    content = ''
    with codecs.open(filename, 'r', encoding="utf-8") as f:
        content = f.read()
    return markdown(content, extras=extras)


def swift_tempurl(course, filename, date):
    swift_endpoint = os.environ.get('SWIFT_ENDPOINT')
    swift_path = os.environ.get('SWIFT_PATH')
    swift_tempurl_key = os.environ.get('SWIFT_TEMPURL_KEY')

    assert(swift_endpoint)
    assert(swift_path)
    assert(swift_tempurl_key)

    path = u"{}/{}/{}".format(swift_path, course, filename)
    timestamp = int(date.strftime("%s"))
    temp_url = generate_temp_url(path,
                                 timestamp,
                                 swift_tempurl_key,
                                 'GET',
                                 absolute=True)

    return u"{}{}".format(swift_endpoint, temp_url)


def block_url(org, course, run_name, block_type, url_name):
    return "block-v1:{}+{}+{}+type@{}+block@{}".format(
        org, course, run_name, block_type, url_name)


def asset_url(org, course, run_name, filename):
    return "asset-v1:{}+{}+{}+type@asset+block@{}".format(
        org, course, run_name, filename)


def asset_policy(org, course, run_name, path, type=None, has_thumbnail=False,
                 locked=False):
    asset_name = path.replace(u'/', u'_')
    base_name = os.path.basename(path)
    thumbnail_location = None
    if has_thumbnail:
        thumbnail_location = ["c4x", org, course, "thumbnail", asset_name,
                              None]

    return json.dumps({
        asset_name: {
            "contentType": type,
            "content_son": {
                "category": "asset",
                "course": course,
                "name": asset_name,
                "org": org,
                "revision": None,
                "run": run_name,
                "tag": "c4x"
            },
            "displayname": base_name,
            "filename": asset_url(org, course, run_name, asset_name),
            "import_path": path,
            "locked": locked,
            "thumbnail_location": thumbnail_location
        }
    })
