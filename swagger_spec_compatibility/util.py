# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from enum import Enum


class StringEnum(str, Enum):
    """Enum where members are also (and must be) strings"""
