import unittest

import teamtasks as tt


class TeamTasksTests(unittest.TestCase):
    def setUp(self):
        self.tasks = []
        tt.seed_demo(self.tasks)

    def test_add_assigns_next_id(self):
        task = tt.add_task(self.tasks, "New work", "Ali")
        self.assertEqual(task["id"], 6)

    def test_add_rejects_empty_title(self):
        with self.assertRaises(ValueError):
            tt.add_task(self.tasks, "   ")

    def test_add_rejects_bad_priority(self):
        with self.assertRaises(ValueError):
            tt.add_task(self.tasks, "Work", priority="urgent")

    def test_complete_unknown_id(self):
        with self.assertRaises(KeyError):
            tt.complete_task(self.tasks, 99)

    def test_filter_sorts_by_priority_and_hides_done(self):
        titles = [t["title"] for t in tt.filter_tasks(self.tasks)]
        self.assertEqual(titles, ["Build login endpoint", "Write API tests",
                                  "Review pull requests"])

    def test_filter_by_owner_is_case_insensitive(self):
        self.assertEqual(len(tt.filter_tasks(self.tasks, owner="sara")), 2)

    def test_summary_counts(self):
        stats = tt.summarize(self.tasks)
        self.assertEqual(stats["Ali"], {"open": 1, "done": 1})
        self.assertEqual(stats["Omar"], {"open": 0, "done": 1})


if __name__ == "__main__":
    unittest.main()
