from pathlib import Path
import logging

import utility

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def find_argument(arg: dict, arg_list: list) -> bool:
    for a in arg_list:
        if a["name"] == arg["name"] and a["type"] == arg["type"]:
            return True
    return False


def validate_proof_functions(gen_proof: dict, proof: dict) -> None:
    for gen in gen_proof.keys():
        if gen not in proof.keys():
            logger.error(f"Function {gen} is not proven.")
        else:
            logger.info(f"Validating function {gen}")
            for arg in gen_proof[gen]:
                if not find_argument(arg, proof[gen]):
                    logger.warning(f"Function {gen} is missing an argument: {arg}")
            for arg in proof[gen]:
                if not find_argument(arg, gen_proof[gen]):
                    logger.warning(f"Function {gen} has an additional argument: {arg}")


def validate_code(folder: Path, type: str):
    logger.info(f"************ Start Checking {type} Code ************")
    implementation = utility.find_code(folder, type)
    impl_val_dict = utility.scan_val(implementation)
    impl_let_dict = utility.scan_let(implementation)

    proof = Path(str(implementation).removesuffix(".fst") + ".Proof.fst")
    proof_val_dict = utility.scan_val(proof)
    proof_let_dict = utility.scan_let(proof)

    impl_comb_dict = utility.combine_val_let(impl_val_dict, impl_let_dict)
    proof_comb_dict = utility.combine_val_let(proof_val_dict, proof_let_dict)

    impl_proof_dict = utility.build_proof_functions(impl_comb_dict)

    validate_proof_functions(impl_proof_dict, proof_comb_dict)
    logger.info(f"************ End Checking {type} Code ************")


def dystar_validation(args):
    folder = Path(args.folder)
    validate_code(folder, "Total")
    validate_code(folder, "Stateful")
