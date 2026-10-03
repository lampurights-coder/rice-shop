from django.test import TestCase

from accounts.utils import normalize_phone, valid_phone


class PhoneUtilsTest(TestCase):
    def test_normalize_phone(self):
        self.assertEqual(normalize_phone("0912 123 4567"), "09121234567")
        self.assertEqual(normalize_phone("9121234567"), "09121234567")
        self.assertEqual(normalize_phone("+989121234567"), "09121234567")

    def test_valid_phone(self):
        self.assertTrue(valid_phone("09121234567"))
        self.assertFalse(valid_phone("123"))
        self.assertFalse(valid_phone("08121234567"))
