# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
import sys
import typing
from argparse import ArgumentParser

from swagger_spec_compatibility.rules.common import Level
from swagger_spec_compatibility.rules.common import RuleRegistry
from swagger_spec_compatibility.rules.common import RuleType


_RULE_TYPE_TEMPLATE = {
    RuleType.REQUEST_CONTRACT: 'REQ-E{number:03d}',
    RuleType.RESPONSE_CONTRACT: 'RES-E{number:03d}',
    RuleType.MISCELLANEOUS: 'MIS-E{number:03d}',
}
_RULE_CLASS_FILE_TEMPLATE = """# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing

from bravado_core.spec import Spec

from swagger_spec_compatibility.rules.common import BaseRule
from swagger_spec_compatibility.rules.common import Level
from swagger_spec_compatibility.rules.common import RuleType
from swagger_spec_compatibility.rules.common import ValidationMessage


class {detection_class_name}(BaseRule):
    description = {description}
    error_code = {error_code}
    error_level = {error_level}
    rule_type = {rule_type}
    short_name = {short_name}
    documentation_link = {documentation_link}

    @classmethod
    def validate(cls, left_spec, right_spec):
        # type: (Spec, Spec) -> typing.Iterable[ValidationMessage]
        raise NotImplementedError()
"""
_RULE_CLASS_TEST_FILE_TEMPLATE = """# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


from swagger_spec_compatibility.rules.{python_file_name_no_ext} import {detection_class_name}


def test_validate_succeed(minimal_spec):
    assert list({detection_class_name}.validate(
        left_spec=minimal_spec,
        right_spec=minimal_spec,
    )) == []
"""
_RULE_CLASS_DOC_TEMPLATE = """.. automodule:: swagger_spec_compatibility.rules.{module_name}
    :members:
    :undoc-members:
    :show-inheritance:
"""
_MINIMAL_SPECS = """swagger: '2.0'
info:
  title: Minimal Case of {error_code} Rule
  version: '1.0'
definitions: {{}}
paths: {{}}
"""
_TESTER_TEMPLATE = """# -*- coding: utf-8 -*-
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
"""
_RULE_LONG_DOC_TEMPLATE = """[{error_code}] - {short_name}
=====================================================

Rationale
---------
TODO

Mitigation
----------
TODO

Example
-------
Old Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/{error_code}/old.yaml
   :name: Old Swagger Spec
   :language: yaml
   :linenos:

New Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/{error_code}/new.yaml
   :name: New Swagger Spec
   :language: yaml
   :linenos:

.. Please highlight the different lines by using `:emphasize-lines: #`

Backward Incompatibility
~~~~~~~~~~~~~~~~~~~~~~~~
The following snippet triggers the incompatibility error.

.. literalinclude:: examples/{error_code}/tester.py
   :language: py
   :linenos:

**NOTE**: The code is taking advantage of `bravado <https://github.com/Yelp/bravado>`_
"""


def _parser():
    # type: () -> ArgumentParser
    argument_parser = ArgumentParser(description='Helper to create new swagger-spec-compatiblity detection rules')
    argument_parser.add_argument(
        '--description',
        help='Short description of the rationale of the rule. This will be visible on CLI only',
    )
    argument_parser.add_argument(
        '--detection-class-name',
        help='Name of the detection class',
        required=True,
    )
    argument_parser.add_argument(
        '--documentation-link',
        help='Documentation link',
    )
    argument_parser.add_argument(
        '--error-level',
        help='Error level associated to the rule',
        choices=[item.name for item in Level],
        required=True,
    )
    argument_parser.add_argument(
        '--rule-type',
        help='Type of the rule associated',
        choices=[item.name for item in RuleType],
        required=True,
    )
    argument_parser.add_argument(
        '--short-name',
        help='Short name of the rule. This will be visible on CLI in case the rule is triggered',
    )
    return argument_parser


def _write_file(path, lines, fail_if_file_exist=True):
    # type: (typing.Text, typing.Iterable[typing.Text], bool) -> None
    does_file_exist = os.path.exists(path)
    if does_file_exist and fail_if_file_exist:
        raise RuntimeError('Cannot update {} [tool assumption]'.format(path))
    with open(path, 'w') as f:
        f.writelines(map(str, lines))
    print(
        '{prefix} file {path}'.format(
            prefix='Updated' if does_file_exist else 'Created',
            path=path,
        ),
        file=sys.stderr,
    )


def _create_code_skeleton(
    description,  # type: typing.Optional[typing.Text]
    detection_class_name,  # type: typing.Text
    documentation_link,  # type: typing.Optional[typing.Text]
    error_code,  # type: typing.Text
    error_level,  # type: Level
    python_file_name_no_ext,  # type: typing.Text
    rule_type,  # type: RuleType
    short_name,  # type: typing.Optional[typing.Text]
):
    python_file_name = '{}.py'.format(python_file_name_no_ext)
    _write_file(
        path=os.path.join('swagger_spec_compatibility', 'rules', python_file_name),
        lines=[
            _RULE_CLASS_FILE_TEMPLATE.format(
                description=description or repr('TODO'),
                detection_class_name=detection_class_name,
                documentation_link=documentation_link,
                error_code=repr(error_code),
                error_level='Level.{}'.format(error_level.name),
                python_file_name=python_file_name,
                rule_type='RuleType.{}'.format(rule_type.name),
                short_name=short_name or repr('TODO'),
            ),
        ],
    )
    _write_file(
        path=os.path.join('tests', 'rules', '{}_test.py'.format(python_file_name_no_ext)),
        lines=[
            _RULE_CLASS_TEST_FILE_TEMPLATE.format(
                detection_class_name=detection_class_name,
                python_file_name_no_ext=python_file_name_no_ext,
            ),
        ],
    )


