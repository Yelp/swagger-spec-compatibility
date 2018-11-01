# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from argparse import ArgumentTypeError
from os.path import abspath
from os.path import exists

from six.moves.urllib.parse import urljoin
from six.moves.urllib.parse import urlsplit
from six.moves.urllib.request import pathname2url


def uri(param):
    # type: (str) -> str
    if exists(param):
        return urljoin('file:', pathname2url(abspath(param)))
    elif urlsplit(param).scheme:
        return param
    else:
        raise ArgumentTypeError('`{param}` is not an existing file and either a valid URI'.format(param=param))
