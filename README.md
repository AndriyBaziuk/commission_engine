# Daily Commission Engine for a MLM Network

## Overview

This project calculates daily commissions in a MLM network. Each partner earns a 5% commission on the daily gross profit of all their descendants (direct and indirect). The system is designed for high scale: ≥ 50,000 partners and ≥ 15 levels of hierarchy, completing within 2 seconds.

## Features

* CLI interface with JSON-based input/output
* Cycle and invalid tree structure detection
* Efficient commission calculation
* Unit-tested and benchmarked

### Input Format

```json
[
  {
    "id": 1,
    "parent_id": null,
    "name": "Partner1",
    "monthly_revenue": 10000
  },
]
```

### Output Format

```json
{
  "1": 2345.67,
  "2": 456.78,
}
```

### Commission Formula

```
commission_p = 0.05 × sum(daily_profit_d) for all descendants of p
```

where:

```
daily_profit = monthly_revenue / days_in_month
```

_days_in_month_ is determined automatically and is equal to the number of days of the current month

### Execution

```bash
python3 main.py --input partners.json --output commissions.json
```

## Algorithm

I used the **post-order DFS** to accumulate descendant profits and calculate commissions.

### Steps

1. **Build Tree:** Parse input and construct a partners tree.
2. **Cycle Detection:** Run DFS with a recursion stack.
3. **Commission Calculation:** Use post-order DFS to extend profits upward. Memoisation is unnecessary due to strict tree (no revisits).

### Time Complexity

* Build tree: O(n)
* Cycle detection: O(n + e), where e is a number of edges
* Commissions calculation: O(n)
* **Overall: O(n)**

### Space Complexity

* Build tree: O(n)
* Cycle detection: O(n)
* Commissions calculation: O(n)
* **Overall: ≤ 2 × input size**

## Benchmarks

* **Input:** 50,000 generated partners
* **Machine:** 6-core, 3.5 GHz CPU, 16 GB RAM
* **Result:** 0.065s average execution time

Custom number of partners to be generated can be passed via the ```-n``` argument:

```bash
python3 benchmark.py -n 70000
```

## Testing

Install required packages (pytest) before running tests:

```bash
pip install -r requirements.txt 
```

Run unit tests with:

```bash
python3 -m pytest
```

Coverage includes:

* Basic commission flow
* Leaf nodes
* Tree with depth
* Cycles, nonexistent parents, missing roots and multiple roots
