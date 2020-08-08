# django-dynamicsettings


[![tests](https://github.com/fopina/django-dynamicsettings/workflows/tests/badge.svg)](https://github.com/fopina/django-dynamicsettings/actions?query=workflow%3Atests)
[![Test coverage status](https://codecov.io/gh/fopina/django-dynamicsettings/branch/master/graph/badge.svg)](https://codecov.io/gh/fopina/django-dynamicsettings)
[![Current version on PyPi](https://img.shields.io/pypi/v/django-dynamicsettings)](https://pypi.org/project/django-dynamicsettings/)
[![monthly downloads](https://img.shields.io/pypi/dm/django-dynamicsettings)](https://pypi.org/project/django-dynamicsettings/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-dynamicsettings)
![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-dynamicsettings)


Django app to allow (chosen) settings to be configurable through django admin (or anything that updates the Settings model).

## Usage

In your `settings.py` (or whatever DJANGO_SETTINGS_MODULE you are using), simply change:

```python
MIGHTY_SETTING = 'boring_setting_requires_deploy'
```

to

```python
from dynamicsettings import DynamicSetting as DYN

MIGHTY_SETTING = DYN('boring_setting_requires_deploy')
```

And done. `MIGHT_SETTING` value can now be changed using `dynsetting.Setting` model (registered in django-admin).

`DynamicSetting` class caches the values from database as, quite often, the settings are accessed many times in the same loop.  
There is `CACHE_TTL` setting to control it (default being `1` second).

To change it simply put

```python
from dynamicsettings import DynamicSetting as DYN

DYN.CACHE_TTL = 30
```

in that same settings module. `0` disables cache entirely (not recommended).


## Alternatives

https://django-dynamic-preferences.readthedocs.io/en/latest/ seems like a popular solution to this problem but it solves it differently.
  
You need to register the settings with those decorators while with `dynamicsettings` you just add an helper to your usual settings.py definition and everything ~~should~~ seamlessly works!
