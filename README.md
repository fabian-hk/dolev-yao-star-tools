# DY* Tools

This repository contains a Python script to assist 
in the development of formal security analysis using 
[DY*](https://github.com/REPROSEC/dolev-yao-star-extrinsic).
The script has four functionalities: First, there is
a subcommand to visualize a debug trace. Second, there is 
a subcommand to make some plausibility checks on the protocol
and proof code, and third, there is a subcommand to generate 
the proof structure for the total and stateful proofs. Fourth, the `benchmark`
subcommand measures Lean verification times.

## Visualization

The command `./dystar_tool vis <DYSTAR_EXE>` runs an executable DY*
protocol run and converts the output into a Plantuml
sequence diagram.

## Validation

The command `./dystar_tool val <DYSTAR_PROTOCOL_FOLDER>` runs some
plausibility checks on the protocol and proof code.
For this to work, the protocol code files must have the suffix
`.Total.fst` and `.Stateful.fst` and the proof code files must
have the suffix `.Total.Proof.fst` and `.Stateful.Proof.fst`.

Currently, the following validations are done:

1. Check that every protocol function has a corresponding proof function.
2. Compare the parameters for the protocol function with the parameters
    of the proof function and warn if they deviate.

## Generate Proof Structure

The command `./dystar_tool gen <DYSTAR_PROTOCOL_FOLDER>` generates
the basic structure for the total and stateful proofs from
the protocol implementation. For this command to work
the protocol must be implemented in a file ``*.Total.fst``
and ``*.Stateful.fst`` and the code must follow the [DY* coding guidelines](https://github.com/REPROSEC/dolev-yao-star-extrinsic/blob/main/CONTRIBUTING.md#coding-style).

## Benchmark Lean Verification

From the Lean project's directory (containing `lakefile.toml` or `lakefile.lean`), run:

```sh
python3 /path/to/dystar_tool.py benchmark
```

The scan root is always the directory where the command is invoked. By default,
the command scans its `.lean` files, excluding hidden directories and
`lakefile.lean`, and includes their transitive workspace dependencies. Imports
are built outside the timer; each source is then verified sequentially with
`lake lean`. Python 3.9+ and the project's Lake toolchain are required.

Optional files restrict the scan roots, for example `benchmark Web/URL.lean`.
Use `--project-only` to time only project sources, or `--graph-only` to generate
the dependency graph without verification. Outputs default to
`verification-times.csv`, `dependency-graph.dot`, and `.lake/verification-logs`
relative to the invocation directory; override them with `--csv`, `--graph`,
and `--log-dir`. The command returns a nonzero exit status on failure.
