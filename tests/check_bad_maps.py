"""
    Test bench for the invalid maps in maps/easy/bad_*.txt

    Runs Parsing.parse_data() on every fixture and compares the reported
    line numbers with the expected ones (see maps/easy/BAD_MAPS.md).

    Usage : make check_bad_maps
            PYTHONPATH=. uv run python tests/check_bad_maps.py
            PYTHONPATH=. uv run python tests/check_bad_maps.py bad_19
"""
import contextlib
import io
import sys
from glob import glob

from utils import Parsing

Error = tuple[bool, int, str]

"""
    What every fixture is supposed to report : the 1-based line numbers
    and a reminder of the cause. An empty list means no error expected.
"""
EXPECTED: dict[str, tuple[list[int], str]] = {
    "bad_01": ([2], "first useful line must be nb_drones:"),
    "bad_02": ([2], "nb_drones must be an integer > 0"),
    "bad_03": ([], "no start_hub (expected : 1 error without a line)"),
    "bad_04": ([5], "two start_hub"),
    "bad_05": ([], "no end_hub (expected : 1 error without a line)"),
    "bad_06": ([6], "zone name middle already used on line 5"),
    "bad_07": ([6], "coord (1, 0) already used on line 5"),
    "bad_08": ([5], "coordinates are not integers"),
    "bad_09": ([6], "dash inside a zone name"),
    "bad_10": ([9], "zone nowhere never defined"),
    "bad_11": ([9], "duplicate connection middle-start == start-middle"),
    "bad_12": ([6], "zone=banana is invalid"),
    "bad_13": ([5], "max_drones=0 is not positive"),
    "bad_14": ([8], "max_link_capacity=-2 is not positive"),
    "bad_15": ([7, 8, 9], "unknown key / no = / block not at end of line"),
    "bad_16": ([6], "unknown key zone:"),
    "bad_17": ([7, 8], "no : at all / two : on the same line"),
    "bad_18": ([5], "start_hub must stay normal"),
    "bad_19": ([5, 6, 7, 8, 9, 10, 15, 16, 17], "cumulative - 9 errors"),
    "bad_20": ([], "control fixture : no error"),
}

"""
    Fixtures whose error cannot be pinned to a line (a missing hub).
    For those we only expect "at least one error", whatever the line.
"""
NO_LINE = {"bad_03", "bad_05"}


def run_map(path: str) -> tuple[list[Error] | None, str]:
    """
        Run the parsing while swallowing the debug print() of parse_data().
        Returns the list of errors, or None if the parsing raised.
    """
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            raw = Parsing(path).parse_data()
    except Exception as exc:
        return (None, "%s: %s" % (type(exc).__name__, exc))
    errors: list[Error] = []
    for tup in raw:
        if len(tup) < 3:
            errors.append((tup[0], tup[1], "<2 FIELDS TUPLE>"))
        else:
            errors.append((tup[0], tup[1], tup[2]))
    return (errors, "")


def verdict(key: str, expected: list[int], got: list[int]) -> tuple[bool, str]:
    """
        Compare the reported lines with the expected ones.
        Returns (ok, readable verdict).
    """
    if key in NO_LINE:
        if got:
            return (True, "OK (error reported)")
        return (False, "NOT DETECTED")
    if got == expected:
        return (True, "OK")
    if not got:
        return (False, "NOT DETECTED")
    hit = sorted(set(got) & set(expected))
    extra = sorted(set(got) - set(expected))
    missed = sorted(set(expected) - set(got))
    if not expected:
        return (False, "FALSE POSITIVE on %s" % (extra,))
    bits = []
    if hit:
        bits.append("%d/%d right" % (len(hit), len(expected)))
    if missed:
        bits.append("missing %s" % (missed,))
    if extra:
        bits.append("spurious %s" % (extra,))
    if len(got) != len(set(got)):
        bits.append("duplicates")
    return (False, ", ".join(bits))


def main(argv: list[str]) -> int:
    """
        Print the table and return the exit code (0 when everything passes).
    """
    only = set(argv[1:])
    paths = sorted(glob("maps/easy/bad_*.txt"))
    if not paths:
        print("no fixture found in maps/easy/bad_*.txt")
        return 2

    head = "%-8s | %-26s | %-26s | %s" % (
        "file", "expected", "reported", "verdict")
    print(head)
    print("-" * len(head))

    passed = 0
    total = 0
    details: list[tuple[str, list[Error]]] = []

    for path in paths:
        key = path.split("/")[-1][:6]
        if only and key not in only:
            continue
        total += 1
        expected, _cause = EXPECTED.get(key, ([], "?"))
        errors, crash = run_map(path)
        if errors is None:
            print("%-8s | %-26s | %-26s | CRASH %s" % (
                key, expected, "-", crash))
            continue
        got = sorted(err[1] for err in errors)
        ok, note = verdict(key, expected, got)
        passed += int(ok)
        print("%-8s | %-26s | %-26s | %s" % (
            key, expected if expected else "no line",
            got if got else "[]", note))
        if errors:
            details.append((key, errors))

    print("-" * len(head))
    print("Score : %d / %d" % (passed, total))

    print("\nReported causes")
    print("-" * len(head))
    for key, errors in details:
        for err in errors:
            print("%-8s | line %-5d | %s" % (key, err[1], err[2]))
        reminder = EXPECTED.get(key, ([], "?"))[1]
        print("%-8s | expected   | %s\n" % (key, reminder))

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
