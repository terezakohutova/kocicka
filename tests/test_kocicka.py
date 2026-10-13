"""Tests for the parts of her that decide things: counting work, scheduling breaks,
remembering you, what a click does, where she stands. Standard library only, like her.

    python -m unittest discover -s tests -v
"""
import ast
import ctypes
import random
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import kocicka as K  # noqa: E402

NOON = 12
NOW = 1_000_000.0
TODAY = "2026-10-13"
S = K.STRINGS


def working_pet(now=NOW):
    """A cat that is already awake and counting, with her next pep talk far away."""
    p = K.Pet(1920, x=500)
    p.last_step = now
    p.next_line = now + 10 ** 9
    p.until = now + 10 ** 9              # and no new trick unless a test asks for one
    return p


class Seeded(unittest.TestCase):
    """Every test starts from the same dice, so a failure can be replayed."""

    def setUp(self):
        random.seed(7)


# --------------------------------------------------------------------------- the pet

class CountingWork(Seeded):
    def test_counts_real_time_while_you_are_there(self):
        p = working_pet()
        for i in range(1, 101):
            p.step(NOW + i, NOON)
        self.assertAlmostEqual(p.worked, 100.0)
        self.assertAlmostEqual(p.total, 100.0)

    def test_a_long_gap_counts_as_at_most_two_seconds(self):
        # the laptop slept, or the process was frozen: that hour was not work
        p = working_pet()
        p.step(NOW + K.PAUSE_EVERY, NOON)
        self.assertEqual(p.worked, 2.0)
        self.assertEqual(p.state, "idle")

    def test_time_away_from_the_desk_does_not_count(self):
        p = working_pet()
        p.worked = 600.0
        for i in range(1, 1000):
            self.assertEqual(p.step(NOW + i, NOON, away=True), "away")
        self.assertEqual(p.worked, 600.0)

    def test_night_counts_too_while_she_dozes(self):
        p = working_pet()
        p.worked = 100.0
        for i in range(1, 100):
            self.assertEqual(p.step(NOW + i, 23), "sleep")
        self.assertAlmostEqual(p.worked, 199.0, msg="a night owl's hour is still an hour")

    def test_clock_going_backwards_does_not_subtract(self):
        p = working_pet()
        p.worked = 50.0
        p.step(NOW - 3600, NOON)
        self.assertEqual(p.worked, 50.0)

    def test_night_hours(self):
        start, end = K.NIGHT
        p = K.Pet(1000)
        self.assertTrue(p.asleep(start))
        self.assertTrue(p.asleep(end - 1))
        self.assertFalse(p.asleep(end))
        self.assertFalse(p.asleep(start - 1))

    def test_time_behind_a_fullscreen_app_still_counts(self):
        # a call or a presentation is work; she only stops drawing
        p = working_pet()
        for i in range(1, 101):
            p.step(NOW + i, NOON, hidden=True)
        self.assertAlmostEqual(p.worked, 100.0)

    def test_a_due_break_waits_until_she_is_visible_again(self):
        p = working_pet()
        p.worked = K.PAUSE_EVERY - 1
        for i in range(1, 20):
            self.assertNotEqual(p.step(NOW + i, NOON, hidden=True), "pause")
        self.assertGreater(p.worked, K.PAUSE_EVERY)
        self.assertEqual(p.step(NOW + 20, NOON), "pause")

    def test_she_keeps_quiet_while_hidden(self):
        p = working_pet()
        p.next_line, p.say = NOW, ""
        p.step(NOW + 1, NOON, hidden=True)
        self.assertEqual(p.say, "")
        self.assertGreater(p.next_line, NOW + 1)


