"""An easy to use printer for use within iterations."""

import re
import typing

PATTERN_REGEX: str = r"\{([^{}]*)\}"
"""The pattern used to identify pattern substitutions in messages."""


class Iterwriter(object):
    def __init__(self, *args: str, sep: str = " ‖ ", **kwargs: str):
        """An object that prints results repeatedly, while maintaining alignment for changing values.

        The Iterwriter was created to de-clutter messy output strings created
        during iterative processes, such as model fitting.

        Args:
            sep: Placed between message elements. Usually a single character with a space on either side;
                characters that encourage vertical alignment (such as the default) make for prettier
                output.
            *args: Kept for future, but currently returns an error.
            **kwargs: Named messages. Each message should contain a single element to be substituted; see examples.

        Raises:
            NotImplementedError: When either unnamed arguments are given, or when given messages are too complex.

        """

        # validate inputs
        if len(args) > 0:
            raise NotImplementedError("Unnamed arguments not yet handled.")

        # separator will be placed in between strings
        self.sep: str = sep

        # convert inputs to internal storage and keep ready
        self.names: typing.List[str] = list(kwargs.keys())
        self.messages: typing.Dict[str, str] = {}
        self.bases: typing.Dict[str, str] = {}
        self.pad_lengths: typing.Dict[str, int] = {}
        self.decimals: typing.Dict[str, int] = {}

        # for name, template in kwargs.items():
        for name, message in kwargs.items():
            self.add_message(name, message)

    @staticmethod
    def validate_message(message: str) -> True:
        """Check that the provided string is a valid message format.

        Args:
            message: The full message to check.

        Returns:
            Returns ``True`` if the message will be parsed correctly, and raises an error otherwise.

        Raises:
             ValueError: If the given message will not be parsed properly.
             NotImplementedError: If the message will not be parsed properly, but the ability could be
                added. In this case, please raise an issue on our GitHub!

        """
        # message must be a string (easy)
        if not isinstance(message, str):
            raise ValueError(f"Given message should be a string, got {message} instead.")

        # pattern must exist
        patterns = re.findall(PATTERN_REGEX, message)
        if len(patterns) < 1:
            raise ValueError(f"Could not find a pattern in message {message}.")
        if len(patterns) > 1:
            raise NotImplementedError(
                "Found multiple patterns in {}, not yet handled. (patterns: {}).".format(message, ", ".join(patterns))
            )

        # pattern must be valid
        base, pad_length, decimals = Iterwriter.decompose_pattern(patterns[0])
        if base not in {"d", "f"}:
            raise NotImplementedError(f"Pattern type {base} not implemented yet; use another type or raise an issue.")
        if decimals is not None and base != "f":
            raise ValueError(f"Decimal specification provided to non-decimal argument.")

        # all tests passed!
        return True

    @staticmethod
    def decompose_pattern(pattern: str) -> typing.Tuple[str, typing.Optional[int], typing.Optional[int]]:
        """Extract the component elements from a given element pattern.

        This is essentially the reverse of the ``compose_pattern`` method.

        Args:
            pattern: The pattern from within the curly braces ("message {pattern}").

        Returns:
            A tuple of the ``(base, pad_length, decimal)`` values. The base is the
                flag indicating the value type, the pad length is the user-given
                minimum size for the value, and the decimal is the decimal accuracy
                desired.

        """
        # get base, maximum length and decimals using standard patterns
        base = pattern[-1]
        pad_length_all = re.findall(r":([0-9]+)", pattern)
        decimal_all = re.findall(r"\.([0-9]+)", pattern)

        # extract optional arguments if present
        pad_length = int(pad_length_all[0]) if len(pad_length_all) > 0 else None
        decimal = int(decimal_all[0]) if len(decimal_all) > 0 else None

        # no checking for validity in basic decomposition
        return base, pad_length, decimal

    @staticmethod
    def compose_pattern(
        base: typing.Optional[str] = None, pad_length: typing.Optional[int] = None, decimal: typing.Optional[int] = None
    ) -> str:
        """Combines the given elements back into a single pattern.

        This is essentially the reverse of the ``decompose_pattern`` method.

        Args:
            base: A single-character string indicating the type of the value, as passed to
                ``str.format``.
            pad_length: The length to pad the value to.
            decimal: The number of decimals to include in the output.

        Returns:
            A string with the composed pattern.

        """
        if base is None:
            base = ""
        if pad_length is None:
            pad_length = ""
        if decimal is None:
            pattern = "{{:{}{}}}".format(pad_length, base)
        else:
            pattern = "{{:{}.{}{}}}".format(pad_length, decimal, base)

        return pattern

    def add_message(self, name: str, message: str) -> None:
        """Stores a new name, message pair in the Iterwriter.

        Args:
            name: The name given to the message.
            message: The message (including the pattern).

        """
        self.validate_message(message)
        if name not in self.names:
            self.names.append(name)

        # separate the pattern and the message from the given format
        patterns = re.findall(PATTERN_REGEX, message)
        message = re.sub(PATTERN_REGEX, "{}", message)

        # extract information from input pattern
        base, pad_length, decimal = self.decompose_pattern(patterns[0])

        # store element as decomposed pieces
        self.messages[name] = message
        self.bases[name] = base
        self.pad_lengths[name] = 0 if pad_length is None else pad_length
        self.decimals[name] = decimal

    def format(self, **kwargs: typing.Any) -> str:
        """Create a string with the updated values.

        Args:
            **kwargs: New message values with given names.

        Returns:
            An adaptively-aligned output string, helpful for printing during iterative procedures.

        Raises:
            ValueError: An error is raised if some of the original messages are missed.

        """
        # stores the elements with updated values
        composed_elements = {}

        for name, value in kwargs.items():
            # compose the pattern to find the current length
            pattern = self.compose_pattern(
                base=self.bases[name], pad_length=self.pad_lengths[name], decimal=self.decimals[name]
            )
            composed_len = len(pattern.format(value))

            # update stored length if required, and recompose pattern
            if composed_len > self.pad_lengths[name]:
                self.pad_lengths[name] = max(self.pad_lengths[name], composed_len)
                pattern = self.compose_pattern(
                    base=self.bases[name], pad_length=self.pad_lengths[name], decimal=self.decimals[name]
                )

            # compose all patterns with values
            composed_elements[name] = pattern.format(value)

        # check that all messages were given
        if any(name not in composed_elements for name in self.names):
            missing_names = set(self.names) - set(composed_elements.keys())
            raise ValueError("Missing messages for names: {}.".format(" ".join(missing_names)))

        # make sure that order is preserved when returning
        messages = {name: self.messages[name].format(composed_elements[name]) for name in self.names}
        return self.sep.join(messages[name] for name in self.names)
