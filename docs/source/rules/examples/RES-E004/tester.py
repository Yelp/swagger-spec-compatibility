# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from os.path import abspath

from bravado.client import SwaggerClient
from bravado_core.validate import validate_schema_object
from jsonschema import ValidationError
from six.moves.urllib.parse import urljoin
from six.moves.urllib.request import pathname2url

old_client = SwaggerClient.from_url(
    spec_url=urljoin('file:', pathname2url(abspath('old.yaml'))),
)
new_client = SwaggerClient.from_url(
    spec_url=urljoin('file:', pathname2url(abspath('new.yaml'))),
)

object_to_validate = {'property': None}

print('Validating the get endpoint response with the old client: Failed')
try:
    validate_schema_object(
        swagger_spec=old_client.swagger_spec,
        schema_object_spec=old_client.swagger_spec.definitions['get_endpoint_response']._model_spec,
        value=object_to_validate,
    )
    raise RuntimeError('An error was expected')
except ValidationError:
    pass

print('Validating the get endpoint response with the new client: Succeeded')
validate_schema_object(
    swagger_spec=new_client.swagger_spec,
    schema_object_spec=new_client.swagger_spec.definitions['get_endpoint_response']._model_spec,
    value=object_to_validate,
)
