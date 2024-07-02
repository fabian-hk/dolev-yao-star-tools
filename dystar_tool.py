#!/usr/bin/env python3
import argparse

from visualization import dystar_visualization
from validation import dystar_validation

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="DYStar Tools",
        description="Commandline tool that helps analyzing protocols with DYStar."
    )
    subparsers = parser.add_subparsers(help='sub-command help')
    parser_visualization = subparsers.add_parser("vis",
                                                 help="Parse the output of a DYStar protocol run and generate a Plantuml sequence diagram.")
    parser_visualization.add_argument(
        "program_path",
        help="Path to the DYStar program executable."
    )
    parser_visualization.set_defaults(func=dystar_visualization)

    parser_validation = subparsers.add_parser("val",
                                              help="Validate properties of the implementation and the corresponding proofs of a DYStar analysis.")
    parser_validation.add_argument(
        "folder",
        help="Path to the folder containing the protocol analysis."
    )
    parser_validation.set_defaults(func=dystar_validation)

    args = parser.parse_args()
    args.func(args)
