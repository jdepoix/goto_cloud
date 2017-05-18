from .base import *

ENVIRONMENT = 'testing'

DATABASES = {
    'default': {
        "USER": "postgres",
        "HOST": "localhost",
        "PASSWORD": "",
        "PORT": 5432,
        "NAME": "goto_cloud",
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
    }
}
