import sys

from utils.io import fetch_and_cache

if __name__ == "__main__":
    fetch_and_cache(force="--force" in sys.argv)
    print("Data ready in data/")
