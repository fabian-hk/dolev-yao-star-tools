#!/usr/bin/env python3
import argparse
import sys

from visualization import dystar_visualization
from validation import dystar_validation
from generation import dystar_generate
from time_verify_lean import add_benchmark_arguments

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="DYStar Tools",
        description="Commandline tool that helps analyzing protocols with DYStar.",
    )
    subparsers = parser.add_subparsers(help="sub-command help")

    # ******* Subparser for Visualization *******
    parser_visualization = subparsers.add_parser(
        "vis",
        help="Parse the output of a DYStar protocol run and generate a Plantuml sequence diagram.",
    )
    parser_visualization.add_argument(
        "-u", "--url",
        help="URL of the Plantuml server (default: https://www.plantuml.com/plantuml/img/)",
        default="https://www.plantuml.com/plantuml/img/"
    )
    parser_visualization.add_argument(
        "program_path", help="path to the DYStar program executable."
    )
    parser_visualization.add_argument(
        "-n", "--namespaces",
        help="only print states and events in these namespaces",
        nargs="*"
    )
    parser_visualization.set_defaults(func=dystar_visualization)

    # ******* Subparser for Validation *******
    parser_validation = subparsers.add_parser(
        "val",
        help="Validate properties of the implementation and the corresponding proofs of a DYStar analysis.",
    )
    parser_validation.add_argument(
        "folder", help="path to the folder containing the protocol analysis."
    )
    parser_validation.set_defaults(func=dystar_validation)

    # ******* Subparser for Code Generation *******
    parser_gen = subparsers.add_parser(
        "gen", help="Generate the proof structure for a DYStar analysis."
    )
    parser_gen.add_argument(
        "folder", help="path to the folder containing the protocol implementation."
    )
    parser_gen.add_argument(
        "-f", "--file", help="specify a file in the folder for which a proof structure should be generated", default=None
    )
    parser_gen.set_defaults(func=dystar_generate)

    # ******* Subparser for Lean Benchmarking *******
    parser_benchmark = subparsers.add_parser(
        "benchmark",
        help="Time Lean verification in the current working directory.",
        description="Discover and time Lean files in the current working directory's Lake project.",
    )
    add_benchmark_arguments(parser_benchmark)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)
    sys.exit(args.func(args))
