from collections import defaultdict
from typing import NotRequired, TypedDict

from commission_engine.exceptions import (
    CycleError,
    MultipleRootsError,
    ParentNotFoundError,
    RootNotFoundError,
)

COMMISSION_RATE = 0.05


class Partner(TypedDict):
    id: int
    parent_id: int | None
    name: NotRequired[str]
    monthly_revenue: int


def detect_cycle(tree: dict[int, list[int]]) -> bool:
    """Detects if there is a cycle in a tree structure."""
    visited, stack = set(), set()

    def dfs(node: int) -> bool:
        if node in stack:
            return True
        if node in visited:
            return False
        stack.add(node)
        for child in tree.get(node, []):
            if dfs(child):
                return True
        stack.remove(node)
        visited.add(node)
        return False

    for node in tree:
        if node not in visited and dfs(node):
            return True

    return False


def build_partners_tree(partners: list[Partner]) -> tuple[dict[int, list[int]], int]:
    """
    Builds a tree from a list of partners, ensuring a valid hierarchy.

    Validates the tree structure by checking:
        - Only one root exists.
        - All parent ids exist.
        - The hierarchy doesn't contain cycles.
    """
    tree = defaultdict(list)
    root = None
    existing_ids = {p["id"] for p in partners}

    for partner in partners:
        if partner["parent_id"] is None:
            if root is not None:
                raise MultipleRootsError
            root = partner["id"]
        else:
            if partner["parent_id"] not in existing_ids:
                raise ParentNotFoundError
            tree[partner["parent_id"]].append(partner["id"])
    if root is None:
        raise RootNotFoundError

    if detect_cycle(tree):
        raise CycleError

    return tree, root


def calculate_commissions(
    partners: list[Partner],
    days_in_month: int,
) -> dict[str, float]:
    """
    Calculates daily commissions for each partner in the MLM hierarchy.

    Each partner earns 5% commission on the daily revenue of all direct
    and indirect descendants. The revenue is assumed to be monthly and
    divided by a given `days_in_month`.
    """
    tree, root = build_partners_tree(partners=partners)
    daily_profits = {p["id"]: p["monthly_revenue"] / days_in_month for p in partners}
    commissions = {str(p["id"]): 0.0 for p in partners}

    def accumulate_profit(partner_id: int) -> float:
        total_profit = 0.0
        for child_id in tree.get(partner_id, []):
            total_profit += accumulate_profit(child_id) + daily_profits[child_id]
        commissions[str(partner_id)] = round(total_profit * COMMISSION_RATE, 2)
        return total_profit

    accumulate_profit(root)
    return commissions
