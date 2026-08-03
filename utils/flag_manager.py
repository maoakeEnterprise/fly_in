import argparse


class FlagManager:
    def __init__(self) -> None:
        self.args: argparse.Namespace | None = None

    """
        define every flag one flag for each map 
        and default launch to a custom map
    """
    def init_args(self, arglist: list[str] | None) -> None:
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

    """
        get every flag
    """
    def _get_args_values(self) -> list[str]:
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

    """
        check if the flags are good
    """
    def _flag_check(self, values: list[str]) -> bool:
        none_count = values.count("None")

        if none_count != 10:
            raise ValueError("There is too much or no"
                             " flag up flag up should be one")
        return True

    """
        get the path from the flag
    """
    def get_path_from_flag(self) -> str:
        v = self._get_args_values()
        path = ""

        self._flag_check(v)
        new_v = [val for val in v if val != "None"]
        for val in new_v:
            if val != "graphed" and val != "not_graph":
                path = val
        return path

    def is_graphed(self) -> bool:
        v = self._get_args_values()

        self._flag_check(v)
        new_v = [val for val in v if val == "graphed"]
        if len(new_v) == 1:
            return True
        return False
