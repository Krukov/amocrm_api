# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import sys
import logging


logger = logging.getLogger(__name__)

if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)d %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S'
    )
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)