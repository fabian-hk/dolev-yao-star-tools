# DY* Tools

This repository contains a Python script to help develop 
formal security analysis with [DY*](https://github.com/REPROSEC/dolev-yao-star-extrinsic). 
The script has two 
functionalities: First, there is a subcommand to visualize 
a debug trace, and second, there is a subcommand to make
some plausibility checks on the protocol and proof code.

# Visualization

The command `./dystar_tool vis <DYSTAR_EXE>` runs an executable DY*
protocol run and converts the output into a Plantuml
sequence diagram.

# Validation

The command `./dystar_tool val <DYSTAR_PROTOCOL_FOLDER>` runs some
plausibility checks on the protocol and proof code.
For this to work, the protocol code files must have the suffix
`.Total.fst` and `.Stateful.fst` and the proof code files must
have the suffix `.Total.Proof.fst` and `.Stateful.Proof.fst`.