class Breaks(Seeded):
    def test_break_starts_exactly_when_the_hour_of_work_is_full(self):
        p = working_pet()
        p.worked = K.PAUSE_EVERY - 1.5
        self.assertEqual(p.step(NOW + 1, NOON), "idle")
        self.assertEqual(p.step(NOW + 2, NOON), "pause")
        self.assertEqual(p.worked, 0.0, "the hour resets the moment the break starts")
        self.assertEqual(p.pause_left(NOW + 2), K.PAUSE_SECS)
        self.assertEqual(p.say, "", "the sign replaces the bubble")

    def test_nothing_counts_during_the_break_and_counting_resumes_after(self):
        p = working_pet()
        p.start_pause(NOW)
        for i in range(1, K.PAUSE_SECS):
            self.assertEqual(p.step(NOW + i, NOON), "pause")
        self.assertEqual(p.worked, 0.0)
        self.assertEqual(p.step(NOW + K.PAUSE_SECS, NOON), "idle")
        p.step(NOW + K.PAUSE_SECS + 1, NOON)
        self.assertAlmostEqual(p.worked, 1.0)

    def test_she_stays_put_while_the_sign_is_up(self):
        p = working_pet()
        p.start_pause(NOW)
        for i in range(1, 10):
            p.step(NOW + i, NOON)
            self.assertEqual(p.x, 500)

    def test_a_break_from_the_menu_resets_the_hour_too(self):
        p = working_pet()
        p.worked = 1800.0
        p.start_pause(NOW)
        self.assertEqual((p.state, p.kind, p.worked), ("pause", "break", 0.0))

    def test_the_break_even_holds_through_night_and_absence(self):
        # once the sign is up it runs its course; she does not drop it mid-stretch
        p = working_pet()
        p.start_pause(NOW)
        self.assertEqual(p.step(NOW + 1, 23, away=True), "pause")

    def test_a_new_stretch_every_few_seconds_and_never_a_blank_sign(self):
        p = working_pet()
        p.start_pause(NOW)
        lines = [p.coach_line(NOW + s / 10) for s in range(K.PAUSE_SECS * 10)]
        self.assertNotIn("", lines)
        self.assertEqual(len(set(lines)), K.PAUSE_SECS // K.COACH_EVERY)
        self.assertLessEqual(set(lines), set(S["pause_coach"]))
        self.assertEqual(K.Pet(1000).coach_line(NOW), "", "no break, no prompt")

    def test_breathing_follows_4_7_8_and_repeats(self):
        p = working_pet()
        p.start_pause(NOW)
        inhale, hold, exhale = S["breath"]
        for offset, word, breath in ((2, inhale, 0.5), (5, hold, 1.0), (15, exhale, 0.5),
                                     (21, inhale, 0.5)):
            p._breathe(NOW + offset)
            self.assertEqual(p.breath_word, word, offset)
            self.assertAlmostEqual(p.breath, breath)

    def test_zoom_eases_up_and_back_down(self):
        p = working_pet()
        p.start_pause(NOW)
        self.assertEqual(p.zoom(NOW), 1.0)
        self.assertEqual(p.zoom(NOW + 0.25), 1.0 + (K.PAUSE_ZOOM - 1.0) / 2)
        self.assertEqual(p.zoom(NOW + 1), K.PAUSE_ZOOM)
        self.assertEqual(p.zoom(p.pause_until - 0.25), 1.0 + (K.PAUSE_ZOOM - 1.0) / 2)
        self.assertEqual(p.zoom(p.pause_until), 1.0)

    def test_zoom_is_flat_outside_a_break(self):
        p = working_pet()
        for state in ("walk", "idle", "sleep", "away"):
            p.state = state
            self.assertEqual(p.zoom(NOW), 1.0)

    def test_end_of_day_is_longer_and_she_lies_down_after(self):
        p = working_pet()
        p.start_pause(NOW, "end")
        self.assertEqual(p.pause_left(NOW), K.END_SECS)
        self.assertIn(p.coach_line(NOW), S["end_coach"])
        self.assertEqual(p.step(NOW + K.END_SECS, NOON), "rest")


class Behaviour(Seeded):
    def test_do_with_none_picks_her_usual_length_and_zero_means_zero(self):
        p = K.Pet(1000)
        p.do("lick", NOW)
        low, high = K.DURATION["lick"]
        self.assertTrue(NOW + low <= p.until <= NOW + high)
        p.do("idle", NOW, 0)
        self.assertEqual(p.until, NOW)

    def test_bounces_off_both_edges_and_never_escapes(self):
        for width in (1920, 400, 120):
            p = K.Pet(width, x=0)
            p.do("walk", NOW, 999)
            p.dir = -1
            turned = 0
            for i in range(3000):
                before = p.dir
                p.step(NOW + i * 0.04, NOON)
                turned += p.dir != before
                self.assertTrue(0 <= p.x <= p.max_x, (width, p.x))
            if p.max_x:
                self.assertGreaterEqual(turned, 2, width)

    def test_she_sleeps_at_night_and_wakes_quietly(self):
        p = working_pet()
        p.next_line = NOW - 1
        self.assertEqual(p.step(NOW, 23), "sleep")
        self.assertEqual(p.say, "")
        self.assertGreater(p.next_line, NOW, "no blurting the second she wakes up")
        woke = p.step(NOW + 1, 8)
        self.assertIn(woke, K.TRICKS, "back to her own business")
        self.assertNotIn(p.say, S["lines"], "and no pep talk the second she wakes")

    def test_she_notices_you_came_back(self):
        p = working_pet()
        p.step(NOW + 1, NOON, away=True)
        p.step(NOW + 2, NOON)
        self.assertEqual(p.state, "idle")
        self.assertIn(p.say, S["back"])

    def test_pep_talk_when_it_is_due_and_bubble_expires(self):
        p = working_pet()
        p.until, p.next_line = NOW + 9999, NOW
        p.step(NOW + 1, NOON)
        self.assertIn(p.say, S["lines"])
        self.assertGreater(p.next_line, NOW + 1)
        p.step(NOW + 9, NOON)
        self.assertEqual(p.say, "")

    def test_wheels_turn_only_while_she_rolls(self):
        p = working_pet()
        p.do("walk", NOW, 999)
        p.step(NOW + 0.04, NOON)
        self.assertEqual(p.roll, K.SPEED)
        p.do("idle", NOW, 999)
        p.step(NOW + 0.08, NOON)
        self.assertEqual(p.roll, K.SPEED)

    def test_every_trick_turns_up_but_no_sitting_in_the_cart(self):
        p = working_pet()
        seen = set()
        for i in range(800):
            p.until, p.worked = 0.0, 0.0       # force a fresh trick every step
            seen.add(p.step(NOW + i * 0.01, NOON))
        self.assertNotIn("sit", seen)
        self.assertLessEqual({"walk", "idle", "lick", "meow", "milk", "grass", "rest",
                              "highfive", "butt"}, seen)
        p.cart = False
        for i in range(800):
            p.until, p.worked = 0.0, 0.0
            seen.add(p.step(NOW + 10 + i * 0.01, NOON))
        self.assertIn("sit", seen)

    def test_hairballs_follow_grass(self):
        p = working_pet()
        results = []
        for i in range(40):
            p.do("grass", NOW, 0)
            results.append(p.step(NOW + i * 0.01, NOON))
        self.assertIn("hairball", results)
        self.assertIn(p.say if p.state == "hairball" else S["hairball"][0], S["hairball"])


# --------------------------------------------------------------------------- what she says

class Words(unittest.TestCase):
    def test_everything_fits(self):
        self.assertTrue(all(len(s) <= 70 for s in S["lines"]), "longer lines overflow")
        self.assertGreaterEqual(len(S["lines"]), 20)
        self.assertTrue(all(len(s) <= 60 for s in S["pause_coach"] + S["end_coach"]))

    def test_the_breathing_pep_talk_matches_the_4_7_8_she_coaches(self):
        breathing = [s for s in S["lines"] if s.startswith("nádech")]
        self.assertEqual(breathing, ["nádech na čtyři, zadrž na sedm, výdech na osm. "
                                     "předu s tebou"])

    def test_all_user_facing_text_lives_in_the_strings_table(self):
        # the README promises this; any Czech outside STRINGS breaks the promise
        tree = ast.parse((ROOT / "kocicka.py").read_text(encoding="utf-8"))
        table = next(n for n in tree.body if isinstance(n, ast.Assign)
                     and getattr(n.targets[0], "id", "") == "STRINGS")
        inside = {id(n) for n in ast.walk(table)}
        stray = [n.value for n in ast.walk(tree)
                 if isinstance(n, ast.Constant) and isinstance(n.value, str)
                 and id(n) not in inside and any(ord(ch) > 127 for ch in n.value)]
        self.assertEqual(stray, [])

    def test_every_key_the_code_asks_for_exists(self):
        tree = ast.parse((ROOT / "kocicka.py").read_text(encoding="utf-8"))
        asked = {n.slice.value for n in ast.walk(tree)
                 if isinstance(n, ast.Subscript) and getattr(n.value, "id", "") == "STRINGS"
                 and isinstance(n.slice, ast.Constant)}
        self.assertTrue(asked)
        self.assertLessEqual(asked, set(S))

    def test_every_palette_is_offered(self):
        self.assertEqual({k for k, _ in S["fur_labels"]}, set(K.PALETTES))
        self.assertTrue(all(len(v) == 3 for v in K.PALETTES.values()), "fur, shading, nose")


# --------------------------------------------------------------------------- her memory

class Memory(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.dir = Path(self.folder.name)
        self.store = K.Store(self.dir / "cfg" / "kocka.json", legacy=None)

    def tearDown(self):
        self.folder.cleanup()

    def test_round_trip_keeps_a_czech_name_and_makes_the_folder(self):
        cfg = {"name": "Mňaučka", "fur": "cerna", "cart": False}
        self.assertTrue(self.store.save(cfg))
        self.assertEqual(self.store.load(), cfg)

    def test_missing_corrupt_or_not_a_dict_means_start_over(self):
        self.assertEqual(self.store.load(), {})
        self.store.path.parent.mkdir()
        for text in ("{ rozbite", "[1, 2, 3]"):
            self.store.path.write_text(text, encoding="utf-8")
            self.assertEqual(self.store.load(), {})

    def test_writes_are_atomic_and_keep_the_previous_version(self):
        self.store.save({"name": "Micka"})
        self.store.save({"name": "Mourek"})
        self.assertEqual(self.store.load(), {"name": "Mourek"})
        self.assertEqual(K._read_json(self.store.backup), {"name": "Micka"})
        self.assertEqual(sorted(p.name for p in self.store.path.parent.iterdir()),
                         ["kocka.json", "kocka.json.bak"], "no temp file left behind")

    def test_a_corrupt_file_falls_back_to_the_backup(self):
        self.store.save({"name": "Micka"})
        self.store.save({"name": "Mourek"})
        self.store.path.write_text("{ half writ", encoding="utf-8")
        self.assertEqual(self.store.load(), {"name": "Micka"})

    def test_a_failed_write_leaves_the_old_file_alone(self):
        self.store.save({"name": "Micka"})
        with mock.patch.object(K.os, "replace", side_effect=OSError("disk full")):
            self.assertFalse(self.store.save({"name": "Mourek"}))
        self.assertEqual(self.store.load(), {"name": "Micka"})
        self.assertFalse(self.store.path.with_name("kocka.json.tmp").exists())

    def test_an_unwritable_place_is_reported_not_raised(self):
        blocker = self.dir / "a-file"
        blocker.write_text("", encoding="utf-8")
        self.assertFalse(K.Store(blocker / "kocka.json", legacy=None).save({"name": "x"}))

    def test_moves_in_from_the_old_place_next_to_the_script(self):
        old = self.dir / "kocka.json"
        old.write_text('{"name": "Micka", "fur": "seda"}', encoding="utf-8")
        store = K.Store(self.dir / "new" / "kocka.json", legacy=old)
        self.assertEqual(store.load(), {"name": "Micka", "fur": "seda"})
        self.assertEqual(K._read_json(store.path), {"name": "Micka", "fur": "seda"})
        self.assertTrue(old.exists(), "the old file is left alone, not deleted")
        old.write_text('{"name": "Stara"}', encoding="utf-8")
        self.assertEqual(store.load()["name"], "Micka", "the new place wins from then on")

    def test_config_folder_per_system(self):
        home = Path("/home/t")
        self.assertEqual(K.config_dir("win32", {"APPDATA": "C:/Users/t/AppData/Roaming"}, home),
                         Path("C:/Users/t/AppData/Roaming/kocicka"))
        self.assertEqual(K.config_dir("win32", {}, home),
                         home / "AppData" / "Roaming" / "kocicka")
        self.assertEqual(K.config_dir("darwin", {}, home),
                         home / "Library" / "Application Support" / "kocicka")
        self.assertEqual(K.config_dir("linux", {"XDG_CONFIG_HOME": "/xdg"}, home),
                         Path("/xdg/kocicka"))
        self.assertEqual(K.config_dir("linux", {}, home), home / ".config" / "kocicka")
        self.assertEqual(K.config_dir("linux", {"XDG_CONFIG_HOME": "relative"}, home),
                         home / ".config" / "kocicka", "the spec says ignore relative paths")

    def test_greeting(self):
        self.assertEqual(K.greeting({"name": "Claudie"}, TODAY), S["hello"] % "Claudie")
        self.assertEqual(K.greeting({}, TODAY), S["hello"] % S["fallback_name"])
        self.assertIn("12. den", K.greeting(
            {"name": "C", "first_seen": "2026-10-02", "last_seen": "2026-10-12"}, TODAY))
        self.assertIn("3 dny", K.greeting(
            {"name": "C", "first_seen": "2026-09-01", "last_seen": "2026-10-10"}, TODAY))
        self.assertIn("5 dní", K.greeting(
            {"name": "C", "first_seen": "2026-10-01", "last_seen": "2026-10-08"}, TODAY))
        self.assertEqual(K.greeting({"name": "M", "first_seen": "loni", "last_seen": 5}, TODAY),
                         S["hello"] % "M")
        self.assertEqual([K.czech_days(n) for n in (1, 4, 9)], ["1 den", "4 dny", "9 dní"])

    def test_water_nag(self):
        self.assertIsNone(K.water_line({}, TODAY, 9), "no nagging before the afternoon")
        self.assertEqual(K.water_line({}, TODAY, 15), S["water_none"])
        self.assertEqual(K.water_line({"water": {"date": TODAY, "count": 3}}, TODAY, 15),
                         S["water_some"] % 3)
        self.assertIsNone(K.water_line({"water": {"date": TODAY, "count": K.WATER_GOAL}},
                                       TODAY, 15))
        self.assertEqual(K.water_line({"water": {"date": "2026-10-12", "count": 9}}, TODAY, 15),
                         S["water_none"], "yesterday's glasses don't count")
        for water in ([], "lots", {"date": TODAY, "count": "three"}):
            self.assertEqual(K.water_line({"water": water}, TODAY, 15), S["water_none"], water)


# --------------------------------------------------------------------------- the app, headless

class FailingStore:
    def __init__(self):
        self.saves = 0

    def save(self, cfg):
        self.saves += 1
        return False


class AppTest(Seeded):
    def setUp(self):
        super().setUp()
        self.folder = tempfile.TemporaryDirectory()
        self.store = K.Store(Path(self.folder.name) / "kocka.json", legacy=None)

    def tearDown(self):
        self.folder.cleanup()

    def app(self, cfg=None, scale=1.0, today=TODAY):
        pet = working_pet()
        cfg = {"name": "Micka"} if cfg is None else cfg
        return K.Companion(cfg, self.store, pet, today, NOW, scale)

    def work(self, app, seconds, hour=NOON, start=NOW):
        for i in range(1, int(seconds) + 1):
            app.pet.step(start + i, hour)
        return start + seconds


class Day(AppTest):
    def test_past_midnight_yesterdays_one_thing_is_gone_and_she_asks_again(self):
        app = self.app({"name": "M", "focus": {"date": TODAY, "text": "daně", "done": False}})
        self.assertEqual(app.focus_label(), S["focus_today"] + "daně")
        self.assertFalse(app.wants_focus(9))
        app.slow(NOW, 0, "2026-10-14", 0.0, False)
        self.assertEqual(app.focus_label(), S["focus_none"])
        self.assertEqual(app.cfg["last_seen"], "2026-10-14")
        self.assertFalse(app.wants_focus(0), "not at half past midnight")
        self.assertTrue(app.wants_focus(9), "but in the morning, yes")
        app.set_focus("  prezentace  ", NOW)
        self.assertFalse(app.wants_focus(10), "once a day")
        self.assertEqual(app.focus_label(), S["focus_today"] + "prezentace")
        self.assertEqual(self.store.load()["focus"]["date"], "2026-10-14")

    def test_an_empty_answer_counts_as_asked(self):
        app = self.app()
        app.set_focus(None, NOW)
        self.assertFalse(app.wants_focus(9))
        self.assertEqual(app.focus_label(), S["focus_none"])
        self.assertFalse(app.toggle_focus(NOW), "nothing to tick off")

    def test_she_does_not_ask_into_an_empty_room_or_over_a_presentation(self):
        app = self.app()
        app.away = True
        self.assertFalse(app.wants_focus(9))
        app.away, app.hidden = False, True
        self.assertFalse(app.wants_focus(9))
        app.hidden = False
        app.pet.start_pause(NOW)
        self.assertFalse(app.wants_focus(9))
        self.assertFalse(app.wants_focus(K.WORK_END), "too late to promise anything")

    def test_ticking_the_one_thing_off_and_back(self):
        app = self.app()
        app.set_focus("daně", NOW)
        self.assertTrue(app.toggle_focus(NOW))
        self.assertEqual(app.focus_label(), S["focus_done"] + "daně")
        self.assertEqual(app.pet.say, S["focus_proud"])
        app.toggle_focus(NOW)
        self.assertEqual(app.focus_label(), S["focus_today"] + "daně")

    def test_water_counts_today_only(self):
        app = self.app({"name": "M", "water": {"date": "2026-10-12", "count": 5}})
        app.drank(NOW)
        self.assertEqual(app.cfg["water"], {"date": TODAY, "count": 1})
        self.assertEqual(app.pet.say, S["water_count"] % (1, K.WATER_GOAL - 1))

    def test_an_unwritable_memory_is_mentioned_once(self):
        store = FailingStore()
        app = K.Companion({"name": "M"}, store, working_pet(), TODAY, NOW)
        self.assertFalse(app.save(NOW))
        self.assertEqual(app.pet.say, S["cant_save"])
        app.pet.say = ""
        app.drank(NOW)
        self.assertNotEqual(app.pet.say, S["cant_save"])
        self.assertEqual(store.saves, 2)


class EndOfDay(AppTest):
    def test_starting_after_work_end_shows_no_sign_until_real_work(self):
        app = self.app()
        app.slow(NOW, K.WORK_END, TODAY, 0.0, False)
        self.assertNotEqual(app.pet.state, "pause")
        now = self.work(app, K.END_AFTER_WORK, hour=K.WORK_END)
        app.slow(now, K.WORK_END, TODAY, 0.0, False)
        self.assertEqual((app.pet.state, app.pet.kind), ("pause", "end"))
        self.assertEqual(app.cfg["ended"], TODAY)

    def test_only_once_a_day(self):
        app = self.app()
        now = self.work(app, K.END_AFTER_WORK, hour=K.WORK_END)
        app.slow(now, K.WORK_END, TODAY, 0.0, False)
        app.pet.finish_pause(now)
        app.pet.state = "idle"
        app.slow(now + 5, K.WORK_END, TODAY, 0.0, False)
        self.assertEqual(app.pet.state, "idle")

    def test_not_before_work_end_not_away_not_hidden(self):
        app = self.app()
        now = self.work(app, K.END_AFTER_WORK, hour=K.WORK_END - 1)
        app.slow(now, K.WORK_END - 1, TODAY, 0.0, False)
        self.assertNotEqual(app.pet.state, "pause")
        app.slow(now, K.WORK_END, TODAY, K.AWAY_AFTER + 1, False)
        self.assertNotEqual(app.pet.state, "pause")
        app.slow(now, K.WORK_END, TODAY, 0.0, True)
        self.assertNotEqual(app.pet.state, "pause")

    def test_work_before_midnight_does_not_count_for_the_next_day(self):
        app = self.app()
        now = self.work(app, K.END_AFTER_WORK, hour=K.WORK_END - 1)
        app.slow(now, 7, "2026-10-14", 0.0, False)
        self.assertEqual(app.worked_today(), 0.0)

    def test_a_click_dismisses_the_end_sign_but_not_the_hourly_one(self):
        app = self.app()
        app.pet.start_pause(NOW, "end")
        app.press(100)
        self.assertEqual(app.release(100, 100, NOW + 1), "dismissed")
        self.assertEqual(app.pet.state, "rest")
        app.pet.start_pause(NOW + 2)
        app.press(100)
        self.assertEqual(app.release(100, 100, NOW + 3), "held")
        self.assertEqual(app.pet.state, "pause")

    def test_snoozing_the_end_sign_brings_it_back_in_ten_minutes(self):
        app = self.app()
        now = self.work(app, K.END_AFTER_WORK, hour=K.WORK_END)
        app.slow(now, K.WORK_END, TODAY, 0.0, False)
        app.snooze(now)
        self.assertEqual(app.pet.state, "idle")
        app.slow(now + K.SNOOZE - 1, K.WORK_END, TODAY, 0.0, False)
        self.assertNotEqual(app.pet.state, "pause")
        app.slow(now + K.SNOOZE, K.WORK_END, TODAY, 0.0, False)
        self.assertEqual((app.pet.state, app.pet.kind), ("pause", "end"))


class SkipAndSnooze(AppTest):
    def test_skip_puts_the_sign_down(self):
        app = self.app()
        app.pet.start_pause(NOW)
        app.skip(NOW + 3)
        self.assertEqual(app.pet.state, "idle")
        self.assertEqual(app.pet.say, S["skipped"])
        self.assertEqual(app.pet.worked, 0.0, "a full hour until the next one")

    def test_skip_before_a_break_skips_the_coming_one(self):
        app = self.app()
        app.pet.worked = K.PAUSE_EVERY - 30
        app.skip(NOW)
        self.assertEqual(app.pet.worked, 0.0)

    def test_snooze_brings_the_break_back_after_ten_minutes_of_work(self):
        app = self.app()
        app.pet.start_pause(NOW)
        app.snooze(NOW + 1)
        self.assertEqual(app.pet.state, "idle")
        app.pet.last_step = NOW + 1
        for i in range(1, K.SNOOZE):
            self.assertNotEqual(app.pet.step(NOW + 1 + i, NOON), "pause")
        self.assertEqual(app.pet.step(NOW + 1 + K.SNOOZE, NOON), "pause")

    def test_snooze_never_brings_a_break_closer(self):
        app = self.app()
        app.pet.worked = 60.0
        app.snooze(NOW)
        self.assertEqual(app.pet.worked, 60.0)


class Clicks(AppTest):
    def click(self, app, x, y):
        app.press(0)
        return app.release(x, y, NOW)

    def test_the_bowl_is_under_her_nose_whichever_way_she_faces(self):
        for scale in (1.0, 2.0):
            app = self.app(scale=scale)
            app.pet.do("milk", NOW, 99)
            y = (K.GROUND - 10) * scale
            right_side, left_side = 150 * scale, (K.W - 150) * scale
            app.pet.dir = 1
            self.assertEqual(self.click(app, right_side, y), "drank", scale)
            app.pet.do("milk", NOW, 99)
            self.assertEqual(self.click(app, left_side, y), "highfive", scale)
            app.pet.do("milk", NOW, 99)
            app.pet.dir = -1
            self.assertEqual(self.click(app, left_side, y), "drank", scale)
            app.pet.do("milk", NOW, 99)
            self.assertEqual(self.click(app, right_side, y), "highfive", scale)
            self.assertEqual(app.cfg["water"]["count"], 2)

    def test_bowl_box_mirrors(self):
        x1, y1, x2, y2 = K.bowl_box(1)
        self.assertEqual(K.bowl_box(-1), (K.W - x2, y1, K.W - x1, y2))

    def test_a_click_gets_a_paw_and_a_line(self):
        app = self.app()
        self.assertEqual(self.click(app, 100, 100), "highfive")
        self.assertEqual(app.pet.state, "highfive")
        self.assertIn(app.pet.say, S["lines"])

    def test_a_drag_moves_her_and_is_not_a_click(self):
        app = self.app(scale=2.0)
        app.pet.screen_w = 2000
        app.pet.x = 500
        app.press(1000)
        app.drag(1040)
        self.assertEqual(app.pet.x, 520, "screen pixels are halved at 200 %")
        self.assertEqual(app.release(10, 10, NOW), "drag")
        self.assertNotEqual(app.pet.state, "highfive")

    def test_cart_and_rename(self):
        app = self.app()
        app.pet.state = "sit"
        app.set_cart(True, NOW)
        self.assertEqual(app.pet.state, "idle", "no sitting in the cart")
        self.assertFalse(app.rename(None, NOW), "closing the window changes nothing")
        self.assertEqual(app.cfg["name"], "Micka")
        self.assertTrue(app.rename({"name": "Mourek", "fur": "cerna", "cart": True}, NOW))
        self.assertEqual((app.pet.fur, app.pet.colours), ("cerna", K.PALETTES["cerna"]))
        self.assertEqual(app.pet.say, S["renamed"] % "Mourek")
        self.assertFalse(hasattr(K, "FUR"), "colours live on the cat, not in globals")


class Screen(AppTest):
    def test_hides_and_shows_with_a_fullscreen_app(self):
        app = self.app()
        self.assertTrue(app.slow(NOW, NOON, TODAY, 0.0, True))
        self.assertTrue(app.hidden)
        self.assertFalse(app.slow(NOW + 1, NOON, TODAY, 0.0, True), "no change, no flicker")
        self.assertFalse(app.advance(NOW + 1, NOON), "nothing to draw while hidden")
        self.assertEqual(app.tick_ms(), K.TICK_HIDDEN)
        self.assertTrue(app.slow(NOW + 2, NOON, TODAY, 0.0, False))
        self.assertTrue(app.advance(NOW + 2, NOON))

    def test_redraws_only_when_something_changed(self):
        app = self.app()
        app.pet.do("idle", NOW, 999)
        self.assertTrue(app.advance(NOW, NOON))
        self.assertFalse(app.advance(NOW, NOON), "same moment, same picture")
        self.assertTrue(app.advance(NOW + 0.2, NOON), "her breathing moved on")

    def test_ticks_slower_when_nothing_moves_fast(self):
        app = self.app()
        app.pet.do("walk", NOW, 999)
        self.assertEqual(app.tick_ms(), K.TICK)
        app.pet.do("idle", NOW, 999)
        self.assertEqual(app.tick_ms(), 2 * K.TICK)
        app.pet.state = "sleep"
        self.assertEqual(app.tick_ms(), K.TICK_SLEEP)
        self.assertEqual(app.frame(NOW + 0.2) % 6, 0, "coarser frames while she sleeps")
        app.press(0)
        self.assertEqual(app.tick_ms(), K.TICK, "but smooth while you drag her")

    def test_asleep_she_redraws_a_few_times_a_second_not_twenty_five(self):
        app = self.app()
        app.pet.state = "sleep"
        ticks = 250                              # ten seconds' worth of 25-a-second frames
        draws = sum(app.advance(NOW + i * K.TICK / 1000, 23) for i in range(ticks))
        self.assertLessEqual(draws, ticks / 6 + 1)

    def test_stands_on_the_work_area_and_grows_around_herself(self):
        app = self.app()
        app.slow(NOW, NOON, TODAY, 0.0, False, (100, 0, 1100, 740))
        self.assertEqual(app.pet.screen_w, 1000)
        app.pet.x = 400
        k, extra, cw, ch, x, y = app.layout(NOW)
        self.assertEqual((k, extra, cw, ch, x, y), (1.0, 0, K.W, K.H, 500, 740 - K.H))
        app.pet.start_pause(NOW)
        k, extra, cw, ch, x, y = app.layout(NOW + 5)
        self.assertEqual((k, extra), (K.PAUSE_ZOOM, K.PAUSE_EXTRA))
        self.assertEqual(x + cw / 2, 500 + K.W / 2, "centred on where she was")
        self.assertEqual(y + ch, 740, "feet still on the taskbar line")

    def test_never_leaves_the_work_area(self):
        app = self.app(scale=1.5)
        app.slow(NOW, NOON, TODAY, 0.0, False, (-1920, 0, 0, 1040))
        self.assertEqual(app.pet.screen_w, 1920 / 1.5)
        for px in (0, app.pet.max_x):
            app.pet.x = px
            app.pet.start_pause(NOW)
            for t in (NOW, NOW + 5):
                _, _, cw, ch, x, y = app.layout(t)
                self.assertTrue(x >= -1920 and x + cw <= 0, (px, x, cw))
                self.assertEqual(y + ch, 1040)

    def test_display_scaling_makes_her_bigger_not_blurrier(self):
        app = self.app(scale=2.0)
        k, _, cw, ch, _, _ = app.layout(NOW)
        self.assertEqual((k, cw, ch), (2.0, 2 * K.W, 2 * K.H))


# --------------------------------------------------------------------------- the OS

class FakeUser32:
    """Answers the handful of user32 questions she asks, the way Windows would."""

    def __init__(self, window, monitor, style=0, cls="Chrome_WidgetWin_1", work=None):
        self.window, self.monitor, self.style, self.cls = window, monitor, style, cls
        self.work = work

    def GetForegroundWindow(self):
        return 100

    def GetShellWindow(self):
        return 1

    def GetDesktopWindow(self):
        return 2

    def GetWindowLongW(self, hwnd, index):
        return self.style

    def GetClassNameW(self, hwnd, buf, size):
        buf.value = self.cls
        return len(self.cls)

    def GetWindowRect(self, hwnd, ref):
        r = ref._obj
        r.left, r.top, r.right, r.bottom = self.window
        return 1

    def MonitorFromWindow(self, hwnd, flags):
        return 7

    def GetMonitorInfoW(self, monitor, ref):
        m = ref._obj.rcMonitor
        m.left, m.top, m.right, m.bottom = self.monitor
        return 1

    def SystemParametersInfoW(self, action, param, ref, flags):
        if not self.work:
            return 0
        r = ref._obj
        r.left, r.top, r.right, r.bottom = self.work
        return 1


class Sensing(unittest.TestCase):
    def fullscreen(self, **kw):
        with mock.patch.object(K, "_win32", return_value=(FakeUser32(**kw), None)):
            return K.fullscreen_in_front()

    def test_without_windows_apis_she_assumes_you_are_there_and_nothing_is_fullscreen(self):
        with mock.patch.object(K, "_win32", return_value=(None, None)):
            self.assertEqual(K.idle_seconds("win32"), 0.0)
            self.assertFalse(K.fullscreen_in_front())
            self.assertEqual(K.work_area(1920, 1080), (0, 0, 1920, 1080 - K.TASKBAR))

    def test_fullscreen_on_the_main_monitor(self):
        self.assertTrue(self.fullscreen(window=(0, 0, 1920, 1080), monitor=(0, 0, 1920, 1080)))

    def test_fullscreen_on_a_second_monitor_counts_too(self):
        self.assertTrue(self.fullscreen(window=(1920, 0, 4480, 1440),
                                        monitor=(1920, 0, 4480, 1440)))

    def test_a_big_window_on_a_small_monitor_is_judged_by_its_own_monitor(self):
        # 1920 wide covers a 1280 laptop panel; it would not cover a 2560 one
        self.assertTrue(self.fullscreen(window=(-1280, 0, 640, 1080),
                                        monitor=(-1280, 0, 0, 800)))
        self.assertFalse(self.fullscreen(window=(1920, 0, 3840, 1080),
                                         monitor=(1920, 0, 4480, 1440)))

    def test_a_maximised_window_with_a_title_bar_is_not_fullscreen(self):
        self.assertFalse(self.fullscreen(window=(0, 0, 1920, 1080), monitor=(0, 0, 1920, 1080),
                                         style=0x00C00000))

    def test_clicking_the_wallpaper_is_not_a_presentation(self):
        for cls in ("WorkerW", "Progman"):
            self.assertFalse(self.fullscreen(window=(0, 0, 1920, 1080),
                                             monitor=(0, 0, 1920, 1080), cls=cls))

    def test_work_area_comes_from_windows_when_it_answers(self):
        fake = FakeUser32((0, 0, 0, 0), (0, 0, 0, 0), work=(0, 0, 2560, 1392))
        with mock.patch.object(K, "_win32", return_value=(fake, None)):
            self.assertEqual(K.work_area(2560, 1440), (0, 0, 2560, 1392))
        fake.work = (0, 0, 0, 0)                 # nonsense answer: fall back
        with mock.patch.object(K, "_win32", return_value=(fake, None)):
            self.assertEqual(K.work_area(2560, 1440), (0, 0, 2560, 1440 - K.TASKBAR))

    def test_covers(self):
        self.assertTrue(K.covers((0, 0, 100, 100), (0, 0, 100, 100)))
        self.assertTrue(K.covers((-8, -8, 108, 108), (0, 0, 100, 100)))
        self.assertFalse(K.covers((0, 0, 100, 99), (0, 0, 100, 100)))

    @unittest.skipUnless(sys.platform == "win32", "real Windows calls")
    def test_the_real_windows_calls_answer_with_the_right_types(self):
        self.assertIsInstance(K.idle_seconds(), float)
        self.assertGreaterEqual(K.idle_seconds(), 0.0)
        self.assertIsInstance(K.fullscreen_in_front(), bool)
        left, top, right, bottom = K.work_area(1, 1)
        self.assertTrue(right > left and bottom > top)


class SelfCheck(unittest.TestCase):
    def test_the_single_file_smoke_check_passes(self):
        K.smoke()                                # raises if anything is off

    @unittest.skipUnless(sys.platform == "win32", "C long is 4 bytes only on Windows")
    def test_rect_structs_match_windows(self):
        self.assertEqual(ctypes.sizeof(K._RECT), 16)
        self.assertEqual(ctypes.sizeof(K._MONITORINFO), 40)


# --------------------------------------------------------------------------- review fixes

class AwayIsABreak(Seeded):
    def test_time_away_from_the_desk_counts_as_your_break(self):
        p = working_pet()
        p.worked = K.PAUSE_EVERY - 60
        for i in range(1, 600):
            p.step(NOW + i, NOON, away=True)
        p.step(NOW + 600, NOON)
        self.assertLess(p.worked, 5, "a walk round the block is a break")
        self.assertIn(p.say, S["back"], "and she says hello")

    def test_a_blip_shorter_than_a_break_is_not_a_break(self):
        p = working_pet()
        p.worked = 1000.0
        with mock.patch.object(K, "AWAY_AFTER", 5):
            for i in range(1, 4):
                p.step(NOW + i, NOON, away=True)
            p.step(NOW + 4, NOON)
        self.assertGreaterEqual(p.worked, 1000.0)

    def test_coming_back_at_night_she_stays_quiet(self):
        p = working_pet()
        p.worked = 1000.0
        for i in range(1, 400):
            p.step(NOW + i, 23, away=True)
        p.say = ""
        p.step(NOW + 400, 23)
        self.assertLess(p.worked, 5)
        self.assertEqual(p.say, "")


class NightOwls(Seeded):
    def test_work_at_night_counts_and_still_gets_a_break(self):
        p = working_pet()
        p.worked = K.PAUSE_EVERY - 3
        states = [p.step(NOW + i, 23) for i in range(1, 6)]
        self.assertEqual(states[0], "sleep", "she dozes while you work")
        self.assertIn("pause", states, "but she still gets you up once an hour")

    def test_no_pep_talks_at_night(self):
        p = working_pet()
        p.next_line = NOW
        for i in range(1, 50):
            p.step(NOW + i, 2)
        self.assertEqual(p.say, "")

    def test_no_end_of_day_sign_at_night(self):
        app = K.Companion({"name": "M"}, FailingStore(), working_pet(), TODAY, NOW)
        app.pet.total = K.END_AFTER_WORK * 2
        app.slow(NOW, 23, TODAY, 0.0, False)
        self.assertNotEqual(app.pet.state, "pause")


class RememberingWork(AppTest):
    def restart(self, now, cfg=None):
        cfg = self.store.load() if cfg is None else cfg
        return K.Companion(cfg, self.store, working_pet(now), TODAY, now)

    def test_work_time_survives_a_restart_the_same_day(self):
        app = self.app()
        now = self.work(app, 1200)
        app.remember_work(now)
        again = self.restart(now + 5)
        self.assertAlmostEqual(again.pet.worked, 1200.0)
        self.assertAlmostEqual(again.worked_today(), 1200.0)

    def test_she_writes_it_down_every_so_often_on_her_own(self):
        app = self.app()
        now = self.work(app, 120)
        app.slow(now, NOON, TODAY, 0.0, False)
        self.assertAlmostEqual(self.store.load()["work"]["worked"], 120.0)

    def test_yesterdays_work_starts_fresh(self):
        cfg = {"name": "M", "work": {"date": "2026-10-12", "at": NOW, "worked": 900.0,
                                     "today": 5000.0}}
        again = self.restart(NOW + 5, cfg)
        self.assertEqual((again.pet.worked, again.worked_today()), (0.0, 0.0))

    def test_a_long_gap_between_runs_was_a_break_but_the_day_still_counts(self):
        cfg = {"name": "M", "work": {"date": TODAY, "at": NOW, "worked": 900.0,
                                     "today": 5000.0}}
        again = self.restart(NOW + K.AWAY_AFTER + 1, cfg)
        self.assertEqual(again.pet.worked, 0.0)
        self.assertAlmostEqual(again.worked_today(), 5000.0)

    def test_nonsense_on_disk_is_ignored(self):
        for work in ("lots", [], {"date": TODAY, "at": NOW, "worked": "a", "today": None},
                     {"date": TODAY, "at": NOW, "worked": -5, "today": -1}):
            again = self.restart(NOW + 1, {"name": "M", "work": work})
            self.assertEqual((again.pet.worked, again.worked_today()), (0.0, 0.0), work)


class SnoozeOnTheClock(AppTest):
    def test_break_in_ten_minutes_is_ten_minutes_on_the_clock(self):
        app = self.app()
        app.pet.start_pause(NOW)
        app.snooze(NOW + 1)
        app.pet.last_step = NOW + 1
        t = NOW + 1
        while t + 5 < NOW + 1 + K.SNOOZE:     # a frame every 5 s, so worked crawls
            t += 5
            self.assertNotEqual(app.pet.step(t, NOON), "pause")
        self.assertEqual(app.pet.step(NOW + 1 + K.SNOOZE, NOON), "pause")

    def test_snoozing_a_break_that_is_nearly_due(self):
        app = self.app()
        app.pet.worked = K.PAUSE_EVERY - 30
        app.snooze(NOW)
        self.assertNotEqual(app.pet.step(NOW + K.SNOOZE - 1, NOON), "pause")
        self.assertEqual(app.pet.step(NOW + K.SNOOZE, NOON), "pause")

    def test_skip_cancels_a_snoozed_break(self):
        app = self.app()
        app.pet.start_pause(NOW)
        app.snooze(NOW + 1)
        app.skip(NOW + 2)
        self.assertNotEqual(app.pet.step(NOW + 2 + K.SNOOZE, NOON), "pause")

    def test_the_words_follow_snooze(self):
        self.assertNotIn("10", S["menu_snooze"])
        self.assertNotIn("deset", S["snoozed"])
        for secs, want in ((600, "10 minut"), (300, "5 minut"), (120, "2 minuty"),
                           (60, "1 minutu")):
            with mock.patch.object(K, "SNOOZE", secs):
                self.assertIn(want, K.snooze_label())
                app = self.app()
                app.snooze(NOW)
                self.assertIn(want, app.pet.say)


class SingleInstance(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / "kocka.lock"

    def tearDown(self):
        self.folder.cleanup()

    def test_a_second_copy_is_turned_away_until_the_first_one_leaves(self):
        first = K.FileLock(self.path)
        self.assertTrue(first.acquire())
        self.assertFalse(K.FileLock(self.path).acquire())
        first.release()
        self.assertFalse(self.path.exists())
        self.assertTrue(K.FileLock(self.path).acquire())

    def test_a_lock_left_by_a_crashed_copy_is_taken_over(self):
        self.path.write_text("999999", encoding="utf-8")
        with mock.patch.object(K, "pid_alive", return_value=False):
            self.assertTrue(K.FileLock(self.path).acquire())
        self.assertEqual(self.path.read_text(encoding="utf-8"), str(K.os.getpid()))
        self.path.write_text("not a pid", encoding="utf-8")
        self.assertTrue(K.FileLock(self.path).acquire())

    def test_she_knows_she_is_alive(self):
        self.assertTrue(K.pid_alive(K.os.getpid()))
        self.assertFalse(K.pid_alive(0))

    @unittest.skipUnless(sys.platform == "win32", "named mutex is Windows only")
    def test_windows_uses_a_named_mutex(self):
        first = K.single_instance(self.path)
        self.assertIsNotNone(first)
        self.assertIsNone(K.single_instance(self.path))
        first.release()
        again = K.single_instance(self.path)
        self.assertIsNotNone(again)
        again.release()

    def test_two_writers_never_share_a_temp_file(self):
        store = K.Store(Path(self.folder.name) / "kocka.json", legacy=None)
        used = []
        real = K.os.replace

        def spy(src, dst):
            used.append(Path(src).name)
            return real(src, dst)

        with mock.patch.object(K.os, "replace", side_effect=spy):
            store.save({"name": "a"})
            store.save({"name": "b"})
        self.assertEqual(len(set(used)), 2, used)
        self.assertNotIn("kocka.json.tmp", used)


class Tidying(AppTest):
    def test_dpi_is_only_reported_when_windows_said_yes(self):
        def fake(per_monitor, system):
            w = mock.Mock()
            w.shcore.SetProcessDpiAwareness.return_value = per_monitor
            w.user32.SetProcessDPIAware.return_value = system
            return w

        for per_monitor, system, want in ((0, 1, "per-monitor"), (-2147024891, 1, "system"),
                                          (-2147024891, 0, "none")):
            with mock.patch.object(K.ctypes, "windll", fake(per_monitor, system), create=True):
                self.assertEqual(K.set_dpi_awareness(), want)

    def test_a_corrupt_file_never_overwrites_a_good_backup(self):
        self.store.save({"name": "Micka"})
        self.store.save({"name": "Mourek"})
        self.store.path.write_text("{ half writ", encoding="utf-8")
        cfg = self.store.load()
        self.assertTrue(self.store.save(cfg))
        self.assertEqual(K._read_json(self.store.backup), {"name": "Micka"})
        self.assertEqual(self.store.load(), {"name": "Micka"})

    def test_the_work_area_is_given_once(self):
        app = K.Companion({"name": "M"}, self.store, working_pet(), TODAY, NOW,
                          area=(0, 0, 1280, 760))
        self.assertEqual(app.area, (0, 0, 1280, 760))


class IdleEverywhere(unittest.TestCase):
    def setUp(self):
        K._IDLE_CACHE.update(at=-1e18, value=0.0)

    def run_gives(self, out, code=0):
        return mock.Mock(return_value=mock.Mock(stdout=out, returncode=code))

    def test_macos_reads_hid_idle_time(self):
        run = self.run_gives('  |   "HIDIdleTime" = 12500000000\n')
        self.assertEqual(K.idle_seconds("darwin", run=run), 12.5)
        self.assertEqual(run.call_args[0][0][0], "ioreg")
        self.assertIn("timeout", run.call_args[1])

    def test_linux_x11_uses_xprintidle_when_it_is_there(self):
        run = self.run_gives("4200\n")
        self.assertEqual(K.idle_seconds("linux", run=run, which=lambda n: "/usr/bin/" + n),
                         4.2)
        K._IDLE_CACHE.update(at=-1e18, value=0.0)
        self.assertEqual(K.idle_seconds("linux", run=run, which=lambda n: None), 0.0,
                         "no xprintidle: she can't tell, so she assumes you are there")

    def test_anything_odd_means_zero_not_a_crash(self):
        import subprocess
        for run in (self.run_gives("nonsense"), self.run_gives("", code=1),
                    mock.Mock(side_effect=OSError),
                    mock.Mock(side_effect=subprocess.TimeoutExpired("x", 2))):
            K._IDLE_CACHE.update(at=-1e18, value=0.0)
            self.assertEqual(K.idle_seconds("darwin", run=run), 0.0)

    def test_she_asks_the_os_only_every_few_seconds(self):
        run = self.run_gives('"HIDIdleTime" = 1000000000')
        clock = iter([100.0, 101.0, 100.0 + K.IDLE_EVERY])
        for _ in range(3):
            K.idle_seconds("darwin", run=run, clock=lambda: next(clock))
        self.assertEqual(run.call_count, 2)


class FocusQuestion(unittest.TestCase):
    """The morning question must not freeze her: it answers through a callback."""

    @classmethod
    def setUpClass(cls):
        try:
            import tkinter as tk
            cls.root = tk.Tk()
        except Exception as e:  # ImportError without Tk, TclError without a display
            raise unittest.SkipTest("no Tk display: %s" % e) from e
        cls.root.withdraw()
        cls.tk = tk

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def widgets(self, win, kind):
        found, todo = [], list(win.winfo_children())
        while todo:
            w = todo.pop()
            found.append(w)
            todo.extend(w.winfo_children())
        return next(w for w in found if isinstance(w, kind))

    def test_asking_returns_at_once_and_answers_later(self):
        got = []
        win = K.ask_focus(self.root, got.append)
        self.assertEqual(got, [], "nothing answered yet, and nothing blocked")
        self.widgets(win, self.tk.Entry).insert(0, "daně")
        self.widgets(win, self.tk.Button).invoke()
        self.assertEqual(got, ["daně"])
        self.assertFalse(win.winfo_exists())

    def test_closing_the_question_is_an_empty_answer(self):
        got = []
        win = K.ask_focus(self.root, got.append)
        self.root.tk.eval(win.protocol("WM_DELETE_WINDOW"))
        self.assertEqual(got, [None])
        self.assertFalse(win.winfo_exists())


# --------------------------------------------------------------------------- drawing

class Drawing(unittest.TestCase):
    """Every pose actually draws the right things, in and out of the cart, facing both
    ways. Needs a display; skipped where Tk cannot open one (CI on Linux uses Xvfb)."""

    @classmethod
    def setUpClass(cls):
        try:
            import tkinter as tk
            cls.root = tk.Tk()
        except Exception as e:  # ImportError without Tk, TclError without a display
            raise unittest.SkipTest("no Tk display: %s" % e) from e
        cls.root.withdraw()
        cls.tk = tk

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def canvas(self, k=1.0, extra=0):
        return self.tk.Canvas(self.root, width=int(K.W * k), height=int((K.H + extra) * k))

    def test_every_pose_draws_what_it_should(self):
        c = self.canvas()
        states = sorted(set(K.TRICKS) | {"sleep", "away", "pause"})
        furs = list(K.PALETTES)
        for n, state in enumerate(states):
            for cart in (True, False):
                for direction in (1, -1):
                    p = K.Pet(1000)
                    p.state, p.cart, p.dir, p.progress = state, cart, direction, 0.8
                    p.fur = furs[n % len(furs)]
                    p.say = "mrrr" if direction > 0 else ""
                    K.draw(c, p, 30)
                    why = (state, cart, direction)
                    has = {tag: bool(c.find_withtag(tag)) for tag in
                           ("wheel", "bowl", "paw", "zzz", "bubble", "head", "grass",
                            "hairball", "eyes_shut", "eyes_open", "mouth", "tongue")}
                    self.assertEqual(has["wheel"], cart, why)
                    self.assertEqual(has["bubble"], direction > 0, why)
                    fills = {c.itemcget(i, "fill") for i in c.find_all()
                             if c.type(i) != "text"}
                    self.assertIn(K.PALETTES[p.fur][0], fills, why)
                    if state == "butt":
                        self.assertFalse(has["head"], "she has turned her back")
                        continue
                    napping = state in ("sleep", "away", "rest")
                    self.assertTrue(has["head"], why)
                    self.assertEqual(has["bowl"], state == "milk", why)
                    self.assertEqual(has["grass"], state == "grass", why)
                    self.assertEqual(has["hairball"], state == "hairball", why)
                    self.assertEqual(has["paw"], state in ("highfive", "pause"), why)
                    self.assertEqual(len(c.find_withtag("zzz")), 3 if napping else 0, why)
                    self.assertEqual(has["eyes_shut"], napping or state == "lick", why)
                    self.assertEqual(has["eyes_open"], not has["eyes_shut"], why)
                    self.assertEqual(has["mouth"], state in ("meow", "hairball"), why)
                    self.assertEqual(has["tongue"], state in ("lick", "milk", "grass"), why)

    def test_no_text_straight_on_the_see_through_background(self):
        # antialiased text on the magenta colour key leaves pink fringes; text only ever
        # sits on her white bubble or her sign
        c = self.canvas()
        for state in ("sleep", "away", "rest", "idle", "pause"):
            for k in (1.0, 1.5):
                p = working_pet()
                p.state, p.say = state, "mrrr"
                K.draw(c, p, 30, k)
                loose = [c.itemcget(i, "text") for i in c.find_all() if c.type(i) == "text"
                         and not set(c.gettags(i)) & {"bubble", "sign"}]
                self.assertEqual(loose, [], (state, k))

    def test_the_bowl_is_drawn_where_a_click_finds_it(self):
        c = self.canvas()
        for direction in (1, -1):
            p = K.Pet(1000)
            p.state, p.dir = "milk", direction
            K.draw(c, p, 30)
            x1, y1, x2, y2 = c.bbox("bowl")
            bx1, by1, bx2, by2 = K.bowl_box(direction)
            for got, want in ((x1, bx1), (y1, by1), (x2, bx2), (y2, by2)):
                self.assertAlmostEqual(got, want, delta=3)

    def test_two_cats_two_coats_no_shared_paint(self):
        c = self.canvas()
        grey, black = K.Pet(1000), K.Pet(1000)
        grey.fur, black.fur = "seda", "cerna"
        K.draw(c, grey, 30)
        K.draw(c, black, 30)
        fills = {c.itemcget(i, "fill") for i in c.find_all()}
        self.assertIn(K.PALETTES["cerna"][0], fills)
        self.assertNotIn(K.PALETTES["seda"][0], fills)

    def test_the_bubble_wraps_its_text_at_any_zoom(self):
        for k in (1.0, 1.5, 2.0):
            c = self.canvas(k)
            p = K.Pet(1000)
            p.say = S["lines"][0]
            K.draw(c, p, 30, k)
            text = next(i for i in c.find_withtag("bubble") if c.type(i) == "text")
            box = next(i for i in c.find_withtag("bubble") if c.type(i) == "rectangle")
            tx1, ty1, tx2, ty2 = c.bbox(text)
            bx1, by1, bx2, by2 = c.coords(box)
            self.assertTrue(bx1 < tx1 and by1 < ty1 and tx2 < bx2 and ty2 < by2, k)
            self.assertLessEqual(bx2 - bx1, K.W * k, k)

    def test_break_sign_at_full_zoom(self):
        for kind, title in (("break", S["sign_break"][0]), ("end", S["sign_end"][0])):
            p = working_pet()
            p.start_pause(NOW, kind)
            p.step(NOW + 9, NOON)
            k = p.zoom(NOW + 9)
            c = self.canvas(k, K.PAUSE_EXTRA)
            K.draw(c, p, 30, k)
            K.draw_sign(c, int(K.W * k), k, p, NOW + 9)
            texts = [c.itemcget(i, "text") for i in c.find_withtag("sign")
                     if c.type(i) == "text"]
            self.assertEqual(texts[0], title)
            self.assertIn(p.coach_line(NOW + 9), texts)
            self.assertIn(S["sign_count"] % (p.pause_left(NOW + 9), p.breath_word), texts)


if __name__ == "__main__":
    unittest.main()
