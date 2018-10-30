# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from swagger_spec_compatibility.example import hello


def test_hello():
    assert hello() == 'world'
