# coding: utf-8

"""
Functions for generating HTML output.
"""

import logging
import os
from os.path import join as pjoin
from pkg_resources import resource_filename
from urllib.parse import urlencode

from ashes import AshesEnv

from commongroups.errors import MissingParamError
from commongroups import logconf  # pylint: disable=unused-import
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

TEMPLATES_DIR = resource_filename(__name__, 'templates')
DIR_TITLE = 'Compound group processing results'


def pubchem_image(cid_or_container, size=500):
    """
    Generate HTML code for a PubChem molecular structure graphic and link.

    Parameters:
        cid_or_container: The CID (int, str) or a subscriptable object that
            contains a key ``cid``.

    Returns:
        HTML code for an image from PubChem.
    """
    if type(cid_or_container) in (int, str):
        cid = cid_or_container
    elif 'cid' in cid_or_container:
        cid = cid_or_container['cid']
    else:
        raise MissingParamError('cid')
    cid_url = 'https://pubchem.ncbi.nlm.nih.gov/compound/{}'.format(cid)
    imgbase = 'https://pubchem.ncbi.nlm.nih.gov/image/imagefly.cgi?'
    params = {'cid': cid, 'width': size, 'height': size}
    img_url = imgbase + urlencode(params)
    ret = '<a target="_blank" href="{0}"><img src="{1}"></a>'
    ret = ret.format(cid_url, img_url)
    return ret


def get_notes(cmg):
    """Retrieve ``notes`` from CMGroup info, if exists."""
    if 'notes' in cmg.info:
        return cmg.info['notes']
    else:
        return ''


def info_to_context(info):
    """Convert CMGroup ``info`` to a context for HTML templating."""
    top_keys = ['about', 'notes', 'sql', 'count']
    more_keys = [key for key in info.keys() if key not in top_keys]
    ret = {'more': []}
    for key in top_keys:
        if key in info and info[key]:
            ret.update({key: info[key]})
    for key in sorted(more_keys):
        ret['more'].append({'key': key, 'value': info[key]})
    return ret


def describe_cmg(cmg):
    """
    Generate an HTML snippet describing the parameters of a CMGroup.
    """
    # TODO:
    html = ''
    return html


def cmg_to_html(cmg, formats=None, img_source='PubChem', img_size=500):
    """
    Generate an HTML document showing results of processing a ``CMGroup``.

    Parameters:
        cmg: A :class:`CMGroup` object.
        formats (list): Other formats to link to for this compound group, such
            as: ``json``, ``excel``, ``csv``.
        img_source (str): How to generate images. Currently the only option
            is ``PubChem``.
    """
    if img_source == 'PubChem':
        image = pubchem_image
    else:
        raise NotImplementedError('Unsupported image source: '
                                  '{}'.format(img_source))

    if cmg.compounds is None:
        items = []
    else:
        items = cmg.compounds.to_dict(orient='records')
        for item in items:
            item['image'] = image(item, size=img_size)

    context = {'cmg_id': cmg.cmg_id,
               'name': cmg.name,
               'size': img_size,
               'info': info_to_context(cmg.info),
               'items': items,
               'formats': formats}

    templater = AshesEnv([TEMPLATES_DIR])
    html = templater.render('cmgroup.html', context)
    path = pjoin(cmg.results_path, 'html', '{}.html'.format(cmg.cmg_id))
    logger.info('Writing HTML file: %s', path)
    with open(path, 'w') as html_file:
        html_file.write(html)


def directory(cmgs, env, title=DIR_TITLE, formats=None):
    """
    Generate an HTML directory for a collection of compound groups.

    Writes and HTML file in the environment's ``results/html`` directory.

    Parameters:
        cmgs: Iterable of :class:`CMGroup` objects.
        env: :class:`CommonEnv` to contain output.
        title (str): Title of page.
        formats (list): List of file extensions to use to create links to other
            formats of this collection, e.g. ``json``, ``xlsx``.
    """
    items = [{'cmg_id': cmg.cmg_id,
              'name': cmg.name,
              'notes': get_notes(cmg)} for cmg in cmgs]
    context = {'title': title,
               'items': items,
               'formats': formats}
    templater = AshesEnv([TEMPLATES_DIR])
    html = templater.render('directory.html', context)
    path = pjoin(env.results_path, 'html', 'index.html')
    logger.info('Writing HTML file: %s', path)
    with open(path, 'w') as html_file:
        html_file.write(html)
