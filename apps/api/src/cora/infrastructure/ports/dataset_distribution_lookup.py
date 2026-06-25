"""DatasetDistributionLookup port: cross-BC query for a Dataset's Distributions.

Used by the Run BC start_run gate (leg C of stage-then-reconstruct) to check
that a reconstruction's input Dataset has a Verified Distribution before the Run
may start ([[project_run_input_dependency_design]]). Cross-BC mirror of
`SupplyLookup` / `ClearanceLookup`: one implementor (Data BC ships the Postgres
adapter reading `proj_data_distribution_summary`), multiple consumers (the Run
start gate first). It lives in `cora.infrastructure.ports` because Run may not
import the Data-internal `cora.data.ports.DistributionLookup` (that one is the
Edition-shaped lowest-id canonical pick, a different need).

## Decider-gates, not port-gates

Returns EVERY non-Discarded Distribution for the Dataset regardless of status,
so the start_run decider can both gate on Verified AND produce a useful
diagnostic ("the input has a Distribution but it is Stale" vs "no Distribution
at all"). This is the `SupplyLookup` posture: the port returns rows, the decider
partitions on `status`. It deliberately does NOT reuse the canonical-pick query,
whose lowest-id row may be Stale while a higher-id Distribution is Verified.

`status` is the `DistributionStatus` value as a plain string (matches the
projection's TEXT column); `supply_id` is carried for the deferred reachability
check (which Storage Supply / tier the copy rests on); `distribution_id` is
carried for diagnostics and the eventual lineage record.
"""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class DatasetDistributionLookupResult:
    """A non-Discarded Distribution of a Dataset, for the Run-start input gate."""

    distribution_id: UUID
    dataset_id: UUID
    supply_id: UUID
    status: str


class DatasetDistributionLookup(Protocol):
    """Cross-BC port: query a Dataset's non-Discarded Distributions from the Run BC."""

    async def find_by_dataset(
        self, dataset_id: UUID
    ) -> tuple[DatasetDistributionLookupResult, ...]:
        """Return every non-Discarded Distribution for `dataset_id` (any status).

        Empty tuple when the Dataset has no non-Discarded Distribution. The
        decider gates on `status == "Verified"`; the port does not filter on
        status so the decider can distinguish Stale from absent.
        """
        ...


class NoDatasetDistributionsLookup:
    """Test stub: every Dataset has no Distribution (the not-present gate path).

    The conservative default for tests that do not seed the input gate: the
    start_run decider sees an input with no Verified Distribution and raises.
    """

    async def find_by_dataset(
        self, dataset_id: UUID
    ) -> tuple[DatasetDistributionLookupResult, ...]:
        _ = dataset_id
        return ()


class SeededDatasetDistributionLookup:
    """Test stub: returns the Distributions configured per Dataset id.

    Construct with a mapping `{dataset_id: (result, ...)}`; an unmapped Dataset
    returns an empty tuple (absent). Lets a gate test seed a Verified row, a
    Stale-only row, or no row to exercise each decider branch.
    """

    def __init__(self, by_dataset: dict[UUID, tuple[DatasetDistributionLookupResult, ...]]) -> None:
        self._by_dataset = dict(by_dataset)

    async def find_by_dataset(
        self, dataset_id: UUID
    ) -> tuple[DatasetDistributionLookupResult, ...]:
        return self._by_dataset.get(dataset_id, ())


__all__ = [
    "DatasetDistributionLookup",
    "DatasetDistributionLookupResult",
    "NoDatasetDistributionsLookup",
    "SeededDatasetDistributionLookup",
]
