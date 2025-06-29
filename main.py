import argparse
import json

from commission_engine.core import calculate_commissions
from commission_engine.exceptions import (
    CycleError,
    MultipleRootsError,
    RootNotFoundError,
)
from commission_engine.utils import get_days_in_month


def main():
    parser = argparse.ArgumentParser(
        description="Daily Commission Engine for a MLM Network"
    )
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        partners = json.load(f)

    days_in_month = get_days_in_month()
    try:
        commissions = calculate_commissions(partners, days_in_month)
    except MultipleRootsError:
        print("Multiple root partners detected. Please correct input data.")
        exit(1)
    except RootNotFoundError:
        print("No root partner found. Please correct input data.")
        exit(1)
    except CycleError:
        print("Cycle detected in partners structure. Please correct input data.")
        exit(1)

    with open(args.output, "w") as f:
        json.dump(commissions, f, indent=2)


if __name__ == "__main__":
    main()
