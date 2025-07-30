from pathlib import Path
import logging
import re

logger = logging.getLogger(__name__)

find_val_declaration = r"^val\s*[a-zA-Z_0-9]+:(\s*(\n)?[a-zA-Z:\s_0-9\(\)&]+(->))+(\s*(\n)?[a-zA-Z\s_0-9\(\)&]+\n)+"
find_let_declaration = r"^let\s+[a-z_0-9]+(\s+[a-z_0-9]+)+"


def scan_val(file: Path) -> dict:
    with open(file, "r") as f:
        content = f.read()
        val_declarations = re.finditer(
            find_val_declaration, content, flags=re.MULTILINE
        )
        val_declarations_dict = {}
        for vd in val_declarations:
            vd_str = vd.group()
            vd_name = re.match(r"^val\s+[a-zA-Z_0-9]+:", vd_str).group()
            vd_list = vd_str.removeprefix(vd_name).split("->")
            name = vd_name.removeprefix("val").removesuffix(":").strip()
            arguments = []
            for arg in vd_list:
                arg_split = arg.split(":")
                if len(arg_split) == 2:
                    arguments.append(
                        {"type": arg_split[1].strip(), "name": arg_split[0].strip()}
                    )
                else:
                    arguments.append({"type": arg_split[0].strip(), "name": ""})
            val_declarations_dict[name] = arguments
    logger.debug(val_declarations_dict)
    return val_declarations_dict


def scan_let(file: Path) -> dict:
    with open(file, "r") as f:
        content = f.read()
        let_declarations = re.finditer(
            find_let_declaration, content, flags=re.MULTILINE
        )
        let_declarations_dict = {}
        for ld in let_declarations:
            ld_str = ld.group()
            ld_list = ld_str.split()
            name = ld_list[1]
            arguments = [a.strip() for a in ld_list[2:]]
            let_declarations_dict[name] = arguments
    logger.debug(let_declarations_dict)
    return let_declarations_dict


def combine_val_let(val_dict: dict, let_dict: dict) -> dict:
    combined_dict = {}
    for vd in val_dict.keys():
        if vd in let_dict.keys():
            combined_dict[vd] = []
            for val_arg, let_arg in zip(val_dict[vd], let_dict[vd]):
                if val_arg["name"] == "":
                    combined_dict[vd].append({"type": val_arg["type"], "name": let_arg})
                else:
                    if val_arg["name"] != let_arg:
                        logger.warning(
                            f"Argument name mismatch for function {vd} ({val_arg['name']} != {let_arg})"
                        )
                    combined_dict[vd].append(
                        {"type": val_arg["type"], "name": val_arg["name"]}
                    )
        else:
            logger.error(
                f"Function {vd} has no let implementation. This is no valid F* code."
            )
    logger.debug(combined_dict)
    return combined_dict


def build_proof_functions(comb_dict: dict) -> dict:
    proof_functions = {}
    for func in comb_dict.keys():
        proof_functions[f"{func}_proof"] = [{"type": "trace", "name": "tr"}]
        for arg in comb_dict[func]:
            proof_functions[f"{func}_proof"].append(
                {"type": arg["type"], "name": arg["name"]}
            )
    logger.debug(proof_functions)
    return proof_functions


def find_code(folder: Path, type: str) -> Path:
    for file in folder.iterdir():
        if file.is_file() and str(file).endswith(f".{type}.fst"):
            return file
    logger.error(f"No {type} code found in {folder}")
    return None
