#!/usr/bin/env python3
import argparse

from visualization import dystar_visualization
from validation import dystar_validation
from generation import dystar_generate

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
    parser_gen.set_defaults(func=dystar_generate)

    args = parser.parse_args()
    args.func(args)
