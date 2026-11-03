"""TeamTasks: a small command-line task tracker for teams.

Usage examples:
    python teamtasks.py demo
    python teamtasks.py add "Write API tests" --owner Sara --priority high
    python teamtasks.py list --owner Sara
    python teamtasks.py done 1
    python teamtasks.py summary
"""
import argparse
import json
import sys
from pathlib import Path

PRIORITIES = {"low": 1, "medium": 2, "high": 3}
DEFAULT_FILE = Path("tasks.json")


def load_tasks(path):
    """Return the list of tasks stored in path, or an empty list."""
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save_tasks(path, tasks):
    with path.open("w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)


def add_task(tasks, title, owner="Unassigned", priority="medium"):
    """Append a new task and return it. Raises ValueError on bad input."""
    if not title.strip():
        raise ValueError("Title must not be empty.")
    if priority not in PRIORITIES:
        raise ValueError(f"Priority must be one of: {', '.join(PRIORITIES)}.")
    next_id = max((t["id"] for t in tasks), default=0) + 1
    task = {"id": next_id, "title": title.strip(), "owner": owner,
            "priority": priority, "done": False}
    tasks.append(task)
    return task


def complete_task(tasks, task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            return task
    raise KeyError(f"No task with id {task_id}.")


def filter_tasks(tasks, owner=None, include_done=False):
    """Return tasks sorted by priority (high first), then id."""
    result = [t for t in tasks
              if (owner is None or t["owner"].lower() == owner.lower())
              and (include_done or not t["done"])]
    return sorted(result, key=lambda t: (-PRIORITIES[t["priority"]], t["id"]))


def summarize(tasks):
    """Return {owner: {"open": n, "done": n}} for every owner."""
    stats = {}
    for t in tasks:
        entry = stats.setdefault(t["owner"], {"open": 0, "done": 0})
        entry["done" if t["done"] else "open"] += 1
    return stats


def format_task(t):
    mark = "x" if t["done"] else " "
    return f"[{mark}] #{t['id']:<3} {t['priority']:<6} {t['owner']:<10} {t['title']}"


def seed_demo(tasks):
    """Fill tasks with sample data for a three-person team."""
    samples = [
        ("Design database schema", "Ali", "high"),
        ("Build login endpoint", "Sara", "high"),
        ("Write API tests", "Sara", "medium"),
        ("Draft user guide", "Omar", "low"),
        ("Review pull requests", "Ali", "medium"),
    ]
    for title, owner, priority in samples:
        add_task(tasks, title, owner, priority)
    complete_task(tasks, 1)
    complete_task(tasks, 4)


def build_parser():
    parser = argparse.ArgumentParser(prog="teamtasks", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE,
                        help="JSON file that stores the tasks (default: tasks.json)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="add a task")
    p_add.add_argument("title")
    p_add.add_argument("--owner", default="Unassigned")
    p_add.add_argument("--priority", default="medium", choices=PRIORITIES)

    p_list = sub.add_parser("list", help="list open tasks")
    p_list.add_argument("--owner")
    p_list.add_argument("--all", action="store_true", help="include finished tasks")

    p_done = sub.add_parser("done", help="mark a task as done")
    p_done.add_argument("id", type=int)

    sub.add_parser("summary", help="show open and done counts per person")
    sub.add_parser("demo", help="replace the task file with sample team data")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    tasks = [] if args.command == "demo" else load_tasks(args.file)
    try:
        if args.command == "add":
            print("Added:", format_task(add_task(tasks, args.title, args.owner, args.priority)))
        elif args.command == "list":
            for t in filter_tasks(tasks, args.owner, args.all):
                print(format_task(t))
        elif args.command == "done":
            print("Completed:", format_task(complete_task(tasks, args.id)))
        elif args.command == "summary":
            for owner, s in sorted(summarize(tasks).items()):
                print(f"{owner:<10} open: {s['open']}  done: {s['done']}")
        elif args.command == "demo":
            seed_demo(tasks)
            print(f"Demo data written to {args.file} ({len(tasks)} tasks).")
    except (ValueError, KeyError) as err:
        print("Error:", err.args[0], file=sys.stderr)
        return 1
    save_tasks(args.file, tasks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
