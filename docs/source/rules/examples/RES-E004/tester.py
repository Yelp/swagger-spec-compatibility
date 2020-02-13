# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from os.path import abspath

from bravado.client import SwaggerClient
from six.moves.urllib.parse import urljoin
from six.moves.urllib.request import pathname2url

old_client = SwaggerClient.from_url(
    spec_url=urljoin('file:', pathname2url(abspath('old.yaml'))),
)
new_client = SwaggerClient.from_url(
    spec_url=urljoin('file:', pathname2url(abspath('new.yaml'))),
)

raise NotImplementedError()
