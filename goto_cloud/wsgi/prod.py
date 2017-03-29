"""
WSGI config for goto_cloud project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'goto_cloud'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.prod")

application = get_wsgi_application()
