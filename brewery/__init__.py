#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Brewery"""

import os
import sys
from fields import *

try:
    import json
except ImportError:
    import simplejson as json

__version__ = '0.7.0'

brewery_search_paths = ['/etc/brewery', \
						'~/.brewery/', \
						'./.brewery/']

def set_brewery_search_paths(paths):
    global brewery_search_paths
    brewery_search_paths = paths

def default_logger_name():
    return 'brewery'

__all__ = (
    "Field",
    "FieldList",
    "fieldlist",
    "expand_record",
    "collapse_record"
)