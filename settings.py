"""
Django settings for your project.

Generated by 'dorm init', with minimal settings required for just using Django's ORM.

For the full list of settings and their values, see:
- https://docs.djangoproject.com/en/5.1/topics/settings/
- https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path



BASE_DIR = Path(__file__).parent.resolve()

# List of packages (Django apps), defining Django models.
# Each item should be a dotted Python path to package containing `models` as a module or a sub-package.
# https://docs.djangoproject.com/en/5.1/topics/db/models/
INSTALLED_APPS = ["game"] # TODO: add package here, after adding models

# Databases
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
