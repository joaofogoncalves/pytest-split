import argparse
import glob
import json
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict


def list_slowest_tests() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--durations-path",
        help=(
            "Path to the file in which durations are stored, "
            "default is .test_durations in the current working directory"
        ),
        default=".test_durations",
        type=argparse.FileType(),
    )
    parser.add_argument(
        "-c",
        "--count",
        help="How many slowest to list",
        default=10,
        type=int,
    )
    args = parser.parse_args()
    return _list_slowest_tests(json.load(args.durations_path), args.count)


def _list_slowest_tests(durations: "Dict[str, float]", count: int) -> None:
    slowest_tests = tuple(
        sorted(durations.items(), key=lambda item: item[1], reverse=True)
    )[:count]
    for test, duration in slowest_tests:
        print(f"{duration:.2f} {test}")  # noqa: T201


def run_combine_tests() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--durations-path",
        help=(
            "Path to the file in which durations are stored, "
            "default is .test_durations in the current working directory"
        ),
        default=".test_durations",
        type=str,
    )
    parser.add_argument(
        "--durations-pattern",
        help=(
            "Pattern to match the files in which durations are stored, "
            "default is */.test_durations in the current working directory"
        ),
        default="*/.test_durations",
        type=str,
    )
    parser.add_argument(
        "--root-folder",
        help=(
            "Path to the folder where to run the command"
            "default is . to run in the current working directory"
        ),
        default=".",
        type=str,
    )
    parser.add_argument("--keep_original", action="store_true", default=False)

    args = parser.parse_args()

    return _run_combine_tests(
        args.durations_path,
        args.durations_pattern,
        args.root_folder,
        keep_original=args.keep_original,
    )


def _run_combine_tests(
    durations_path: str,
    durations_pattern: str,
    root_folder: str,
    *,
    keep_original: bool,
) -> None:
    """
    Combines JSON files matching a pattern into a single object and writes it to an output file.

    Args:
        durations_pattern (str): A file pattern (e.g., "data_*.json") to match JSON files.
        durations_path (str): The path to the output file where the combined data will be written.

    """
    combined_data = {}
    filenames = glob.glob(durations_pattern, root_dir=root_folder)

    if not filenames:
        print(  # noqa: T201
            f"No file found with pattern {durations_pattern} in {root_folder}"
        )
        return

    try:
        for filename in filenames:
            fullpath_filename = os.path.join(root_folder, filename)
            with open(fullpath_filename) as f:
                data = json.load(f)
            combined_data.update(data)  # Efficiently merge dictionaries
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error processing file '{filename}': {e}")  # noqa: T201
        return

    if keep_original:
        with open(durations_path) as f:
            data = json.load(f)
        combined_data.update(data)

    print(  # noqa: T201
        f"{len(filenames)} files combined, with a total of {len(combined_data)} entries"
    )

    with open(durations_path, "w") as f:
        json.dump(combined_data, f, indent=4)  # Write with indentation
