import os
import unittest
from html.parser import HTMLParser
from string import Formatter
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import ToEnWikipediaBot as bot


class MessageMarkup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.open_tags = []

    def handle_starttag(self, tag, attrs):
        self.open_tags.append(tag)

    def handle_endtag(self, tag):
        if not self.open_tags or self.open_tags.pop() != tag:
            raise AssertionError(f"Unbalanced message markup: {tag}")


class LocalizationTests(unittest.IsolatedAsyncioTestCase):
    def test_translations_have_matching_keys_and_placeholders(self):
        self.assertEqual(bot.TEXT["en"].keys(), bot.TEXT["it"].keys())
        formatter = Formatter()
        for key, english in bot.TEXT["en"].items():
            with self.subTest(key=key):
                placeholders = lambda text: {
                    name for _, name, _, _ in formatter.parse(text) if name is not None
                }
                self.assertEqual(placeholders(english), placeholders(bot.TEXT["it"][key]))
                self.assertTrue(bot.TEXT["it"][key].strip())

    def test_automatic_language_selection(self):
        for code, expected in [("it", "it"), ("it-IT", "it"), ("IT", "it"),
                               ("en", "en"), ("fr", "en"), (None, "en")]:
            with self.subTest(code=code):
                self.assertEqual(bot._detected_language({"language_code": code}), expected)

    async def test_saved_language_overrides_telegram_language(self):
        user = SimpleNamespace(id=123, language_code="it")
        with patch.object(bot, "_read_language_preference", return_value="en"):
            self.assertEqual(await bot._language_for_user(user), "en")
        with patch.object(bot, "_read_language_preference", return_value=None):
            self.assertEqual(await bot._language_for_user(user), "it")

    async def test_privacy_policy_matches_selected_language(self):
        for language, filename in [("en", "/PRIVACY_POLICY.html"),
                                   ("it", "/PRIVACY_POLICY.it.html")]:
            with self.subTest(language=language), \
                 patch.object(bot, "_language", new=AsyncMock(return_value=language)), \
                 patch.object(bot, "_reply", new=AsyncMock()) as reply:
                await bot.privacy(SimpleNamespace(), SimpleNamespace())
                text = reply.call_args.args[1]
                self.assertTrue(text.endswith(filename))
                self.assertTrue(text.startswith(bot.TEXT[language]["privacy_policy"]))

    async def test_status_unknown_values_are_localized(self):
        for language in ("en", "it"):
            with self.subTest(language=language), \
                 patch.object(bot, "_language", new=AsyncMock(return_value=language)), \
                 patch.object(bot, "_read_monitor_state", return_value={}), \
                 patch.object(bot, "_reply", new=AsyncMock()) as reply, \
                 patch.dict(os.environ, {}, clear=True):
                await bot.status_command(SimpleNamespace(), SimpleNamespace())
                text = reply.call_args.args[1]
                self.assertEqual(text.count(bot.TEXT[language]["unknown"]), 4)
                self.assertIn(bot.TEXT[language]["unknown_status"], text)
                if language == "it":
                    self.assertNotIn("unknown", text)

    async def test_status_elapsed_time_uses_singular_and_plural(self):
        for language, singular, plural in [("en", "1 second ago", "seconds ago"),
                                           ("it", "1 secondo fa", "secondi fa")]:
            for age in (0, 1, 2):
                with self.subTest(language=language, age=age), \
                     patch.object(bot, "_language", new=AsyncMock(return_value=language)), \
                     patch.object(bot, "_read_monitor_state", return_value={"checked_at": "100"}), \
                     patch.object(bot, "_reply", new=AsyncMock()) as reply, \
                     patch.object(bot.time, "time", return_value=100 + age):
                    await bot.status_command(SimpleNamespace(), SimpleNamespace())
                    self.assertIn(singular if age == 1 else f"{age} {plural}", reply.call_args.args[1])

    async def test_help_and_license_messages_have_balanced_markup(self):
        update = SimpleNamespace(effective_user=SimpleNamespace(first_name="A&B <Mario>"))
        context = SimpleNamespace(bot=SimpleNamespace(username="ToEnWikipediaBot"))
        for language in ("en", "it"):
            for handler in (bot.send_info, bot.license_command):
                with self.subTest(language=language, handler=handler.__name__), \
                     patch.object(bot, "_language", new=AsyncMock(return_value=language)), \
                     patch.object(bot, "_reply", new=AsyncMock()) as reply, \
                     patch.dict(os.environ, {"STATUS_CHANNEL_URL": "https://t.me/example"}):
                    await handler(update, context)
                    text = reply.call_args.args[1]
                    parser = MessageMarkup()
                    parser.feed(text)
                    parser.close()
                    self.assertEqual(parser.open_tags, [])
                    if handler == bot.send_info:
                        self.assertIn("A&amp;B &lt;Mario&gt;", text)
                        self.assertIn("/language", text)
                        self.assertIn("@ToEnWikipediaBot", text)
                    else:
                        self.assertIn("AGPL-3.0", text)
                        self.assertIn("CC BY-SA 4.0", text)


if __name__ == "__main__":
    unittest.main()