def _create_documentation_skeleton(
    description,  # type: typing.Optional[typing.Text]
    detection_class_name,  # type: typing.Text
    documentation_link,  # type: typing.Optional[typing.Text]
    error_code,  # type: typing.Text
    error_level,  # type: Level
    python_file_name_no_ext,  # type: typing.Text
    rule_type,  # type: RuleType
    short_name,  # type: typing.Optional[typing.Text]
):
    module_doc_file_path = os.path.join('docs', 'source', 'swagger_spec_compatibility.rst')
    with open(module_doc_file_path, 'r') as f:
        swagger_spec_compatibility_lines = f.readlines()

    add_new_rules_anchor = '.. ADD NEW RULES HERE\n'
    add_new_rules_anchor_index = swagger_spec_compatibility_lines.index(str(add_new_rules_anchor))
    swagger_spec_compatibility_lines[add_new_rules_anchor_index] = str('{doc}\n{anchor}'.format(
        anchor=add_new_rules_anchor,
        doc=_RULE_CLASS_DOC_TEMPLATE.format(module_name=python_file_name_no_ext),
    ))

    _write_file(
        path=module_doc_file_path,
        lines=swagger_spec_compatibility_lines,
        fail_if_file_exist=False,
    )

    rules_directory = os.path.join('docs', 'source', 'rules')
    examples_directory = os.path.join('docs', 'source', 'rules', 'examples', error_code)
    os.makedirs(examples_directory, exist_ok=True)  # type: ignore  # for some reason mypy does not find exist_ok parameter
    _write_file(
        path=os.path.join(examples_directory, 'old.yaml'),
        lines=[_MINIMAL_SPECS.format(error_code=error_code)],
    )
    _write_file(
        path=os.path.join(examples_directory, 'new.yaml'),
        lines=[_MINIMAL_SPECS.format(error_code=error_code)],
    )
    _write_file(
        path=os.path.join(examples_directory, 'tester.py'),
        lines=[_TESTER_TEMPLATE],
    )
    _write_file(
        path=os.path.join(rules_directory, '{}.rst'.format(error_code)),
        lines=[
            _RULE_LONG_DOC_TEMPLATE.format(
                error_code=error_code,
                short_name=short_name or repr('TODO'),
            ),
        ],
    )

    with open(os.path.join(rules_directory, 'index.rst'.format(error_code)), 'r') as f:
        index_lines = f.readlines()

    add_new_rules_index_anchor = '.. ADD HERE NEW {} rules\n'.format(_RULE_TYPE_TEMPLATE[rule_type])
    add_new_rules_index_anchor_index = index_lines.index(str(add_new_rules_index_anchor))
    index_lines[add_new_rules_index_anchor_index] = str('   {error_code}\n{anchor}'.format(
        anchor=add_new_rules_index_anchor,
        error_code=error_code,
    ))

    _write_file(
        path=os.path.join(rules_directory, 'index.rst'.format(error_code)),
        lines=index_lines,
        fail_if_file_exist=False,
    )


def create_rule_skeleton(
    description,  # type: typing.Optional[typing.Text]
    detection_class_name,  # type: typing.Text
    documentation_link,  # type: typing.Optional[typing.Text]
    error_level,  # type: Level
    rule_type,  # type: RuleType
    short_name,  # type: typing.Optional[typing.Text]
):
    # type: (...) -> None
    def _camel_to_snake_case(text):
        # type: (typing.Text) -> typing.Text
        # Thanks to https://stackoverflow.com/a/1176023
        return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()

    python_file_name_no_ext = _camel_to_snake_case(detection_class_name)

    error_code = _RULE_TYPE_TEMPLATE[rule_type].format(
        number=1 + sum(
            1
            for rule in RuleRegistry.rules()
            if rule.rule_type == rule_type
        ),
    )

    for method in _create_code_skeleton, _create_documentation_skeleton:
        method(
            description=description,
            detection_class_name=detection_class_name,
            documentation_link=documentation_link,
            error_code=error_code,
            error_level=error_level,
            python_file_name_no_ext=python_file_name_no_ext,
            rule_type=rule_type,
            short_name=short_name,
        )


def main(args=None):
    # type: (typing.Optional[typing.List[typing.Text]]) -> None
    parsed_arguments = _parser().parse_args(args=args)
    print(
        'The tool is far from perfect. Please make sure that all the created skeleton make sense ;)',
        file=sys.stderr,
    )
    create_rule_skeleton(
        description=parsed_arguments.description,
        detection_class_name=parsed_arguments.detection_class_name,
        documentation_link=parsed_arguments.documentation_link,
        error_level=Level[parsed_arguments.error_level],
        rule_type=RuleType[parsed_arguments.rule_type],
        short_name=parsed_arguments.short_name,
    )


if __name__ == '__main__':
    main()
