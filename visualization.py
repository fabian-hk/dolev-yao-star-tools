import os
import subprocess
import json
from pathlib import Path
from plantuml import PlantUML


# Find all principals from log sessions
def find_principals(lines: list[dict]):
    principals = []
    for line in lines:
        if line["Type"] == "Session":
            if line["Principal"] not in principals:
                principals.append(line["Principal"])
    return principals


def dystar_visualization(args):
    program_path = args.program_path
    process = subprocess.Popen([program_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    output = stdout.decode('utf-8')
    lines = []
    # Parse output lines as json and skip lines that are not valid json.
    for line in output.split("\n"):
        try:
            lines.append(json.loads(line))
        except json.JSONDecodeError:
            pass

    principals = find_principals(lines)

    last_principal = "alice"
    plantuml = ["@startuml"]
    for line in lines:
        # Draw sessions to the plantuml diagram
        if line["Type"] == "Session":
            plantuml.append(
                f"{line['Principal']} -> {line['Principal']} : Session {line['Content']}"
            )
        # Use events to find out at which principal
        # we are right now in the protocol run.
        elif line["Type"] == "Event":
            last_principal = line["Principal"]
        # Draw messages to the plantuml diagram
        # as arrows from one principal to another
        elif line["Type"] == "Message":
            # We assume that the last active principal is
            # sending the message.
            sender = last_principal
            # We assume that there are only two principals.
            # So we can take the other principal as the receiver.
            # TODO find other heuristics for more complex protocols.
            principals_copy = principals.copy()
            principals_copy.remove(sender)
            receiver = principals_copy[0]
            plantuml.append(
                f"{sender} -> {receiver} : {line['Content']}"
            )
    plantuml.append("@enduml")

    # Write generated plantuml code to file
    # plantuml_file = Path(f"{os.path.basename(program_path)}.puml")
    # plantuml_file.write_text("\n".join(plantuml))

    # Generate PNG from plantuml code
    puml = PlantUML(url="http://www.plantuml.com/plantuml/img/")
    png_raw = puml.processes("\n".join(plantuml))
    png_file = Path(f"{os.path.basename(program_path)}.png")
    png_file.write_bytes(png_raw)

    # Open the generated PNG file in
    # the default image viewer.
    subprocess.Popen(["xdg-open", str(png_file)])
