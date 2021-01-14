# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

__version__ = '2.3.1'

import sys
import logging

logger = logging.getLogger('amocrm')

if not logger.handlers:
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)d %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S'
    )
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
