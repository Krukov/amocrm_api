# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .base import Field, CustomField
from .api import *


class Contact():

    objects = ContactsManager

    def __init__(self):
        pass