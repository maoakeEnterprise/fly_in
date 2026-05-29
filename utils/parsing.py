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
            type=str,
            required=False,
            default="maps/easy/01*",
        )
        parser.add_argument(
            "--launch_E1",
            type=str,
            required=False,
            default="maps/easy/01*",
        )
        parser.add_argument(
            "--launch_E2",
            type=str,
            required=False,
            default="maps/easy/02*",
        )
        parser.add_argument(
            "--launch_E3",
            type=str,
            required=False,
            default="maps/easy/03*",
        )
        parser.add_argument(
            "--launch_M1",
            type=str,
            required=False,
            default="maps/medium/01*",
        )
        parser.add_argument(
            "--launch_M2",
            type=str,
            required=False,
            default="maps/medium/02*",
        )
        parser.add_argument(
            "--launch_M3",
            type=str,
            required=False,
            default="maps/medium/03*",
        )

        args = parser.parse_args()
        self.args = args
