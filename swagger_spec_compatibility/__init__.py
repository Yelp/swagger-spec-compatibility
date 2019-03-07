# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import venusian

import swagger_spec_compatibility.rules

# Scan the whole library in order to import all the available rules
venusian.Scanner().scan(swagger_spec_compatibility.rules)
