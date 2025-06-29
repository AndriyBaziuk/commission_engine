import argparse
import random
from timeit import repeat

from commission_engine.core import Partner, calculate_commissions


def generate_partners(n: int) -> list[Partner]:
    return [
        {
            "id": i,
            "parent_id": i // 2 if i != 1 else None,
            "monthly_revenue": random.randint(200, 8000),
        }
        for i in range(1, n + 1)
    ]


def benchmark(total_partners: int) -> None:
    print(f"Generating {total_partners:,} partners...")
    partners = generate_partners(total_partners)

    number_of_repeats = 5
    time_list = repeat(
        "func(partners, 30)",
        repeat=number_of_repeats,
        number=1,
        globals={"func": calculate_commissions, "partners": partners},
    )
    average_time = sum(time_list) / number_of_repeats
    print(f"Average computation time: {average_time:.3f}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        default=50_000,
        help="Number of partners to generate (defaults to %(default)s)",
    )
    args = parser.parse_args()
    benchmark(total_partners=args.number)
