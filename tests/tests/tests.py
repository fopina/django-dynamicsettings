from unittest import mock

from django.test import TestCase, override_settings
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from dynamicsettings import DynamicSetting as DYN, models


class Test(TestCase):
    def setUp(self) -> None:
        # most tests need cache disabled
        self.__original_cache = DYN.CACHE_TTL
        DYN.CACHE_TTL = 0
        # also make sure cache is reset on every test, of course...
        DYN._reset()

    def tearDown(self) -> None:
        DYN.CACHE_TTL = self.__original_cache

    def test_guess_name(self):
        # this works
        var = DYN(2)
        self.assertEqual(var, 2)
        # this does not
        with self.assertRaises(ImproperlyConfigured):
            # do not auto-format, need this for the test
            # fmt: off
            var = (
                DYN(2)
            )
            # fmt: on
        # but you can work around it
        # do not auto-format, need this for the test
        # fmt: off
        var = (
                  DYN(2, setting_name='TEST_VAR')
        )
        # fmt: on
        self.assertEqual(var, 2)

    # fmt: off
    @override_settings(
        TEST_SET_STATIC=1,
        TEST_SET_DYNAMIC=DYN('a'),
    )
    # fmt: on
    def test_settings(self):
        self.assertEqual(settings.TEST_SET_STATIC, 1)
        # __eq__ should work (__repr__ should not be called)
        self.assertEqual(settings.TEST_SET_DYNAMIC, 'a')
        # __eq__ just to make sure it does not return always true
        self.assertNotEqual(settings.TEST_SET_DYNAMIC, 3)
        # reversing order still works, hopefully
        self.assertEqual('a', settings.TEST_SET_DYNAMIC)

        c = models.Setting.objects.create(name='TEST_SET_DYNAMIC', value='b')
        c.clean()
        self.assertEqual(settings.TEST_SET_DYNAMIC, 'b')
        self.assertEqual(settings.TEST_SET_DYNAMIC + 'abe', 'babe')

    def test_settings_bool(self):
        var_b = DYN(True)
        self.assertEqual(var_b, True)
        c = models.Setting.objects.create(name='var_b', value='')
        c.clean()
        self.assertEqual(var_b, False)
        self.assertEqual(not var_b, True)

    def test_settings_int(self):
        var_i = DYN(2)
        self.assertEqual(var_i, 2)
        c = models.Setting.objects.create(name='var_i', value='3')
        c.clean()
        # reverse __eq__ behaves as well?
        self.assertEqual(3, var_i)
        self.assertEqual(var_i, 3)
        self.assertEqual(var_i + 1, 4)

    def test_settings_int_cast(self):
        var_i = DYN(2)
        self.assertEqual(var_i, 2)
        self.assertEqual(int(var_i), 2)
        # implementing __instancecheck__ would be nice (for cases like datetime.timedelta that check types)
        # but should we (instead of just explicit casting)...?
        self.assertFalse(isinstance(var_i, int))
        self.assertTrue(isinstance(int(var_i), int))

    def test_settings_other(self):
        var_o = DYN(None, setting_type=int)
        self.assertEqual(var_o, None)
        c = models.Setting.objects.create(name='var_o', value='3')
        c.clean()
        self.assertEqual(var_o, 3)
        self.assertEqual(var_o + 1, 4)
        self.assertTrue(var_o < 4)
        self.assertTrue(var_o <= 3)
        self.assertFalse(var_o <= 2)

    # fmt: off
    @override_settings(
        TEST_VAR_S=DYN('a'),
    )
    # fmt: on
    def test_settings_cache(self):
        DYN.CACHE_TTL = 10
        self.assertEqual(settings.TEST_VAR_S, 'a')
        c = models.Setting.objects.create(name='TEST_VAR_S', value='b')
        c.clean()
        # cache hit
        self.assertEqual(settings.TEST_VAR_S, 'a')
        with mock.patch('time.time', return_value=9588073256):
            # cache expired, new value
            self.assertEqual(settings.TEST_VAR_S, 'b')
