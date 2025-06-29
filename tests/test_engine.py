import pytest

from commission_engine import exceptions
from commission_engine.core import (
    COMMISSION_RATE,
    Partner,
    build_partners_tree,
    calculate_commissions,
    detect_cycle,
)


@pytest.fixture
def simple_partners():
    return [
        {"id": 1, "parent_id": None, "monthly_revenue": 2000},
        {"id": 2, "parent_id": 1, "monthly_revenue": 1000},
        {"id": 3, "parent_id": 1, "monthly_revenue": 1500},
        {"id": 4, "parent_id": 2, "monthly_revenue": 500},
    ]


@pytest.mark.parametrize(
    ("tree", "is_cyclic"),
    [
        ({1: [2], 2: []}, False),
        ({1: [2], 2: [1]}, True),
        ({1: [2], 2: [3, 4], 3: [], 4: []}, False),
        ({1: [2], 2: [3, 4], 3: [], 4: [1]}, True),
    ],
)
def test_cycle_detection(tree, is_cyclic):
    assert detect_cycle(tree) is is_cyclic


def test_build_tree_valid(simple_partners):
    tree, root = build_partners_tree(simple_partners)
    assert root == 1
    assert tree == {1: [2, 3], 2: [4]}


def test_build_tree_with_multiple_roots():
    partners: list[Partner] = [
        {"id": 1, "parent_id": None, "monthly_revenue": 1000},
        {"id": 2, "parent_id": None, "monthly_revenue": 1000},
    ]
    with pytest.raises(exceptions.MultipleRootsError):
        build_partners_tree(partners)


def test_build_tree_without_root():
    partners: list[Partner] = [
        {"id": 1, "parent_id": 2, "monthly_revenue": 1000},
        {"id": 2, "parent_id": 1, "monthly_revenue": 1000},
    ]
    with pytest.raises(exceptions.RootNotFoundError):
        build_partners_tree(partners)


def test_build_tree_with_nonexistent_parent():
    partners: list[Partner] = [
        {"id": 1, "parent_id": None, "monthly_revenue": 1000},
        {"id": 2, "parent_id": 10, "monthly_revenue": 1000},
    ]
    with pytest.raises(exceptions.ParentNotFoundError):
        build_partners_tree(partners)


def test_build_tree_with_cycle():
    partners = [
        {"id": 1, "parent_id": None, "monthly_revenue": 1000},
        {"id": 2, "parent_id": 4, "monthly_revenue": 1000},
        {"id": 3, "parent_id": 2, "monthly_revenue": 1000},
        {"id": 4, "parent_id": 3, "monthly_revenue": 1000},
    ]
    with pytest.raises(exceptions.CycleError):
        build_partners_tree(partners)


def test_commissions_structure(simple_partners):
    result = calculate_commissions(simple_partners, days_in_month=30)
    assert isinstance(result, dict)
    assert set(result) == {"1", "2", "3", "4"}


def test_commissions_values_accuracy(simple_partners):
    days = 30
    result = calculate_commissions(simple_partners, days)
    # monthly revenue: 2000, 1000, 1500, 500
    assert result["4"] == 0.0
    assert result["3"] == 0.0
    partner_2_comm = 500 / days * COMMISSION_RATE  # gain from partner 4
    assert result["2"] == round(partner_2_comm, 2)
    # gain from partner 2 and 3
    root_comm = (1000 / days + 1500 / days) * COMMISSION_RATE + partner_2_comm
    assert result["1"] == round(root_comm, 2)


def test_commissions_for_zero_revenue_partners():
    partners = [
        {"id": 1, "parent_id": None, "monthly_revenue": 0},
        {"id": 2, "parent_id": 1, "monthly_revenue": 0},
        {"id": 3, "parent_id": 1, "monthly_revenue": 0},
    ]
    result = calculate_commissions(partners, days_in_month=30)
    assert result == {"1": 0.0, "2": 0.0, "3": 0.0}


def test_commissions_for_single_partner():
    partners: list[Partner] = [{"id": 1, "parent_id": None, "monthly_revenue": 3000}]
    result = calculate_commissions(partners, days_in_month=30)
    assert result == {"1": 0.0}  # no children, no commission


def test_leaf_partner_has_no_commission():
    partners = [
        {"id": 1, "parent_id": None, "monthly_revenue": 1000},
        {"id": 2, "parent_id": 1, "monthly_revenue": 1000},
        {"id": 3, "parent_id": 2, "monthly_revenue": 1000},
    ]
    result = calculate_commissions(partners, days_in_month=30)
    assert result["3"] == 0.0


@pytest.mark.parametrize("level", [10, 15, 20])
def test_high_depth_partners_commissions(level):
    revenue, days = 1000, 30
    partners = []
    for i in range(1, level + 1):
        parent_id = i - 1 if i != 1 else None
        partners.append({"id": i, "parent_id": parent_id, "monthly_revenue": revenue})
    result = calculate_commissions(partners, days_in_month=days)
    expected = {}
    value = 0.0
    for i in range(level, 0, -1):
        expected[str(i)] = round(value, 2)
        value += revenue / days * COMMISSION_RATE
    assert result == expected
