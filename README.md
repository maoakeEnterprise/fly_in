*This project has been created as part of the 42 curriculum by mteriier.*

# Fly-in

## Description

**Fly-in** routes a fleet of autonomous drones through a network of connected
zones, from a central base (the *start hub*) to a target location (the *end
hub*), in as few simulation turns as possible.

A map file describes the network: the fleet size, the zones with their
coordinates, movement cost and capacity, and the bidirectional connections
between them with their own capacity. The program reads that file, validates it,
builds a graph out of it, computes a route, then replays the delivery turn by
turn while enforcing every occupancy rule — a zone never holds more drones than
its `max_drones`, a connection never carries more than its `max_link_capacity`,
blocked zones are never entered, and entering a restricted zone costs the drone
two turns during which it sits on the link.

The run produces two outputs at once: the turn-by-turn move list on stdout, in
the format required by the subject, and an animated matplotlib replay of the
same simulation.

The whole project is object-oriented, fully type-hinted, and uses no external
graph library — the graph structure, Dijkstra, the fleet spreading and the turn
engine are all written from scratch. `pydantic` is used for value validation on
the parsed models, `matplotlib` for the animation only.

### Project layout

| Path | Role |
|---|---|
| `src/__main__.py` | Entry point: wires the pipeline together and catches every error |
| `utils/flag_manager.py` | `FlagManager` — CLI flags, one per shipped map |
| `utils/parsing.py` | `Parsing` — syntactic validation of a map file |
| `utils/translator.py` | `Translator(Parsing)` — valid lines → `Hub` / `Connection` objects |
| `utils/hub.py`, `utils/connection.py` | pydantic models, second layer of value checks |
| `utils/graph.py` | `Node`, `Edge`, `Graph`, `Path_Finder` — network + Dijkstra + fleet spreading |
| `utils/drone.py` | `Drone` — id, assigned route, progress, flight state |
| `utils/simulator.py` | `Simulator` — turn engine, capacity enforcement, history recording |
| `utils/visualizer.py` | `Visualizer` — animated replay of the recorded history |
| `maps/` | Shipped maps (easy / medium / hard / challenger) + invalid-map fixtures |
| `tests/` | pytest suites and the invalid-map error bench |

---

## Instructions

### Requirements

