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

print('Calling the post endpoint with the old client: Succeeded')
old_client.endpoint.post_endpoint()
print('Calling the post endpoint with the new client: Failed')
try:
    new_client.endpoint.post_endpoint()
    raise RuntimeError('An error was expected')
except AttributeError:
    pass
