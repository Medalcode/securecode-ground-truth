"""Benchmark result metadata model and validation."""

from dataclasses import dataclass
from datetime import datetime, timezone
import importlib.metadata
import json
import re
from typing import Any, Dict, Optional

DEFAULT_BENCHMARK_VERSION: str = "0.1.0"
SHA256_HEX_PATTERN = re.compile(r"^[a-fA-F0-9]{64}$")


def get_product_version(package_name: str = "securecode") -> str:
    """Retrieve installed SecureCode product version from package metadata."""
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError as e:
        raise RuntimeError(f"Package '{package_name}' is not installed") from e


@dataclass(frozen=True)
class ProductMetadata:
    """Metadata identifying the evaluated product (SecureCode)."""

    name: str
    version: str
    commit: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("product.name must be a non-empty string")
        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("product.version must be a non-empty string")
        if not isinstance(self.commit, str) or not self.commit.strip():
            raise ValueError("product.commit must be a non-empty string")

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "version": self.version,
            "commit": self.commit,
        }


@dataclass(frozen=True)
class BenchmarkMetadata:
    """Metadata identifying the benchmark implementation."""

    version: str
    commit: str

    def __post_init__(self) -> None:
        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("benchmark.version must be a non-empty string")
        if not isinstance(self.commit, str) or not self.commit.strip():
            raise ValueError("benchmark.commit must be a non-empty string")

    def to_dict(self) -> Dict[str, str]:
        return {
            "version": self.version,
            "commit": self.commit,
        }


@dataclass(frozen=True)
class GroundTruthMetadata:
    """Metadata identifying the Ground Truth dataset and evidence."""

    schema_version: str
    dataset_sha256: str
    case_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.schema_version, str) or not self.schema_version.strip():
            raise ValueError("ground_truth.schema_version must be a non-empty string")
        if not isinstance(self.dataset_sha256, str) or not SHA256_HEX_PATTERN.fullmatch(self.dataset_sha256):
            raise ValueError("ground_truth.dataset_sha256 must be a 64-character hexadecimal SHA-256 string")
        if not isinstance(self.case_count, int) or isinstance(self.case_count, bool) or self.case_count < 0:
            raise ValueError("ground_truth.case_count must be a non-negative integer")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "dataset_sha256": self.dataset_sha256,
            "case_count": self.case_count,
        }


@dataclass(frozen=True)
class ExecutionMetadata:
    """Top-level metadata identifying a single benchmark execution."""

    execution_id: str
    execution_timestamp: str
    control: str
    product: ProductMetadata
    benchmark: BenchmarkMetadata
    ground_truth: GroundTruthMetadata

    def __post_init__(self) -> None:
        if not isinstance(self.execution_id, str) or not self.execution_id.strip():
            raise ValueError("execution_id must be a non-empty string")
        if not isinstance(self.control, str) or not self.control.strip():
            raise ValueError("control must be a non-empty string")

        if not isinstance(self.product, ProductMetadata):
            raise TypeError(f"product must be an instance of ProductMetadata, got {type(self.product).__name__}")
        if not isinstance(self.benchmark, BenchmarkMetadata):
            raise TypeError(f"benchmark must be an instance of BenchmarkMetadata, got {type(self.benchmark).__name__}")
        if not isinstance(self.ground_truth, GroundTruthMetadata):
            raise TypeError(
                f"ground_truth must be an instance of GroundTruthMetadata, got {type(self.ground_truth).__name__}"
            )

        if not isinstance(self.execution_timestamp, str) or not self.execution_timestamp.strip():
            raise ValueError("execution_timestamp must be a non-empty string")

        # Validate UTC ISO-8601 format
        if not (self.execution_timestamp.endswith("Z") or self.execution_timestamp.endswith("+00:00")):
            raise ValueError(
                f"execution_timestamp must be a UTC ISO-8601 string ending with 'Z' or '+00:00', got: {self.execution_timestamp}"
            )
        try:
            norm_ts = (
                self.execution_timestamp[:-1] + "+00:00"
                if self.execution_timestamp.endswith("Z")
                else self.execution_timestamp
            )
            parsed = datetime.fromisoformat(norm_ts)
            if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(None):
                raise ValueError("execution_timestamp must have zero UTC offset")
        except Exception as e:
            raise ValueError(f"Invalid ISO-8601 execution_timestamp '{self.execution_timestamp}': {e}") from e

    def to_dict(self) -> Dict[str, Any]:
        """Serialize metadata to a dictionary matching the approved specification."""
        return {
            "execution_id": self.execution_id,
            "execution_timestamp": self.execution_timestamp,
            "control": self.control,
            "product": self.product.to_dict(),
            "benchmark": self.benchmark.to_dict(),
            "ground_truth": self.ground_truth.to_dict(),
        }

    def to_json(self, indent: Optional[int] = 2) -> str:
        """Serialize metadata to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionMetadata":
        """Deserialize and validate metadata from a dictionary."""
        if not isinstance(data, dict):
            raise TypeError("Metadata input must be a dictionary")

        required_keys = ("execution_id", "execution_timestamp", "control", "product", "benchmark", "ground_truth")
        for key in required_keys:
            if key not in data:
                raise KeyError(f"Missing required top-level key: '{key}'")

        prod_data = data["product"]
        if not isinstance(prod_data, dict):
            raise TypeError("product must be a dictionary")
        for key in ("name", "version", "commit"):
            if key not in prod_data:
                raise KeyError(f"Missing required product key: '{key}'")

        bench_data = data["benchmark"]
        if not isinstance(bench_data, dict):
            raise TypeError("benchmark must be a dictionary")
        for key in ("version", "commit"):
            if key not in bench_data:
                raise KeyError(f"Missing required benchmark key: '{key}'")

        gt_data = data["ground_truth"]
        if not isinstance(gt_data, dict):
            raise TypeError("ground_truth must be a dictionary")
        for key in ("schema_version", "dataset_sha256", "case_count"):
            if key not in gt_data:
                raise KeyError(f"Missing required ground_truth key: '{key}'")

        return cls(
            execution_id=data["execution_id"],
            execution_timestamp=data["execution_timestamp"],
            control=data["control"],
            product=ProductMetadata(
                name=prod_data["name"],
                version=prod_data["version"],
                commit=prod_data["commit"],
            ),
            benchmark=BenchmarkMetadata(
                version=bench_data["version"],
                commit=bench_data["commit"],
            ),
            ground_truth=GroundTruthMetadata(
                schema_version=gt_data["schema_version"],
                dataset_sha256=gt_data["dataset_sha256"],
                case_count=gt_data["case_count"],
            ),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "ExecutionMetadata":
        """Deserialize and validate metadata from a JSON string."""
        if not isinstance(json_str, str):
            raise TypeError("JSON input must be a string")
        data = json.loads(json_str)
        return cls.from_dict(data)