- **Python ≥ 3.13** (see `.python-version`)
- [`uv`](https://docs.astral.sh/uv/) as package manager
- A display able to open a matplotlib window (the replay is part of every run)

### Installation

```sh
make install      # uv sync — installs pydantic, numpy, matplotlib + dev tools
```

### Running

```sh
make run          # shortcut for: uv run python -m src --graph --launch_E1
```

Or directly, choosing the map with a flag:

```sh
uv run python -m src --launch_E1
```

**Exactly one map flag must be raised per run**, otherwise the program stops with
`There is too much or no flag up flag up should be one`.

| Flag | Map |
|---|---|
| `--launch_E1` | `maps/easy/01_linear_path.txt` |
| `--launch_E2` | `maps/easy/02_simple_fork.txt` |
| `--launch_E3` | `maps/easy/03_basic_capacity.txt` |
| `--launch_M1` | `maps/medium/01_dead_end_trap.txt` |
| `--launch_M2` | `maps/medium/02_circular_loop.txt` |
| `--launch_M3` | `maps/medium/03_priority_puzzle.txt` |
| `--launch_H1` | `maps/hard/01_maze_nightmare.txt` |
| `--launch_H2` | `maps/hard/02_capacity_hell.txt` |
| `--launch_H3` | `maps/hard/03_ultimate_challenge.txt` |
| `--launch_C1` | `maps/challenger/01_the_impossible_dream.txt` |
| `--default_launch` | same as `--launch_E1` |

Every map flag also accepts a value, which overrides the map it points to. This
is how a custom map is run:

```sh
uv run python -m src --launch_E1 path/to/my_map.txt
```

The value is expanded as a glob and the first match is read, so a prefix is
enough (`"maps/easy/02*"`).

`--graph` is accepted and readable through `FlagManager.is_graphed()`, but the
entry point currently renders the animation on every run, so raising it changes
nothing today.

### Other targets

```sh
make lint              # flake8 . + mypy . with the flags required by the subject
make debug             # runs the entry point under pdb
make clean             # removes __pycache__, .mypy_cache, .pytest_cache
make test_parsing      # pytest on the parser
make test_flag_manager # pytest on the CLI
make norming           # watch flake8
make norming_mp        # watch mypy
```

`make lint` passes clean: no flake8 report, no mypy issue over the 14 source
files.

---

## Usage examples

### A normal run

```sh
$ uv run python -m src --launch_E2
D0-junction D1-junction
D0-path_a D2-junction
D0-goal D1-path_a D3-junction
D1-goal D2-path_a
D2-goal D3-path_a
D3-goal
=== Simulation finished in 6 turns ===
```

One line per turn, one entry per drone that moved this turn, drones that stayed
put being omitted. `D<id>-<zone>` is a landing; `D<id>-<src>-<dst>` is a take-off
over a connection leading to a restricted zone — the drone occupies the link for
that turn and lands on the next one. Delivered drones stop being reported.

### An invalid map

```sh
$ uv run python -m src --launch_E1 "maps/easy/bad_19*"
Parsing error near line 7 : format name hub is not good or uniquename hub
Parsing error near line 8 : the coord is not unique
```

Errors are collected instead of raised on the first one, so a single run reports
what it found with the line number and a cause, and the simulation never starts.

---

## Performance

Measured with the maps shipped in `maps/`. Every target of the subject is met,
and the challenger reference record is beaten.

| Map | Drones | Target | Result |
|---|---|---|---|
| Easy 1 — linear path | 2 | ≤ 6 | **4** |
| Easy 2 — simple fork | 4 | ≤ 8 | **6** |
| Easy 3 — basic capacity | 4 | ≤ 6 | **4** |
| Medium 1 — dead end trap | 5 | ≤ 12 | **8** |
| Medium 2 — circular loop | 6 | ≤ 15 | **10** |
| Medium 3 — priority puzzle | 5 | ≤ 12 | **8** |
| Hard 1 — maze nightmare | 8 | ≤ 30 | **13** |
| Hard 2 — capacity hell | 12 | ≤ 35 | **16** |
| Hard 3 — ultimate challenge | 15 | ≤ 45 | **26** |
| Challenger — the impossible dream | 25 | record 45 | **43** |

---

## Algorithm choices and implementation strategy

The pipeline is a straight line, each stage owning one concern and handing
objects — never raw text — to the next:

```
FlagManager → Parsing → Translator → Graph → Path_Finder → Simulator → Visualizer
   flags       syntax     objects     model    routing       turns       replay
```

### 1. Parsing, in two passes

`Parsing` answers one question only: *can this file be read?* It never tries to
interpret what a line means. It runs whole-file rules first — the first useful
line must be `nb_drones:`, there must be exactly one `start_hub:` and one
`end_hub:`, names and coordinates must be unique, connections must reference
already-defined zones and must not be declared twice — then line-by-line rules
on the key, the coordinates and the metadata block.

The deliberate choice here is that **errors are accumulated, not raised**.
`parse_data()` returns a list of `(bool, line, cause)` tuples, so one run over a
badly written map reports everything wrong with it instead of stopping on the
first mistake. `maps/easy/bad_*.txt` is the bench built for that behaviour: 19
maps each carrying one known defect, plus `bad_20_valid_control.txt`, a valid map
whose job is to catch false positives from a rule that became too strict.

### 2. Translation, and a second validation layer

`Translator` subclasses `Parsing` so it can reuse its line readers, and assumes
the file already passed validation. Each accepted line becomes a `Hub` or a
`Connection`, which are **pydantic models**: `max_drones` and `max_link_capacity`
are declared `Field(gt=0)`, and a `model_validator` enforces that the start and
end zones keep a `normal` movement cost. Syntax is checked by the parser, values
are checked by the models — two layers, two responsibilities.

### 3. Graph, with two views of the map

`Graph` keeps the network **twice**:

- `nodes` / `edges` exclude the blocked zones. This is the graph the pathfinding
  walks, so a blocked zone is not "avoided" by a special case inside the
  algorithm — it simply does not exist in the structure the algorithm sees. A
  connection is skipped as soon as one of its ends is missing, which is what
  prunes the dead branches.
- `complete_nodes` / `complete_edges` keep every zone, blocked ones included, so
  the visualizer can still draw them.

Connections are bidirectional in the file, and are stored as two `Edge` objects,
one in each adjacency list.

### 4. Routing: Dijkstra weighted by entry cost

Movement cost is a property of the **destination** zone, not of the connection,
so the weight of an edge is `Node.entry_cost()` of the zone it leads to: `2` for
a restricted zone, `1` for a normal or priority one, `0` for the start zone since
the fleet is already sitting there.

Dijkstra was chosen over BFS precisely because of that: with restricted zones the
graph is weighted, and a plain BFS would return the route with the fewest hops
rather than the cheapest one in turns. The heap entries are
`(cost, priority_count, tie, name)`:

- **`cost`** is the real criterion.
- **`priority_count`** implements the subject's rule that priority zones cost 1
  turn *but should be preferred*: it cannot change which route is cheapest, it
  only settles ties between routes of equal cost in favour of the one crossing
  the most priority zones. That is what makes it a preference and not a cost
  distortion.
- **`tie`** is a monotonic counter, so two entries comparing equal on both
  criteria never make the heap fall back to comparing zone names, and the
  ordering stays total and stable.

Complexity is the usual `O((V + E) log V)`. The route is computed **once per
run** and rebuilt from the predecessor table; nothing is recomputed during the
simulation, so the pathfinding cost does not grow with the fleet size.

### 5. Fleet spreading

`spread_drones()` hands the drones out one at a time, each one going to the route
with the lowest **projected arrival** — its cost in turns plus the number of
drones already queued on it. The model behind that number is that a route takes
one new drone per turn, so the *n*-th drone on a route of cost *c* lands around
turn *c + n*. Greedily minimizing that value at each hand-out is what balances
the fleet instead of piling it onto the shortest route and letting it queue.

The API takes a list of routes and returns a count per route, so the structure is
already the multi-path one; the current entry point feeds it the single cheapest
route, which is enough to meet every benchmark above.

### 6. The turn engine

`Simulator.run()` is where the constraints are actually enforced. Each turn:

1. **The fleet is re-sorted by progress, most advanced first.** This is the key
   ordering decision: a drone moving out of a zone frees it *within the same
   turn*, so evaluating the leaders first lets the drones behind them advance
   immediately instead of waiting a turn for the space to open. Sorting the other
   way round would serialize the whole convoy.
2. Two per-turn counters are rebuilt from scratch — `occupancy` per zone and
   `link_usage` per `(src, dst)` pair. A move is allowed only if both the target
   zone and the link still have room, which is how `max_drones` and
   `max_link_capacity` are enforced together without any state leaking between
   turns.
3. Each drone then does one of three things: it **lands** on the next zone, it
   **takes off** over a connection toward a restricted zone (`in_flight = True`,
   it occupies the link this turn and lands on the next one, and it cannot wait
   there), or it **waits** on its current zone when the link or the target is
   saturated — a wait still counts against the occupancy of the zone it stays on.
4. The moves are printed as one line, and a snapshot of the whole fleet is
   appended to `history`.

Deadlock avoidance falls out of the structure rather than from a dedicated check:
every drone follows a precomputed acyclic route, so a blocked drone is always
blocked by a drone ahead of it on the same route, which is itself either moving
or delivered. No drone ever waits on a drone that waits on it.

Simulation and rendering are fully decoupled: the engine records `history`, one
frame per turn, and the visualizer replays it afterwards. Nothing is drawn while
the fleet moves, so the display cannot influence the result and the same run can
be replayed at any speed.

### Memory

Nothing is stored per turn beyond the frames: the graph is built once, the route
is computed once, and the per-turn counters are thrown away at the end of each
turn. `history` is the only structure that grows, at one tuple per drone per
turn.

---

## Visual representation

The subject asks for visual feedback of the simulation. Fly-in provides **both**
outputs, from the same run.

### Terminal output

The move list described in *Usage examples* — one line per turn, in the exact
format required by the subject, plus a closing `=== Simulation finished in N
turns ===`. It is the machine-readable trace, and it is what makes one run
comparable to another.

### Animated replay (matplotlib)

`Visualizer` replays the recorded history over a map drawn once and never
redrawn — only the drone markers are cleared and rebuilt at each turn.

What it shows, and why it helps:

- **The map itself.** Zones are drawn at their real coordinates, in the color
  declared in the file, connected by their links. A color the renderer does not
  know falls back to gray, and the legend says so explicitly — so a typo in a map
  file becomes visible instead of silent.
- **Roles carried by the outline, not the fill.** Since the fill color belongs to
  the map file, the role of a zone is drawn as its border: **green** for the
  start, **red** for the end, **purple** for a restricted zone, a **thick gray**
  for a blocked one. This is what lets you see, at a glance, why the route avoids
  a whole region of the map.
- **Drones grouped by position, with a count.** Drones sharing a zone are drawn
  as a single dark marker carrying how many they are. On a crowded map this keeps
  the display readable, and more importantly it makes the capacities *visible*:
  a marker that stops at `3` on a `max_drones=3` zone while others queue behind
  it is the constraint being enforced, on screen.
- **Drones in flight sit on the link.** A drone crossing toward a restricted zone
  is drawn halfway between the two zones — that is why frame coordinates are
  floats and not the integers of the zones. The two-turn cost of a restricted
  zone becomes something you watch happen rather than something you read in the
  rules.
- **A live title.** `Turn i / N   Delivered: d / total`, so progress and the turn
  budget are readable without counting frames.
- **Pause and resume with the space bar**, since a busy map goes by fast and the
  interesting turns are usually the congested ones.

The window closes on its own one interval after the last turn, so the final state
stays on screen as long as any other turn instead of flashing by.

---

## Resources

### Documentation and references

- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- Cormen, Leiserson, Rivest, Stein — *Introduction to Algorithms*, ch. 24
  (single-source shortest paths) and ch. 26 (maximum flow), the references for
  shortest paths and for capacity-constrained routing
- [`heapq` — Python documentation](https://docs.python.org/3/library/heapq.html),
  including the tie-breaking counter pattern used in `dijkstra_alg`
- [`argparse` — Python documentation](https://docs.python.org/3/library/argparse.html)
- [`glob` — Python documentation](https://docs.python.org/3/library/glob.html)
- [pydantic — validators and fields](https://docs.pydantic.dev/latest/concepts/validators/)
- [matplotlib `FuncAnimation`](https://matplotlib.org/stable/api/_as_gen/matplotlib.animation.FuncAnimation.html)
- [PEP 257 — Docstring conventions](https://peps.python.org/pep-0257/) and the
  [Google Python style guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings),
  the docstring style used across the codebase
- [mypy documentation](https://mypy.readthedocs.io/) and
  [flake8 documentation](https://flake8.pycqa.org/)

### Use of AI

AI was used as an assistant on specific, bounded tasks, never as the author of
the project's logic. Concretely:

- **Docstrings.** The Google-style docstrings across `utils/` were drafted with
  AI assistance, then reviewed and corrected file by file — the parser, the
  graph, the simulator, the translator and the visualizer each got their own
  pass. The goal was consistency of wording and PEP 257 compliance, on code that
  already existed.
- **Test fixtures.** The invalid-map bench (`maps/easy/bad_*.txt` and its
  `BAD_MAPS.md` expectation table) was built with AI help to enumerate the error
  cases listed in the subject's parser constraints, including the valid control
  map used to detect false positives.
- **This README.** Drafted with AI from the source code and from real runs of the
  shipped maps; every number in the performance table was measured, not
  estimated.

The design decisions — the two-pass parser accumulating errors, the two views of
the graph, Dijkstra weighted by entry cost with the priority tie-break, the
progress-ordered turn engine, the decoupling of simulation and rendering — were
made and implemented by hand, and can be explained and modified during the peer
review.
