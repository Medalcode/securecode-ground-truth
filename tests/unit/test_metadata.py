"""Unit tests for benchmark result metadata models."""

import json
import pytest

from benchmark.metadata import (
    DEFAULT_BENCHMARK_VERSION,
    BenchmarkMetadata,
    ExecutionMetadata,
    GroundTruthMetadata,
    ProductMetadata,
    get_product_version,
)


def _create_valid_metadata() -> ExecutionMetadata:
    return ExecutionMetadata(
        execution_id="exec_GH-001_20260916T220500Z",
        execution_timestamp="2026-09-16T22:05:00Z",
        control="GH-001",
        product=ProductMetadata(
            name="securecode",
            version="0.1.0",
            commit="a6d9f2d4b1d0df4f7d382f127f82aa64524110d5",
        ),
        benchmark=BenchmarkMetadata(
            version=DEFAULT_BENCHMARK_VERSION,
            commit="6a0fcc248dcb8e80ceb393106999c25fba4f2d91",
        ),
        ground_truth=GroundTruthMetadata(
            schema_version="1.0",
            dataset_sha256="7418F0DA8B8F55DA1123068756650434B0EC03E20D575FBA1C01E6663656832B",
            case_count=6,
        ),
    )


def test_valid_metadata_creation():
    """Verify that a complete, valid metadata hierarchy instantiates with expected attributes."""
    meta = _create_valid_metadata()
    assert meta.execution_id == "exec_GH-001_20260916T220500Z"
    assert meta.execution_timestamp == "2026-09-16T22:05:00Z"
    assert meta.control == "GH-001"
    assert meta.product.name == "securecode"
    assert meta.product.version == "0.1.0"
    assert meta.product.commit == "a6d9f2d4b1d0df4f7d382f127f82aa64524110d5"
    assert meta.benchmark.version == "0.1.0"
    assert meta.benchmark.commit == "6a0fcc248dcb8e80ceb393106999c25fba4f2d91"
    assert meta.ground_truth.schema_version == "1.0"
    assert meta.ground_truth.dataset_sha256 == "7418F0DA8B8F55DA1123068756650434B0EC03E20D575FBA1C01E6663656832B"
    assert meta.ground_truth.case_count == 6


def test_metadata_serialization_and_roundtrip():
    """Verify serialization to dict / JSON and lossless deserialization roundtrip."""
    meta = _create_valid_metadata()
    data = meta.to_dict()

    # Verify top-level and nested structure
    assert data["execution_id"] == meta.execution_id
    assert data["execution_timestamp"] == meta.execution_timestamp
    assert data["control"] == meta.control
    assert data["product"]["name"] == "securecode"
    assert data["product"]["version"] == "0.1.0"
    assert data["product"]["commit"] == meta.product.commit
    assert data["benchmark"]["version"] == "0.1.0"
    assert data["benchmark"]["commit"] == meta.benchmark.commit
    assert data["ground_truth"]["schema_version"] == "1.0"
    assert data["ground_truth"]["dataset_sha256"] == meta.ground_truth.dataset_sha256
    assert data["ground_truth"]["case_count"] == 6

    # Test JSON serialization
    json_str = meta.to_json()
    assert isinstance(json_str, str)
    parsed_json = json.loads(json_str)
    assert parsed_json == data

    # Test deserialization roundtrips
    reconstructed_from_dict = ExecutionMetadata.from_dict(data)
    assert reconstructed_from_dict == meta

    reconstructed_from_json = ExecutionMetadata.from_json(json_str)
    assert reconstructed_from_json == meta


def test_get_product_version_from_installed_package():
    """Verify that product version is resolved from importlib metadata without product code modification."""
    version = get_product_version("securecode")
    assert version == "0.1.0"

    with pytest.raises(RuntimeError, match="not installed"):
        get_product_version("non_existent_package_xyz")


def test_required_fields_cannot_silently_disappear():
    """Verify that omitting required keys raises KeyError during deserialization."""
    valid_data = _create_valid_metadata().to_dict()

    # Missing top-level key
    for key in ("execution_id", "execution_timestamp", "control", "product", "benchmark", "ground_truth"):
        corrupt = valid_data.copy()
        del corrupt[key]
        with pytest.raises(KeyError, match=f"Missing required top-level key: '{key}'"):
            ExecutionMetadata.from_dict(corrupt)

    # Missing nested product key
    for key in ("name", "version", "commit"):
        corrupt = json.loads(json.dumps(valid_data))
        del corrupt["product"][key]
        with pytest.raises(KeyError, match=f"Missing required product key: '{key}'"):
            ExecutionMetadata.from_dict(corrupt)

    # Missing nested benchmark key
    for key in ("version", "commit"):
        corrupt = json.loads(json.dumps(valid_data))
        del corrupt["benchmark"][key]
        with pytest.raises(KeyError, match=f"Missing required benchmark key: '{key}'"):
            ExecutionMetadata.from_dict(corrupt)

    # Missing nested ground_truth key
    for key in ("schema_version", "dataset_sha256", "case_count"):
        corrupt = json.loads(json.dumps(valid_data))
        del corrupt["ground_truth"][key]
        with pytest.raises(KeyError, match=f"Missing required ground_truth key: '{key}'"):
            ExecutionMetadata.from_dict(corrupt)


