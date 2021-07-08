VERSION = (0, 0, 2)
__version__ = '%d.%d.%d' % VERSION

import time

try:
    from django.core.exceptions import ImproperlyConfigured, ValidationError
    import django

    if django.VERSION < (3, 2):
        default_app_config = 'dynamicsettings.apps.DynamicSettingsConfig'
except ModuleNotFoundError:
    # allow import without having django, for setup.py and others
    pass


class DynamicSetting(object):
    """
    Proxy class to be used with the django settings module
    Intercepts setting resolution and checks if it is overriden with a value
    in database (dynamicsettings.Setting model)
    """

    # in seconds, 0 means disabled, default of 1 (to allow initial settings to be loaded with a single query)
    CACHE_TTL = 1
    __cache__ = {}
    __last__cache__ = 0
    __registry__ = {}

    def __init__(self, setting_value, setting_name=None, setting_type=None):
        object.__setattr__(self, "_obj", setting_value)
        if setting_name is None:
            setting_name = _guess_variable_name_()
        if setting_name is None:
            raise ImproperlyConfigured('setting_name is required as it could not be inferred from its declaration')
        if setting_type is None:
            setting_type = type(setting_value)
            if setting_type not in (bool, str, int):
                raise ImproperlyConfigured(
                    'setting_type is required as a valid one (bool, str, int) '
                    'could not be inferred from its declaration'
                )
        object.__setattr__(self, "_obj_setting", setting_name)
        object.__setattr__(self, "_obj_type", setting_type)
        r = self.__class__.__registry__
        if setting_name in r and r[setting_name] != setting_type:
            raise ImproperlyConfigured(
                'already configured with conflicting setting_type',
                r[setting_name],
                setting_type,
            )
        r[setting_name] = setting_type

    def __getattribute__(self, name):
        return object.__getattribute__(self, name)

    def __delattr__(self, name):
        raise ValidationError('attributes not supported with DynamicSetting')

    def __setattr__(self, name, value):
        raise ValidationError('attributes not supported with DynamicSetting')

    def __get_dyn_value__(self):
        self.__load_cache__()

        n = object.__getattribute__(self, "_obj_setting")
        if n not in self.__cache__:
            return object.__getattribute__(self, "_obj")
        return self.__cache__[n]

    @classmethod
    def __load_cache__(cls):
        if time.time() - cls.__last__cache__ < cls.CACHE_TTL:
            return

        # delay importing models in app __init__.py...
        from dynamicsettings.models import Setting

        # dilemma: casting here is beneficial for higher CACHE_TTLs (as less casts per access) but worse
        # for lower CACHE_TTLs (as casting values that will not be used...)
        # if cache is at "instance" level instead of class level, then it would be the same
        # but a DB query would be made for each setting...
        cls.__cache__ = {s.name: cls.cast_type(s.value, name=s.name) for s in Setting.objects.filter(active=True)}
        cls.__last__cache__ = time.time()

    @classmethod
    def get_registry(cls):
        return cls.__registry__

    @classmethod
    def validate_name_value(cls, name, value):
        try:
            return cls.cast_type(value, name=name)
        except (ValueError, TypeError):
            raise ValidationError(
                '%(value)s is not valid for %(name)s',
                params={'value': value, 'name': name},
            )

    @classmethod
    def cast_type(cls, value, name=None, _type=None):
        if _type is None:
            if name is None or name not in cls.__registry__:
                raise ValidationError('%(name)s is not a valid setting', params={'name': name})
            _type = cls.__registry__.get(name)
        if _type is bool and isinstance(value, str):
            if value.lower() in ('true', 'yes', '1'):
                return True
            return False
        return _type(value)

    @classmethod
    def _reset(cls):
        # utility method to reset class-level variables (useful for unit-testing - or stuff even hackier than this)
        cls.__cache__ = {}
        cls.__last__cache__ = 0

    # dull/proxy implementation of all operators... maybe there is an easier way...?
    def __nonzero__(self):
        return bool(self.__get_dyn_value__())

    def __bool__(self):
        return bool(self.__get_dyn_value__())

    def __str__(self):
        return str(self.__get_dyn_value__())

    def __repr__(self):
        return repr(self.__get_dyn_value__())

    def __hash__(self):
        return hash(self.__get_dyn_value__())

    def __add__(self, other):
        return self.__get_dyn_value__() + other

    def __sub__(self, other):
        return self.__get_dyn_value__() - other

    def __mul__(self, other):
        return self.__get_dyn_value__() * other

    def __pow__(self, other):
        return self.__get_dyn_value__() ** other

    def __truediv__(self, other):
        return self.__get_dyn_value__() / other

    def __floordiv__(self, other):
        return self.__get_dyn_value__() // other

    def __mod__(self, other):
        return self.__get_dyn_value__() % other

    def __lshift__(self, other):
        return self.__get_dyn_value__() << other

    def __rshift__(self, other):
        return self.__get_dyn_value__() >> other

    def __and__(self, other):
        return self.__get_dyn_value__() & other

    def __or__(self, other):
        return self.__get_dyn_value__() | other

    def __xor__(self, other):
        return self.__get_dyn_value__() ^ other

    def __invert__(self):
        return ~self.__get_dyn_value__()

    def __lt__(self, other):
        return self.__get_dyn_value__() < other

    def __le__(self, other):
        return self.__get_dyn_value__() <= other

    def __eq__(self, other):
        return self.__get_dyn_value__() == other

    def __ne__(self, other):
        return self.__get_dyn_value__() != other

    def __gt__(self, other):
        return self.__get_dyn_value__() > other

    def __ge__(self, other):
        return self.__get_dyn_value__() >= other


def _guess_variable_name_():
    # delayed import just because "import inspect" always looks bad!!!
    # full disclosure: this is prone to many errors unless used exactly as the usual
    # settings.py definition: `VAR=...`
    # no kinky stuff allowed
    import inspect
    import re

    if not hasattr(_guess_variable_name_, '_re'):
        setattr(_guess_variable_name_, '_re', re.compile(r'[A-Za-z][A-Za-z0-9_]+'))

    frame = inspect.currentframe()
    # `frame - 2` must be the setting declaration
    # otherwise this weird code is being used in some weird way (can't complain!)
    frame = inspect.getouterframes(frame)[2]
    string = inspect.getframeinfo(frame[0]).code_context[0].strip()
    # TODO: improvement
    # check frame.__internals__.f_globals and extract DynamicSettings name
    # then use regexp to extract variable name, so it can be extracted with certainty
    # yup `a = b = c = 1` will result in only using `a`
    if '=' in string:
        v = string.split('=')[0].strip()
        # validate variable name
        if getattr(_guess_variable_name_, '_re').match(v):
            return v
    return None
