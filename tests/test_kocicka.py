"""Tests for the parts of her that decide things: counting work, scheduling breaks,
remembering you. Standard library only, like her.   python -m unittest discover -s tests
"""
import contextlib
import io
import random
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kocicka as K  # noqa: E402

NOON = 12


def working_pet(now=1_000_000.0):
    """A cat that is already awake and counting, with her next pep talk far away."""
    p = K.Pet(1920, x=500)
    p.last_step = now
    p.next_line = now + 10 ** 9
    return p


class SelfTest(unittest.TestCase):
    def test_builtin_selftest_passes(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            K.selftest()
        self.assertEqual(out.getvalue().strip(), "ok")


class CountingWork(unittest.TestCase):
    def setUp(self):
        random.seed(7)

    def test_counts_real_time_while_you_are_there(self):
        p, now = working_pet(), 1_000_000.0
        for i in range(1, 101):
            p.step(now + i, NOON)
        self.assertAlmostEqual(p.worked, 100.0)

    def test_a_long_gap_counts_as_at_most_two_seconds(self):
        # the laptop slept, or the process was frozen: that hour was not work
        p, now = working_pet(), 1_000_000.0
        p.step(now + K.PAUSE_EVERY, NOON)
        self.assertEqual(p.worked, 2.0)
        self.assertNotEqual(p.state, "pause")

    def test_time_away_from_the_desk_does_not_count(self):
        p, now = working_pet(), 1_000_000.0
        p.worked = 600.0
        for i in range(1, 1000):
            self.assertEqual(p.step(now + i, NOON, away=True), "away")
        self.assertEqual(p.worked, 600.0)

    def test_night_does_not_count_and_never_breaks(self):
        p, now = working_pet(), 1_000_000.0
        p.worked = K.PAUSE_EVERY - 1
        for i in range(1, 100):
            self.assertEqual(p.step(now + i, 23), "sleep")
        self.assertEqual(p.worked, K.PAUSE_EVERY - 1)

    def test_clock_going_backwards_does_not_subtract(self):
        p, now = working_pet(), 1_000_000.0
        p.worked = 50.0
        p.step(now - 3600, NOON)
        self.assertEqual(p.worked, 50.0)

    def test_night_hours(self):
        start, end = K.NIGHT
        self.assertTrue(K.Pet(1000).asleep(start))
        self.assertTrue(K.Pet(1000).asleep(end - 1))
        self.assertFalse(K.Pet(1000).asleep(end))
        self.assertFalse(K.Pet(1000).asleep(start - 1))


class Breaks(unittest.TestCase):
    def setUp(self):
        random.seed(7)

    def test_break_starts_exactly_when_the_hour_of_work_is_full(self):
        p, now = working_pet(), 1_000_000.0
        p.worked = K.PAUSE_EVERY - 1.5
        self.assertNotEqual(p.step(now + 1, NOON), "pause")
        self.assertEqual(p.step(now + 2, NOON), "pause")
        self.assertEqual(p.worked, 0.0, "the hour resets the moment the break starts")
        self.assertEqual(p.pause_left(now + 2), K.PAUSE_SECS)

    def test_nothing_counts_during_the_break_and_counting_resumes_after(self):
        p, now = working_pet(), 1_000_000.0
        p.start_pause(now)
        for i in range(1, K.PAUSE_SECS):
            self.assertEqual(p.step(now + i, NOON), "pause")
        self.assertEqual(p.worked, 0.0)
        self.assertNotEqual(p.step(now + K.PAUSE_SECS, NOON), "pause")
        p.step(now + K.PAUSE_SECS + 1, NOON)
        self.assertAlmostEqual(p.worked, 1.0)

    def test_a_break_from_the_menu_resets_the_hour_too(self):
        p, now = working_pet(), 1_000_000.0
        p.worked = 1800.0
        p.start_pause(now)
        self.assertEqual((p.state, p.kind, p.worked), ("pause", "break", 0.0))

    def test_the_break_even_holds_through_night_and_absence(self):
        # once the sign is up it runs its course; she does not drop it mid-stretch
        p, now = working_pet(), 1_000_000.0
        p.start_pause(now)
        self.assertEqual(p.step(now + 1, 23, away=True), "pause")

    def test_a_new_stretch_every_few_seconds_and_never_a_blank_sign(self):
        p, now = working_pet(), 1_000_000.0
        p.start_pause(now)
        lines = [p.coach_line(now + s / 10) for s in range(K.PAUSE_SECS * 10)]
        self.assertNotIn("", lines)
        self.assertEqual(len(set(lines)), K.PAUSE_SECS // K.COACH_EVERY)
        self.assertEqual(K.Pet(1000).coach_line(now), "", "no break, no prompt")

    def test_breathing_follows_4_7_8_and_repeats(self):
        p, now = working_pet(), 1_000_000.0
        p.start_pause(now)
        start = p.pause_until - p.pause_span
        for offset, word in ((0.5, "nádech"), (5, "zadrž"), (12, "výdech"),
                             (19.5, "nádech")):
            p._breathe(start + offset)
            self.assertEqual(p.breath_word, word, offset)
            self.assertTrue(0.0 <= p.breath <= 1.0)

    def test_zoom_is_flat_outside_a_break(self):
        p, now = working_pet(), 1_000_000.0
        for state in ("walk", "idle", "sleep", "away"):
            p.state = state
            self.assertEqual(p.zoom(now), 1.0)

    def test_end_of_day_is_longer_and_she_lies_down_after(self):
        p, now = working_pet(), 1_000_000.0
        p.start_pause(now, "end")
        self.assertEqual(p.pause_left(now), K.END_SECS)
        self.assertIn(p.coach_line(now), K.END_COACH)
        self.assertEqual(p.step(now + K.END_SECS, NOON), "rest")


class Rolling(unittest.TestCase):
    def test_a_screen_narrower_than_her_window_keeps_her_at_zero(self):
        p, now = K.Pet(120, x=0), 1_000_000.0
        p.do("walk", now, 999)
        for i in range(100):
            p.step(now + i * 0.04, NOON)
            self.assertEqual(p.x, 0)


class Memory(unittest.TestCase):
    def test_round_trip_keeps_a_czech_name(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "kocka.json"
            cfg = {"name": "Mňaučka", "fur": "cerna", "cart": False}
            K.save_config(cfg, path)
            self.assertEqual(K.load_config(path), cfg)

    def test_a_json_list_is_not_a_config(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "kocka.json"
            path.write_text("[1, 2, 3]", encoding="utf-8")
            self.assertEqual(K.load_config(path), {})

    def test_greeting_survives_dates_it_cannot_read(self):
        cfg = {"name": "Micka", "first_seen": "loni", "last_seen": 5}
        self.assertEqual(K.greeting(cfg, "2026-10-13"), "ahoj, jsem Micka")

    def test_greeting_after_a_gap_and_on_consecutive_days(self):
        today = "2026-10-13"
        self.assertIn("5 dní", K.greeting(
            {"name": "C", "first_seen": "2026-10-01", "last_seen": "2026-10-08"}, today))
        self.assertIn("2. den", K.greeting(
            {"name": "C", "first_seen": "2026-10-12", "last_seen": "2026-10-12"}, today))

    def test_water_nag_survives_a_hand_edited_config(self):
        today = "2026-10-13"
        for water in ([], "lots", {"date": today, "count": "three"}):
            self.assertIsNotNone(K.water_line({"water": water}, today, 15), water)


class Sensing(unittest.TestCase):
    def test_without_windows_apis_she_assumes_you_are_there_and_not_sharing(self):
        with mock.patch.object(K, "_win32", return_value=(None, None)):
            self.assertEqual(K.idle_seconds(), 0.0)
            self.assertFalse(K.sharing_screen())

    def test_on_this_machine_sensing_never_throws(self):
        self.assertGreaterEqual(K.idle_seconds(), 0.0)
        self.assertIn(K.sharing_screen(), (True, False))


class Drawing(unittest.TestCase):
    """Every pose actually draws, in and out of the cart, facing both ways.

    Needs a display; skipped where Tk cannot open one (CI on Linux runs it under Xvfb).
    """

    @classmethod
    def setUpClass(cls):
        try:
            import tkinter as tk
            cls.root = tk.Tk()
        except Exception as e:  # ImportError without Tk, TclError without a display
            raise unittest.SkipTest("no Tk display: %s" % e)
        cls.root.withdraw()
        cls.tk = tk

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_every_pose(self):
        c = self.tk.Canvas(self.root, width=K.W, height=K.H)
        states = set(K.TRICKS) | {"sleep", "away", "pause", "highfive"}
        for state in sorted(states):
            for cart in (True, False):
                for direction in (1, -1):
                    p = K.Pet(1000)
                    p.state, p.cart, p.dir, p.progress = state, cart, direction, 0.8
                    p.say = "mrrr" if direction > 0 else ""
                    K.draw(c, p, 30)
                    self.assertTrue(c.find_all(), (state, cart, direction))

    def test_break_sign_at_full_zoom(self):
        p, now = working_pet(), 1_000_000.0
        p.start_pause(now)
        p.step(now + 9, NOON)
        k = p.zoom(now + 9)
        c = self.tk.Canvas(self.root, width=int(K.W * k), height=int((K.H + K.PAUSE_EXTRA) * k))
        K.draw(c, p, 30)
        K.zoom_canvas(c, k)
        K.draw_sign(c, int(K.W * k), k, p, now + 9)
        texts = [c.itemcget(i, "text") for i in c.find_all() if c.type(i) == "text"]
        self.assertIn("STOP", texts)
        self.assertIn(p.coach_line(now + 9), texts)


if __name__ == "__main__":
    unittest.main()
