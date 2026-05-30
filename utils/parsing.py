import argparse


class FlagManager:
    def __init__(self):
        self.args: argparse.Namespace | None = None

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

        if arglist is not None:
            args = parser.parse_args(arglist)
        else:
            args = parser.parse_args()
        self.args = args

    def _get_args_values(self) -> list[str]:
        values: list[str] = []
        args = self.args

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

        return values

    def _flag_check(self, values: list[str]) -> bool:
        none_count = values.count("None")

        if none_count != 9:
            raise ValueError("There is too much or no"
                             " flag up flag up should be one")
        return True

    def get_flag_value(self) -> str:
        self
        v = self._get_args_values()
        self._flag_check(v)
        new_v = [val for val in v if val != "None"]
        return new_v[0]
