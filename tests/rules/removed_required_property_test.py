# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from bravado_core.spec import Spec

from swagger_spec_compatibility.rules.removed_required_property import RemovedRequiredProperty


def test_validate_succeed(minimal_spec_dict):
    assert list(RemovedRequiredProperty.validate(
        old_spec=Spec.from_dict(minimal_spec_dict),
        new_spec=Spec.from_dict(minimal_spec_dict),
    )) == []
