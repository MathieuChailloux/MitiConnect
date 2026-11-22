
import qpip
import importlib.metadata
from pathlib import Path

def read_requirements():
    req_file = Path(__file__).parent / "requirements.txt"

    requirements = []

    for line in req_file.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        requirements.append(line)

    return requirements

def missing_packages():
    missing = []

    for requirement in read_requirements():
        package = requirement.split(">=")[0].split("==")[0]

        try:
            importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            missing.append(requirement)

    return missing

missing = missing_packages()

if missing:
    qpip.install(missing)