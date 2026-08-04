"""Command line interface of the Fly-in simulator.

Declares one flag per shipped map plus a ``--graph`` switch, and turns
the raised flag back into the map path the parser has to read.
"""
import argparse


class FlagManager:
    """Declare, parse and read back the command line flags.

    Exactly one map flag may be raised per run. The map flags are not
    declared as a mutually exclusive group, so that rule is enforced
    afterwards by :meth:`_flag_check`.

    Attributes:
        args: Namespace filled by :meth:`init_args`, or None while the
            command line has not been parsed yet.
    """

    def __init__(self) -> None:
        """Create a manager holding no parsed arguments yet."""
        self.args: argparse.Namespace | None = None

    def init_args(self, arglist: list[str] | None) -> None:
        """Declare every flag and parse the command line.

        Each map flag takes an optional value: raised bare it falls
        back to the map it is named after, and given a value it uses
        that path instead, which allows running a custom map. Flags
        left down keep the string ``"None"`` so :meth:`_flag_check`
        can count them.

        Args:
            arglist: Arguments to parse. Pass None to read the real
                command line; a list is mainly useful for tests.
        """
        parser = argparse.ArgumentParser(
            prog="Fly in",
            description="Path finding for drones"
        )
        parser.add_argument(
            "--default_launch",
            nargs="?",
            type=str,
            default="None",
            const="maps/easy/01*",
        )
        parser.add_argument(
            "--launch_E1",
            nargs="?",
            type=str,
            default="None",
            const="maps/easy/01*",
        )
        parser.add_argument(
            "--launch_E2",
            nargs="?",
            type=str,
            default="None",
            const="maps/easy/02*",
        )
        parser.add_argument(
            "--launch_E3",
            nargs="?",
            type=str,
            default="None",
            const="maps/easy/03*",
        )
        parser.add_argument(
            "--launch_M1",
            nargs="?",
            type=str,
            default="None",
            const="maps/medium/01*",
        )
        parser.add_argument(
            "--launch_M2",
            nargs="?",
            type=str,
            default="None",
            const="maps/medium/02*",
        )
        parser.add_argument(
            "--launch_M3",
            nargs="?",
            type=str,
            default="None",
            const="maps/medium/03*",
        )
        parser.add_argument(
            "--launch_H1",
            nargs="?",
            type=str,
            default="None",
            const="maps/hard/01*",
        )
        parser.add_argument(
            "--launch_H2",
            nargs="?",
            type=str,
            default="None",
            const="maps/hard/02*",
        )
        parser.add_argument(
            "--launch_H3",
            nargs="?",
            type=str,
            default="None",
            const="maps/hard/03*",
        )
        parser.add_argument(
            "--launch_C1",
            nargs="?",
            type=str,
            default="None",
            const="maps/challenger/01*",
        )
        parser.add_argument(
            "--graph",
            nargs="?",
            default="not_graph",
            const="graphed"
        )

        if arglist is not None:
            args = parser.parse_args(arglist)
        else:
            args = parser.parse_args()
        self.args = args

    def _get_args_values(self) -> list[str]:
        """Flatten the parsed namespace into an ordered value list.

        The order is fixed: the eleven map flags first, then the
        ``--graph`` switch. :meth:`_flag_check` relies on that layout
        to count the flags left down.

        Returns:
            One entry per flag, ``"None"`` for a map flag left down,
            and ``"graphed"`` or ``"not_graph"`` for the last entry.
            An empty list if the command line was never parsed.
        """
        values: list[str] = []
        args = self.args

        if args is None:
            return values

        values.append(args.default_launch)
        values.append(args.launch_E1)
        values.append(args.launch_E2)
        values.append(args.launch_E3)
        values.append(args.launch_M1)
        values.append(args.launch_M2)
        values.append(args.launch_M3)
        values.append(args.launch_H1)
        values.append(args.launch_H2)
        values.append(args.launch_H3)
        values.append(args.launch_C1)
        values.append(args.graph)

        return values

    def _flag_check(self, values: list[str]) -> bool:
        """Ensure a single map flag was raised.

        Out of the twelve values, the ``--graph`` one is never
        ``"None"``, so ten flags left down means exactly one of the
        eleven map flags is up.

        Args:
            values: Flag values as returned by
                :meth:`_get_args_values`.

        Returns:
            True when exactly one map flag is up.

        Raises:
            ValueError: If no map flag or several of them were given.
        """
        none_count = values.count("None")

        if none_count != 10:
            raise ValueError("There is too much or no"
                             " flag up flag up should be one")
        return True

    def get_path_from_flag(self) -> str:
        """Return the map path selected on the command line.

        Returns:
            The glob pattern of the chosen map, taken either from the
            flag default or from the value the user passed to it.

        Raises:
            ValueError: If no map flag or several of them were given.
        """
        v = self._get_args_values()
        path = ""

        self._flag_check(v)
        new_v = [val for val in v if val != "None"]
        for val in new_v:
            if val != "graphed" and val != "not_graph":
                path = val
        return path

    def is_graphed(self) -> bool:
        """Tell whether the run asked for the graphical display.

        Returns:
            True if ``--graph`` was raised, False if the simulation
            should only print its turns to the terminal.

        Raises:
            ValueError: If no map flag or several of them were given.
        """
        v = self._get_args_values()

        self._flag_check(v)
        new_v = [val for val in v if val == "graphed"]
        if len(new_v) == 1:
            return True
        return False
