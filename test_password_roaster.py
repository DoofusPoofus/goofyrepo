import unittest

from password_roaster import (
    find_keyboard_walk,
    looks_like_a_common_password,
    make_time_sound_human,
    roast_password,
)


class CommonPasswordTests(unittest.TestCase):
    def test_plain_common_passwords_get_caught(self):
        for password in ["password", "qwerty", "123456", "Monkey"]:
            self.assertTrue(looks_like_a_common_password(password), password)

    def test_sneaky_versions_still_get_caught(self):
        for password in ["P@ssw0rd", "p@ssw0rd1", "monkey2024", "dragon!!", "123456!!"]:
            self.assertTrue(looks_like_a_common_password(password), password)

    def test_random_stuff_is_not_common(self):
        self.assertFalse(looks_like_a_common_password("vT9#kq2!Lm"))


class KeyboardWalkTests(unittest.TestCase):
    def test_finds_rows_both_directions(self):
        self.assertEqual(find_keyboard_walk("myasdfpass"), "asdf")
        self.assertEqual(find_keyboard_walk("rewq"), "qwer")

    def test_no_walk_in_random_password(self):
        self.assertIsNone(find_keyboard_walk("vT9#kq2!Lm"))


class RoastTests(unittest.TestCase):
    def test_empty_password(self):
        report = roast_password("")
        self.assertEqual(report["problems"], ["empty"])
        self.assertEqual(report["rating"], "instant L")

    def test_common_password_is_instant(self):
        report = roast_password("password123")
        self.assertIn("common", report["problems"])
        self.assertEqual(report["seconds_to_crack"], 0.0)

    def test_long_passphrase_is_solid(self):
        report = roast_password("purple-Toaster-gallops-at-noon-83")
        self.assertEqual(report["problems"], [])
        self.assertEqual(report["rating"], "actually solid")

    def test_patterns_make_it_weaker(self):
        random_one = roast_password("Xk7#mPq2Wz9!")
        patterned_one = roast_password("Asdf#2024Wz9!")
        self.assertLess(patterned_one["seconds_to_crack"], random_one["seconds_to_crack"])

    def test_long_lowercase_passphrase_doesnt_need_symbols(self):
        report = roast_password("purple toaster gallops at noon")
        self.assertNotIn("no_symbols", report["problems"])
        self.assertNotIn("no_uppercase", report["problems"])


class TimeFormattingTests(unittest.TestCase):
    def test_tiny_times(self):
        self.assertEqual(make_time_sound_human(0), "instantly")

    def test_normal_times(self):
        self.assertEqual(make_time_sound_human(120), "about 2 minutes")
        self.assertEqual(make_time_sound_human(60 * 60 * 24 * 3), "about 3 days")

    def test_absurd_times(self):
        self.assertEqual(make_time_sound_human(1e300), "longer than the universe has existed lol")


if __name__ == "__main__":
    unittest.main()
