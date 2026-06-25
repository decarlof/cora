"""Behavioural tests for the `DatasetDistributionLookup` test stubs (leg C, C1)."""

from uuid import uuid4

import pytest

from cora.infrastructure.ports.dataset_distribution_lookup import (
    DatasetDistributionLookupResult,
    NoDatasetDistributionsLookup,
    SeededDatasetDistributionLookup,
)

_DATASET_ID = uuid4()


@pytest.mark.unit
async def test_no_distributions_stub_returns_empty_for_any_dataset() -> None:
    lookup = NoDatasetDistributionsLookup()
    assert await lookup.find_by_dataset(_DATASET_ID) == ()


@pytest.mark.unit
async def test_seeded_stub_returns_the_configured_rows_for_a_dataset() -> None:
    verified = DatasetDistributionLookupResult(
        distribution_id=uuid4(), dataset_id=_DATASET_ID, supply_id=uuid4(), status="Verified"
    )
    lookup = SeededDatasetDistributionLookup({_DATASET_ID: (verified,)})
    assert await lookup.find_by_dataset(_DATASET_ID) == (verified,)


@pytest.mark.unit
async def test_seeded_stub_returns_empty_for_an_unmapped_dataset() -> None:
    lookup = SeededDatasetDistributionLookup({})
    assert await lookup.find_by_dataset(uuid4()) == ()
