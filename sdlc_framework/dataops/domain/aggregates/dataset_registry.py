"""Dataset Registry aggregate root."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from ..entities import Dataset, DatasetTemplate
from ..types import DatasetType, DatasetStatus, Stage


@dataclass
class DatasetRegistry:
    """Aggregate root for the DatasetRegistry bounded context.

    Enforces invariants:
    - Only one active dataset per client/stage/type
    - Connector names must be unique across all stages
    - Archived datasets are immutable

    Business rules:
    - Stage transition triggers teardown of previous stage datasets
    - Quality threshold (95%) required for READY status
    - Connector health monitoring reverts READY to VALIDATING on failure
    """

    registry_id: UUID = field(default_factory=uuid4)
    registry_version: str = "1.0.0"
    last_updated: datetime = field(default_factory=datetime.utcnow)
    total_datasets: int = 0
    datasets: Dict[UUID, Dataset] = field(default_factory=dict)
    templates: Dict[UUID, DatasetTemplate] = field(default_factory=dict)
    _connector_names: set = field(default_factory=set, init=False, repr=False)

    def register_template(self, template: DatasetTemplate) -> None:
        """Register a new dataset template in the catalog."""
        if template.template_id in self.templates:
            raise ValueError(
                f"Template {template.template_id} already registered"
            )

        self.templates[template.template_id] = template
        self.last_updated = datetime.utcnow()

    def find_template(
        self,
        industry: str = None,
        use_case: str = None,
        dataset_type: DatasetType = None
    ) -> List[DatasetTemplate]:
        """Find templates matching criteria."""
        matches = []
        for template in self.templates.values():
            if template.matches_criteria(industry, use_case, dataset_type):
                matches.append(template)
        return matches

    def register_dataset(self, dataset: Dataset) -> None:
        """Register a new dataset, enforcing uniqueness invariant.

        Raises:
            ValueError: If active dataset already exists for client/stage/type
        """
        # Check uniqueness invariant
        existing = self._find_active_dataset(
            dataset.client_id,
            dataset.stage,
            dataset.dataset_type
        )

        if existing:
            raise ValueError(
                f"Active dataset already exists for client {dataset.client_id}, "
                f"stage {dataset.stage.value}, type {dataset.dataset_type.value}: "
                f"{existing.dataset_id}"
            )

        # Check connector name uniqueness
        if dataset.name in self._connector_names:
            raise ValueError(
                f"Dataset name '{dataset.name}' already in use. "
                "Connector names must be unique across all stages."
            )

        self.datasets[dataset.dataset_id] = dataset
        self._connector_names.add(dataset.name)
        self.total_datasets += 1
        self.last_updated = datetime.utcnow()

    def get_dataset(self, dataset_id: UUID) -> Optional[Dataset]:
        """Retrieve dataset by ID."""
        return self.datasets.get(dataset_id)

    def find_datasets_by_client(
        self,
        client_id: UUID,
        stage: Optional[Stage] = None,
        status: Optional[DatasetStatus] = None
    ) -> List[Dataset]:
        """Find all datasets for a client, optionally filtered by stage/status."""
        results = []
        for dataset in self.datasets.values():
            if dataset.client_id != client_id:
                continue

            if stage and dataset.stage != stage:
                continue

            if status and dataset.status != status:
                continue

            results.append(dataset)

        return results

    def find_datasets_by_journey(self, journey_id: UUID) -> List[Dataset]:
        """Find all datasets for a journey."""
        return [
            dataset for dataset in self.datasets.values()
            if dataset.journey_id == journey_id
        ]

    def teardown_stage_datasets(
        self,
        client_id: UUID,
        stage: Stage
    ) -> List[Dataset]:
        """Teardown all active datasets for a client stage.

        Called when journey transitions to new stage.

        Returns:
            List of datasets transitioned to TEARDOWN status
        """
        datasets_to_teardown = self.find_datasets_by_client(
            client_id,
            stage=stage,
            status=DatasetStatus.READY
        )

        torn_down = []
        for dataset in datasets_to_teardown:
            dataset.start_teardown()
            torn_down.append(dataset)

        if torn_down:
            self.last_updated = datetime.utcnow()

        return torn_down

    def _find_active_dataset(
        self,
        client_id: UUID,
        stage: Stage,
        dataset_type: DatasetType
    ) -> Optional[Dataset]:
        """Find active dataset for client/stage/type (enforces uniqueness)."""
        for dataset in self.datasets.values():
            if dataset.client_id != client_id:
                continue
            if dataset.stage != stage:
                continue
            if dataset.dataset_type != dataset_type:
                continue
            if dataset.status in [DatasetStatus.ARCHIVED, DatasetStatus.FAILED]:
                continue

            return dataset

        return None

    def validate_registry_invariants(self) -> List[str]:
        """Validate all registry-level invariants.

        Returns:
            List of invariant violations (empty if all valid)
        """
        violations = []

        # Check dataset uniqueness
        active_keys = set()
        for dataset in self.datasets.values():
            if dataset.status in [DatasetStatus.ARCHIVED, DatasetStatus.FAILED]:
                continue

            key = (dataset.client_id, dataset.stage, dataset.dataset_type)
            if key in active_keys:
                violations.append(
                    f"Multiple active datasets for {key}: violates uniqueness invariant"
                )
            active_keys.add(key)

        # Check connector name uniqueness
        connector_names = {}
        for dataset in self.datasets.values():
            if dataset.name in connector_names:
                violations.append(
                    f"Duplicate connector name '{dataset.name}' in datasets "
                    f"{connector_names[dataset.name]} and {dataset.dataset_id}"
                )
            connector_names[dataset.name] = dataset.dataset_id

        # Validate each dataset's invariants
        for dataset in self.datasets.values():
            dataset_violations = dataset.validate_invariants()
            violations.extend(dataset_violations)

        return violations

    def __str__(self) -> str:
        """Human-readable representation."""
        active_count = len([
            d for d in self.datasets.values()
            if d.status not in [DatasetStatus.ARCHIVED, DatasetStatus.FAILED]
        ])
        return (
            f"DatasetRegistry v{self.registry_version}: "
            f"{active_count} active / {self.total_datasets} total datasets, "
            f"{len(self.templates)} templates"
        )
