"""Download Nemotron-Personas-Korea parquet shards from HuggingFace into data/raw/."""
from pathlib import Path
from huggingface_hub import snapshot_download

REPO_ID = "nvidia/Nemotron-Personas-Korea"
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)


def main() -> None:
    path = snapshot_download(
        repo_id=REPO_ID,
        repo_type="dataset",
        local_dir=str(RAW),
        allow_patterns=["*.parquet", "README.md", "*.json"],
    )
    print(f"Downloaded to: {path}")
    for p in sorted(RAW.rglob("*.parquet")):
        size_mb = p.stat().st_size / 1e6
        print(f"  {p.relative_to(RAW)}  {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