def test_nested_metadata_type_integrity():
    """Verify that non-dict or wrong types for nested metadata are rejected."""
    valid_data = _create_valid_metadata().to_dict()

    corrupt = valid_data.copy()
    corrupt["product"] = "not_a_dict"
    with pytest.raises(TypeError, match="product must be a dictionary"):
        ExecutionMetadata.from_dict(corrupt)

    corrupt = valid_data.copy()
    corrupt["benchmark"] = 123
    with pytest.raises(TypeError, match="benchmark must be a dictionary"):
        ExecutionMetadata.from_dict(corrupt)

    corrupt = valid_data.copy()
    corrupt["ground_truth"] = None
    with pytest.raises(TypeError, match="ground_truth must be a dictionary"):
        ExecutionMetadata.from_dict(corrupt)


def test_timestamp_validation():
    """Verify that timestamp must follow ISO-8601 UTC format strictly."""
    base = _create_valid_metadata()

    # Valid UTC endings
    ExecutionMetadata(
        execution_id=base.execution_id,
        execution_timestamp="2026-09-16T22:05:00+00:00",
        control=base.control,
        product=base.product,
        benchmark=base.benchmark,
        ground_truth=base.ground_truth,
    )

    # Invalid timestamp format (missing timezone)
    with pytest.raises(ValueError, match="UTC ISO-8601"):
        ExecutionMetadata(
            execution_id=base.execution_id,
            execution_timestamp="2026-09-16T22:05:00",
            control=base.control,
            product=base.product,
            benchmark=base.benchmark,
            ground_truth=base.ground_truth,
        )

    # Invalid timestamp format (non-UTC offset)
    with pytest.raises(ValueError, match="UTC ISO-8601"):
        ExecutionMetadata(
            execution_id=base.execution_id,
            execution_timestamp="2026-09-16T22:05:00+02:00",
            control=base.control,
            product=base.product,
            benchmark=base.benchmark,
            ground_truth=base.ground_truth,
        )

    # Completely malformed timestamp string
    with pytest.raises(ValueError, match="UTC ISO-8601"):
        ExecutionMetadata(
            execution_id=base.execution_id,
            execution_timestamp="not_a_timestamp",
            control=base.control,
            product=base.product,
            benchmark=base.benchmark,
            ground_truth=base.ground_truth,
        )


def test_dataset_hash_validation():
    """Verify that dataset_sha256 must be an exact 64-character hex string."""
    # Valid uppercase & lowercase 64-char hex strings
    GroundTruthMetadata(
        schema_version="1.0",
        dataset_sha256="7418f0da8b8f55da1123068756650434b0ec03e20d575fba1c01e6663656832b",
        case_count=6,
    )

    # Too short (63 chars)
    with pytest.raises(ValueError, match="64-character hexadecimal"):
        GroundTruthMetadata(
            schema_version="1.0",
            dataset_sha256="7418F0DA8B8F55DA1123068756650434B0EC03E20D575FBA1C01E6663656832",
            case_count=6,
        )

    # Too long (65 chars)
    with pytest.raises(ValueError, match="64-character hexadecimal"):
        GroundTruthMetadata(
            schema_version="1.0",
            dataset_sha256="7418F0DA8B8F55DA1123068756650434B0EC03E20D575FBA1C01E6663656832BA",
            case_count=6,
        )

    # Non-hex characters
    with pytest.raises(ValueError, match="64-character hexadecimal"):
        GroundTruthMetadata(
            schema_version="1.0",
            dataset_sha256="Z418F0DA8B8F55DA1123068756650434B0EC03E20D575FBA1C01E6663656832B",
            case_count=6,
        )


def test_case_count_validation():
    """Verify that case_count must be a non-negative integer."""
    # Valid counts
    GroundTruthMetadata(
        schema_version="1.0",
        dataset_sha256="7418F0DA8B8F55DA1123068756650434B0EC03E20D575FBA1C01E6663656832B",
        case_count=0,
    )

    # Negative count
    with pytest.raises(ValueError, match="non-negative integer"):
        GroundTruthMetadata(
            schema_version="1.0",
            dataset_sha256="7418F0DA8B8F55DA1123068756650434B0EC03E20D575FBA1C01E6663656832B",
            case_count=-1,
        )

    # Boolean rejected even though bool is a subclass of int in Python
    with pytest.raises(ValueError, match="non-negative integer"):
        GroundTruthMetadata(
            schema_version="1.0",
            dataset_sha256="7418F0DA8B8F55DA1123068756650434B0EC03E20D575FBA1C01E6663656832B",
            case_count=True,
        )

    # Non-integer (float)
    with pytest.raises(ValueError, match="non-negative integer"):
        GroundTruthMetadata(
            schema_version="1.0",
            dataset_sha256="7418F0DA8B8F55DA1123068756650434B0EC03E20D575FBA1C01E6663656832B",
            case_count=6.5,
        )


def test_commit_and_control_validation():
    """Verify validation of commit identifiers and control code."""
    # Empty product commit
    with pytest.raises(ValueError, match="product.commit"):
        ProductMetadata(name="securecode", version="0.1.0", commit="")

    # Empty benchmark commit
    with pytest.raises(ValueError, match="benchmark.commit"):
        BenchmarkMetadata(version="0.1.0", commit="   ")

    # Empty control
    base = _create_valid_metadata()
    with pytest.raises(ValueError, match="control must be a non-empty string"):
        ExecutionMetadata(
            execution_id=base.execution_id,
            execution_timestamp=base.execution_timestamp,
            control="",
            product=base.product,
            benchmark=base.benchmark,
            ground_truth=base.ground_truth,
        )
