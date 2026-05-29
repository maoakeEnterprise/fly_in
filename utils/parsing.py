import argparse


class Parsing:
    def __init__(self):
        self.args: argparse.Namespace | None = None

    def init_args(self) -> None:
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

        args = parser.parse_args()
        self.args = args
