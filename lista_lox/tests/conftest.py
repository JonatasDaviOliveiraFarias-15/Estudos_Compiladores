import importlib
from pdb import run
import sys
import re
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import pytest

LINE_PATTERN = re.compile(r"^\[line (\d+)\] ")

class NotSupported(Exception):
    """Indicate that a feature is not supported."""

@pytest.fixture
def check():
    return check_program


def check_program(section: str, name: str, /):
    base = Path(__file__).parent.parent / "examples"
    if section:
        path = base / section / f"{name}.lox"
    else:
        path = base / f"{name}.lox"
    source = path.read_text(encoding="utf-8")

    print(f"Testing program: {path.relative_to(base)}\n")
    print(ident(source, "  "))
    print()

    expected = parse_expects(source)
    print("Expected output:\n")
    print(ident(expected, "  "))
    print()

    output, err = run_program(source)

    print("Actual output:\n")
    print(ident(output, "  "))
    print()

    if err is not None:
        raise err
    else:
        compare_output(output, expected)

def parse_expects(src: str) -> str:
    lines = []
    for line in src.splitlines():
        line = line.strip()
        _, sep, comment = line.partition("//")
        if not sep:
            continue
        comment = comment.lstrip()
        if comment.startswith(prefix := "expect:"):
            message = comment.removeprefix(prefix).strip()
            lines.append(message)
        elif comment.startswith(prefix := "expect "):
            message = comment.removeprefix(prefix).strip()
            lines.append(message)
        elif comment.startswith("Error at"):
            lines.append(comment)
        elif comment.startswith("[c"):
            continue
        elif comment.startswith(prefix := "[java"):
            lines.append("[" + comment.removeprefix("[java").lstrip())
        elif comment.startswith("["):
            lines.append(comment)
    return "\n".join(lines)

def compare_output(stdout: str, expected_stdout: str):
    output = stdout.rstrip().splitlines()
    expected = expected_stdout.rstrip().splitlines()
    if output == expected:
        return
    while output and expected:
        if is_compatible_line(output[0], expected[0]):
            output.pop(0)
            expected.pop(0)
            continue
        elif is_compatible_line(output[-1], expected[-1]):
            output.pop()
            expected.pop()
            continue
        raise AssertionError(
            f"expected output line: {expected[0]!r}, got: {output[0]!r}"
        )

def is_compatible_line(actual: str, expected: str) -> bool:
    if actual == expected:
        return True
    elif expected.startswith("runtime error:"):
        prefix, sep, rest = actual.partition(":")
        if sep and "Runtime error" in prefix:
            expected = expected.removeprefix("runtime error:")
            actual = rest
    elif actual.startswith("[line ") and not expected.startswith("[line "):
        _, _, actual = actual.partition("] ")
    elif (m1 := LINE_PATTERN.match(actual)) and (m2 := LINE_PATTERN.match(expected)):
        if m1.group(0) == m2.group(0):
            actual = actual[m1.end() :]
            expected = expected[m2.end() :]
            return is_compatible_line(actual, expected)
    elif actual.startswith("Error at '") and expected.startswith("Error:"):
        actual = "Error:" + actual.partition("':")[2]
    return actual == expected

def is_error_line(text: str) -> bool:
    text = text.lstrip().casefold()
    return (
        text.startswith("[line ")
        or text.startswith("error")
        or text.startswith("runtime error")
    )

def ident(s: str, prefix: str) -> str:
    return "\n".join(prefix + line for line in s.splitlines())

def run_program(source: str) -> tuple[str, Exception | None]:
    for fn in [run_program_from_entrypoint, run_program_from_lox_class]:
        try:
            return fn(source)
        except NotSupported:
            continue
    raise NotSupported("No available method to run the program. Please define a runner function.")

def run_program_from_lox_class(source: str) -> tuple[str, Exception | None]:
    try:
        from lox.__main__ import Lox
    except ImportError:
        raise NotSupported("Lox class is not available in this implementation.")
    try:
        lox = Lox()
    except Exception as e:
        raise NotSupported("Lox cannot be initialized.")
    try:
        run_source = lox.run
    except AttributeError:
        raise NotSupported("Lox does not have a run method.")
    return from_runner(source, run_source)

def run_program_from_entrypoint(source: str, entrypoint: str = "lox:run_source") -> tuple[str, Exception | None]:
    [mod, func] = entrypoint.split(":")
    try:
        run_source = getattr(importlib.import_module(mod), func)
    except (ImportError, AttributeError):
        raise NotSupported(f"Entrypoint {entrypoint} is not available.")
    return from_runner(source, run_source)

def from_runner(source: str, runner: str) -> tuple[str, Exception | None]:
    err = None
    with redirect_stdout(StringIO()) as f:
        try:
            runner(source)
        except Exception as e:
            err = e
            print(f"Runtime error: {err}")
            err.with_traceback(err.__traceback__)
    return f.getvalue().rstrip(), err