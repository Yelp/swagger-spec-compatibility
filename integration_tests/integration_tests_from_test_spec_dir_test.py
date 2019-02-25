# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import glob
import os
import re
from typing import Any  # noqa: F401
from typing import Generator  # noqa: F401
from typing import NamedTuple
from typing import Text

from six import itervalues

from swagger_spec_compatibility.cli.common import uri
from swagger_spec_compatibility.rules import compatibility_status
from swagger_spec_compatibility.spec_utils import load_spec_from_uri


Specification = NamedTuple(
    'Specification', [
        ('test_id', Text),
        ('old_spec_uri', Text),
        ('new_spec_uri', Text),
        ('number_of_reports', int),
    ],
)


def _test_specification_id(test_specification):  # pragma: no cover # this is used internally by pytest and it won't appear on coverage
    # type: (Specification) -> Text
    return test_specification.test_id


def get_test_specifications():  # pragma: no cover # this is used internally by pytest and it won't appear on coverage
    # type: () -> Generator[Specification, None, None]
    test_specs_dir = os.path.join(os.path.dirname(__file__), 'test-specs')
    for case_dir in glob.iglob(os.path.join(test_specs_dir, 'case-*-*-reports*')):
        match = re.match(r'^.*/case-\d+-(?P<number_of_reports>\d+)-reports.*$', case_dir)
        if not match:
            raise RuntimeError('{} does not follow the expected pattern (case-\\d+-\\d+-reports(-description)?'.format(case_dir))

        yield Specification(
            test_id=os.path.basename(case_dir),
            old_spec_uri=uri(str(os.path.join(case_dir, 'old.yaml'))),
            new_spec_uri=uri(str(os.path.join(case_dir, 'new.yaml'))),
            number_of_reports=int(match.group(str('number_of_reports'))),
        )


def pytest_generate_tests(metafunc):  # pragma: no cover # this is used internally by pytest and it won't appear on coverage
    # type: (Any) -> None
    if metafunc.definition.name == 'test_spec_from_test_specs_directory' and ['test_specification'] == metafunc.fixturenames:
        test_specifications = list(get_test_specifications())
        if test_specifications:
            metafunc.parametrize('test_specification', test_specifications, ids=_test_specification_id)
        else:
            metafunc.parametrize('test_specification', [])


def test_spec_from_test_specs_directory(test_specification):
    # type: (Specification) -> None
    result = compatibility_status(
        old_spec=load_spec_from_uri(test_specification.old_spec_uri),
        new_spec=load_spec_from_uri(test_specification.new_spec_uri),
    )
    number_of_reports = len([
        report
        for reports in itervalues(result)
        for report in reports
    ])
    assert number_of_reports == test_specification.number_of_reports
