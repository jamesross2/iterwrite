"""Check that Iterwriter under usual conditions and edge cases."""

import pytest

import iterwrite


def test_message_validation() -> None:
    """Check that bad messages are rejected, and good messages are accepted by validator."""
    # floats can optionally specify padding or decimals only
    assert iterwrite.Iterwriter.validate_message("A valid message + pattern {:5.2f}")
    assert iterwrite.Iterwriter.validate_message("{:0.0f} is also valid")
    assert iterwrite.Iterwriter.validate_message("{:7f}")
    assert iterwrite.Iterwriter.validate_message("{:f}")
    assert iterwrite.Iterwriter.validate_message("{:.3f}")

    # integers can optionally specify padding only
    assert iterwrite.Iterwriter.validate_message("A valid message {:5d}")
    assert iterwrite.Iterwriter.validate_message("{:0d} is also valid")
    assert iterwrite.Iterwriter.validate_message("{:d}")

    # non-strings are invalid
    for bad_types in [25, (5,), lambda: 0]:
        with pytest.raises(ValueError, match="should be a string"):
            iterwrite.Iterwriter.validate_message(bad_types)

    # decimals on integers are invalid
    with pytest.raises(ValueError, match="Decimal specification"):
        iterwrite.Iterwriter.validate_message("{:5.5d}")

    # other types are invalid
    for type_char in ("s", "e", "F", "D", "whoops"):
        pattern = "{{:{}}}".format(type_char)
        with pytest.raises(NotImplementedError, match="type .* not implemented"):
            iterwrite.Iterwriter.validate_message(pattern)

    # only a single pattern is permitted
    with pytest.raises(ValueError, match="Could not find a pattern"):
        iterwrite.Iterwriter.validate_message("I forgot a pattern.")
    with pytest.raises(NotImplementedError, match="Found multiple patterns"):
        iterwrite.Iterwriter.validate_message("Two patterns {:5.2f} {:6.3f}")


def test_decompose_pattern() -> None:
    """Check that valid patterns are decomposed well."""
    # decimals
    assert iterwrite.Iterwriter.decompose_pattern(":0.0f") == ("f", 0, 0)
    assert iterwrite.Iterwriter.decompose_pattern(":7f") == ("f", 7, None)
    assert iterwrite.Iterwriter.decompose_pattern(":f") == ("f", None, None)
    assert iterwrite.Iterwriter.decompose_pattern(":.3f") == ("f", None, 3)

    # ints
    assert iterwrite.Iterwriter.decompose_pattern(":5d") == ("d", 5, None)
    assert iterwrite.Iterwriter.decompose_pattern(":0d") == ("d", 0, None)
    assert iterwrite.Iterwriter.decompose_pattern(":d") == ("d", None, None)


def test_compose_pattern() -> None:
    """Check that pattern elements are composed properly."""
    # ambiguous
    assert iterwrite.Iterwriter.compose_pattern(None, 0, 0) == "{:0.0}"
    assert iterwrite.Iterwriter.compose_pattern(None, 7, None) == "{:7}"
    assert iterwrite.Iterwriter.compose_pattern(None, None, None) == "{:}"
    assert iterwrite.Iterwriter.compose_pattern(None, None, 3) == "{:.3}"

    # decimals
    assert iterwrite.Iterwriter.compose_pattern("f", 0, 0) == "{:0.0f}"
    assert iterwrite.Iterwriter.compose_pattern("f", 7, None) == "{:7f}"
    assert iterwrite.Iterwriter.compose_pattern("f", None, None) == "{:f}"
    assert iterwrite.Iterwriter.compose_pattern("f", None, 3) == "{:.3f}"

    # ints
    assert iterwrite.Iterwriter.compose_pattern("d", 5, None) == "{:5d}"
    assert iterwrite.Iterwriter.compose_pattern("d", 0, None) == "{:0d}"
    assert iterwrite.Iterwriter.compose_pattern("d", None, None) == "{:d}"


def test_initialisation() -> None:
    """Check that Iterwriter object is created well."""
    # object created safely
    writer = iterwrite.Iterwriter(count="count: {:4d}", delta="value += {:.2f}")
    assert isinstance(writer, iterwrite.Iterwriter)

    # internal properties correct
    assert isinstance(writer.sep, str)
    assert writer.names == ["count", "delta"]
    assert writer.messages == {"count": "count: {}", "delta": "value += {}"}
    assert writer.bases == {"count": "d", "delta": "f"}
    assert writer.pad_lengths == {"count": 4, "delta": 0}
    assert writer.decimals == {"count": None, "delta": 2}

    # empty iterwriter initialised safely
    writer = iterwrite.Iterwriter()
    assert isinstance(writer, iterwrite.Iterwriter)

    # sep value can be altered
    writer = iterwrite.Iterwriter(update="({:3d} / 100): ", val="{:6.3f}", sep="")
    assert writer.sep == ""

    # unnamed arguments fail :(
    with pytest.raises(NotImplementedError, match="Unnamed arguments not yet handled"):
        iterwrite.Iterwriter("({update:3d} / 100): ", "{val:6.3f}", sep="")


def test_add() -> None:
    """Check that new values can be added to a writer easily."""
    writer = iterwrite.Iterwriter(count="count: {:4d}", delta="value += {:.2f}")
    writer.add_message("best", "(best: {6.2f})")
    assert writer.names == ["count", "delta", "best"]
    for attributes in (writer.messages, writer.bases, writer.pad_lengths, writer.decimals):
        assert "best" in attributes


def test_separator() -> None:
    writer = iterwrite.Iterwriter(count="count: {:4d}", delta="value += {:.2f}")
    message_def = writer.format(count=100, delta=0.05)
    writer.sep = ",  "
    message_new = writer.format(count=100, delta=0.05)

    assert message_def == "count:  100 ‖ value += 0.05"
    assert message_new == "count:  100,  value += 0.05"


def test_writing() -> None:
    # the order of the tests matters, because writer remembers the length of jumbo
    writer = iterwrite.Iterwriter(sep="--", mumbo="long:{:10d}", jumbo="short:{:0d}")
    assert writer.format(mumbo=0, jumbo=0) == "long:         0--short:0"
    assert writer.format(mumbo=43210, jumbo=0) == "long:     43210--short:0"
    assert writer.format(mumbo=43210, jumbo=6543210) == "long:     43210--short:6543210"
    assert writer.format(mumbo=43210, jumbo=0) == "long:     43210--short:      0"

    # test that forgetting arguments mucks it all up
    with pytest.raises(ValueError, match="Missing messages"):
        writer.format(mumbo=500)
