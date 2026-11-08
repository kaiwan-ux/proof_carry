"""Restore compressed CSVs without overwriting existing research data."""
from pathlib import Path
import gzip
import hashlib
import shutil

def digest(stream):
    value = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        value.update(block)
    return value.digest()

def main():
    root = Path(__file__).resolve().parents[1]
    sources = sorted(root.glob("ProofCarry_Final_Experimental_120/**/expanded120.csv.gz"))
    if not sources:
        raise SystemExit("No compressed expanded120 results found.")
    for source in sources:
        target = source.with_suffix("")
        if target.exists():
            with gzip.open(source, "rb") as data, target.open("rb") as existing:
                if digest(data) != digest(existing):
                    raise SystemExit(f"Refusing to overwrite mismatched file: {target}")
            print(f"Verified existing: {target.relative_to(root)}")
        else:
            with gzip.open(source, "rb") as data, target.open("xb") as output:
                shutil.copyfileobj(data, output)
            print(f"Restored: {target.relative_to(root)}")

if __name__ == "__main__":
    main()
