#!/usr/bin/env python3
from __future__ import annotations

import json
import sys


def main() -> int:
    tasks_path = sys.argv[1] if len(sys.argv) > 1 else "input/tasks.json"
    results_path = sys.argv[2] if len(sys.argv) > 2 else "output/results.json"
    tasks = json.load(open(tasks_path, "r", encoding="utf-8"))
    results = json.load(open(results_path, "r", encoding="utf-8"))
    assert isinstance(tasks, list), "tasks must be a list"
    assert isinstance(results, list), "results must be a list"
    assert len(results) == len(tasks), f"Expected {len(tasks)} result(s), got {len(results)}"
    expected = {t["task_id"]: set(t.get("styles") or []) for t in tasks}
    for result in results:
        task_id = result.get("task_id")
        assert task_id in expected, f"Unexpected task_id: {task_id}"
        captions = result.get("captions")
        assert isinstance(captions, dict), f"Missing captions object for {task_id}"
        missing = expected[task_id] - set(captions)
        assert not missing, f"Missing styles for {task_id}: {sorted(missing)}"
        for style, caption in captions.items():
            assert isinstance(caption, str) and caption.strip(), f"Empty caption for {task_id}/{style}"
    print("PASS: results.json is valid and includes all requested captions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
