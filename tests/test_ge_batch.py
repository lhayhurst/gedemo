import datetime
import os
import shutil
from pathlib import Path
from uuid import uuid4

import pytest
from great_expectations.core import ExpectationSuite
from great_expectations.core.batch import BatchRequest, Batch
from great_expectations.datasource import Datasource
from great_expectations.exceptions import ConfigNotFoundError
from great_expectations.validation_operators.types.validation_operator_result import ValidationOperatorResult
from great_expectations.validator.validator import Validator

from great_expectations import DataContext


@pytest.fixture
def ge_dir(tmp_path):
    cwd = os.getcwd()
    script_dir = Path(__file__).parent
    src_ge_dir = script_dir / "great_expectations"
    target_ge_dir = tmp_path / "great_expectations"
    shutil.copytree(str(src_ge_dir), str(target_ge_dir))
    os.chdir(str(tmp_path))
    yield target_ge_dir
    os.chdir(cwd)


@pytest.fixture
def ge_context_yaml_config() -> str:
    base_dir = Path(__file__).parent.parent / "data"
    yaml_config = rf"""
    class_name: Datasource
    execution_engine:
      class_name: PandasExecutionEngine
    data_connectors:
      my_filesystem_data_connector:
        class_name: InferredAssetFilesystemDataConnector
        datasource_name: gedemo_datasource
        base_directory: {base_dir}
        default_regex:
          group_names:
            - data_asset_name
            - eco_letter
            - file_extension
          pattern: (.*)-(\w)\.(csv)
        """

    return yaml_config


def test_data_context_raises_without_initialized_ge_directory():
    with pytest.raises(ConfigNotFoundError, match="No great_expectations directory was found here"):
        DataContext()


def test_data_context(ge_dir: Path, ge_context_yaml_config: str):
    ge_data_context: DataContext = DataContext()
    datasource_name = "gedemo_datasource"
    dataconnector_name = "my_filesystem_data_connector"
    expectation_suite_name = "chess"
    data_asset_name = "eco"

    ge_data_context.test_yaml_config(name=datasource_name, yaml_config=ge_context_yaml_config)

    datasources = ge_data_context.list_datasources()
    assert len(datasources) == 1

    data_source: Datasource = ge_data_context.get_datasource(datasource_name)
    assert data_source.get_available_data_asset_names() == {dataconnector_name: ["eco"]}

    expectation_suite: ExpectationSuite = ge_data_context.get_expectation_suite(expectation_suite_name)

    for letter in ['A', 'B', 'C', 'D', 'E']:

        batch_request: BatchRequest = BatchRequest(
            datasource_name=datasource_name,
            data_connector_name=dataconnector_name,
            data_asset_name=data_asset_name,
            data_connector_query={
                "batch_filter_parameters": {
                    "eco_letter": letter,
                }
            },
        )

        ge_validator: Validator = ge_data_context.get_validator(
            batch_request=batch_request, expectation_suite=expectation_suite
        )

        active_batch: Batch = ge_validator.active_batch

        assert not active_batch.head().empty  # for show :-)

        # run it
        run_id = {
            "run_name": str(uuid4()),  # insert your own run_name here
            "run_time": datetime.datetime.now(datetime.timezone.utc)
        }

        results: ValidationOperatorResult = ge_data_context.run_validation_operator(
            "action_list_operator",
            assets_to_validate=[ge_validator],
            run_id=run_id)

        assert not results.success  # there are players with elo > 2000

    # TODO: generate docs

