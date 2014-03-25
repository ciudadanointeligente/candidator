#!/usr/bin/env python
from django.core.management import call_command
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "candidator.settings")
call_command('test','elections', verbosity=1)

