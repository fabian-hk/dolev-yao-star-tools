from typing import Tuple
from pathlib import Path
import os
import logging
import jinja2

import utility

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def generate_proof(folder: Path, type: str):
    total_impl = utility.find_code(folder, "Total")
    stateful_impl = utility.find_code(folder, "Stateful")

    total_module = os.path.basename(total_impl).removesuffix(".fst")
    total_proof_module = total_module + ".Proof"
    stateful_module = os.path.basename(stateful_impl).removesuffix(".fst")
    stateful_proof_module = stateful_module + ".Proof"

    impl = utility.find_code(folder, type)

    impl_val = utility.scan_val(impl)
    impl_let = utility.scan_let(impl)
    impl_comb = utility.combine_val_let(impl_val, impl_let)

    gen_proof = utility.build_proof_functions(impl_comb)

    environment = jinja2.Environment(loader=jinja2.FileSystemLoader("templates/"))
    environment.globals.update(zip=zip)
    template = environment.get_template(f"{type}.Proof.fst.jinja2")
    content = template.render(
        module_name=total_proof_module if type == "Total" else stateful_proof_module,
        total_code=total_module,
        total_proof=total_proof_module,
        stateful_code=stateful_module,
        declarations=gen_proof,
        impl_functions=impl_let,
    )
    logger.debug(content)
    proof_file = (
        folder / f"{total_proof_module}.fst"
        if type == "Total"
        else folder / f"{stateful_proof_module}.fst"
    )
    if not proof_file.exists():
        proof_file.write_text(content)
        logger.info(f"Generated {os.path.basename(proof_file)}")
    else:
        logger.error(f"File {os.path.basename(proof_file)} already exists in the destination")


def dystar_generate(args):
    folder = Path(args.folder)
    generate_proof(folder, "Total")
    generate_proof(folder, "Stateful")
