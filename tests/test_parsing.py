from utils import Parsing, HubName


class TestParsing:

    def test_ignore_hashtag(self) -> None:
        line = "# qsdqdqsdqsd"
        parsing = Parsing("path")
        assert parsing._ignore_hashtag(line) is True

    def test_ignore_hashtag_1(self) -> None:
        line = " \t\t\n# qsdqdqsdqsd"
        parsing = Parsing("path")
        assert parsing._ignore_hashtag(line) is True

    def test_ignore_hashtag_2(self) -> None:
        line = " ca# qsdqdqsdqsd"
        parsing = Parsing("path")
        assert parsing._ignore_hashtag(line) is False

    def test_skip_line(self) -> None:
        line = "         "
        parsing = Parsing("titi")
        assert parsing._skip_line(line) is True

    def test_skip_line1(self) -> None:
        line = "      caca   "
        parsing = Parsing("titi")
        assert parsing._skip_line(line) is False

    def test_first_line(self) -> None:
        line = "nb_drones: 23"
        parsing = Parsing("titi")
        assert parsing._first_line(line, 0) is True

    def test_first_line1(self) -> None:
        line = "nb_drones: 23"
        parsing = Parsing("titi")
        assert parsing._first_line(line, 2) is False

    def test_first_line2(self) -> None:
        line = "nb_drones: zi"
        parsing = Parsing("titi")
        assert parsing._first_line(line, 0) is False

    def test_unique_hub(self) -> None:
        parsing = Parsing("titi")
        maze_config = [
            "# Easy Level 1: Simple linear path",
            "nb_drones: 2",
            "start_hub: start 0 0 [color=green]",
            "hub: waypoint1 1 0 [color=blue]",
            "hub: waypoint2 2 0 [color=blue]",
            "end_hub: goal 3 0 [color=red]",
            "connection: start-waypoint1",
            "connection: waypoint1-waypoint2",
            "connection: waypoint2-goal"
        ]
        assert parsing._unique_hub(maze_config,
                                   HubName.START_HUB.value)[0] is True

    def test_unique_hub1(self) -> None:
        parsing = Parsing("titi")
        maze_config = [
            "# Easy Level 1: Simple linear path",
            "nb_drones: 2",
            "start_hub: start 0 0 [color=green]",
            "hub: waypoint1 1 0 [color=blue]",
            "hub: waypoint2 2 0 [color=blue]",
            "end_hub: goal 3 0 [color=red]",
            "start_hub: start 0 0 [color=green]",
            "connection: start-waypoint1",
            "connection: waypoint1-waypoint2",
            "connection: waypoint2-goal"
        ]
        assert parsing._unique_hub(maze_config,
                                   HubName.START_HUB.value)[0] is False

    def test_len_split_data(self) -> None:
        parsing = Parsing("titi")
        maze_config = [
            "# Easy Level 1: Simple linear path",
            "nb_drones: 2",
            "start_hub: start 0 0 [color=green]",
            "hub: waypoint1 1 0 [color=blue]",
            "hub: waypoint2 2 0 [color=blue]",
            "end_hub: goal 3 0 [color=red]",
            "start_hub: start 0 0 [color=green]",
            "connection: start-waypoint1",
            "connection: waypoint1-waypoint2",
            "connection: waypoint2-goal"
        ]
        assert parsing._is_len_split_two_point(maze_config)[0] is True

    def test_len_split_data1(self) -> None:
        parsing = Parsing("titi")
        maze_config = [
            "# Easy Level 1: Simple linear path:",
            "nb_drones: 2",
            "start_hub: start 0 0 [color=green]",
            "hub: waypoint1 1 0 [color=blue]",
            "hub: waypoint2 2 0 [color=blue]",
            "end_hub: goal 3 0 [color=red]",
            "start_hub: start 0 0 [color=green]",
            "connection: start-waypoint1",
            "connection: waypoint1-waypoint2",
            "connection: waypoint2-goal"
        ]
        assert parsing._is_len_split_two_point(maze_config)[0] is False

    def test_key_valid(self) -> None:
        parsing = Parsing("titi")
        maze_config = [
            "# Easy Level 1: Simple linear path:",
            "nb_drones: 2",
            "start_hub: start 0 0 [color=green]",
            "hub: waypoint1 1 0 [color=blue]",
            "hub: waypoint2 2 0 [color=blue]",
            "end_hub: goal 3 0 [color=red]",
            "start_hub: start 0 0 [color=green]",
            "connection: start-waypoint1",
            "connection: waypoint1-waypoint2",
            "connection: waypoint2-goal"
        ]
        assert parsing._is_key_valid(maze_config)[0] is True

    def test_get_name_in(self) -> None:
        pass
