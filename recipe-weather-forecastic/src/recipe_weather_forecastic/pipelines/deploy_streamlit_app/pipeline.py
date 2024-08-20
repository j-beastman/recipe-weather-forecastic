# Copyright 2024 DataRobot, Inc. and its affiliates.
# All rights reserved.
# DataRobot, Inc.
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
# Released under the terms of DataRobot Tool and Utility Agreement.

from kedro.pipeline import node, Pipeline
from kedro.pipeline.modular_pipeline import pipeline
from datarobotx.idp.use_cases import get_or_create_use_case
from datarobotx.idp.custom_applications import get_replace_or_create_custom_app

# from datarobotx.idp.execution_environments import get_or_create_execution_environment
from datarobotx.idp.custom_application_source import (
    get_or_create_custom_application_source,
)

from .nodes import (
    log_outputs,
    prepare_yaml_content,
    make_app_assets,
    get_or_create_custom_application_source_version_with_secrets,
    get_dataset_id,
)


def create_pipeline(**kwargs) -> Pipeline:
    nodes = [
        node(
            name="make_datarobot_use_case",
            func=get_or_create_use_case,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "name": "params:use_case.name",
            },
            outputs="use_case_id",
        ),
        node(
            name="make_app_execution_environment",
            func=get_or_create_custom_application_source,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "name": "params:environment_name",
                # "use_cases": "params:environment_use_cases",
            },
            outputs="custom_application_source_id",
        ),
        node(
            name="get_prediction_dataset_id",
            func=get_dataset_id,
            inputs={
                "dataset_name": "params:prediction_dataset_name",
                "use_case_id": "use_case_id",
            },
            outputs="prediction_data_id",
        ),
        node(
            name="make_app_execution_environment_version",
            func=get_or_create_custom_application_source_version_with_secrets,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "azure_endpoint": "params:credentials.azure_openai_llm_credentials.azure_endpoint",
                "azure_api_key": "params:credentials.azure_openai_llm_credentials.api_key",
                "azure_api_version": "params:credentials.azure_openai_llm_credentials.api_version",
                "custom_application_source_id": "custom_application_source_id",
                "base_environment_id": "params:base_environment_id",
                "secrets_template": "app_secrets",
                "app_assets": "app_assets",
            },
            outputs="custom_application_source_version_id",
        ),
        node(
            name="deploy_app",
            func=get_replace_or_create_custom_app,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "name": "params:custom_app_name",
                "custom_application_source_version_id": "custom_application_source_version_id",
            },
            outputs="application_id",
        ),
        node(
            name="log_outputs",
            func=log_outputs,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "project_id": "project_id",
                "model_id": "recommended_model_id",
                "deployment_id": "deployment_id",
                "application_id": "application_id",
                "project_name": "params:project.name",
                "deployment_name": "params:deployment.label",
                "app_name": "params:custom_app_name",
            },
            outputs=None,
        ),
        node(
            name="make_app_parameters",
            func=prepare_yaml_content,
            inputs={
                "deployment_id": "deployment_id",
                "page_title": "params:page_title",
                "graph_y_axis": "params:graph_y_axis",
                "lower_bound_forecast_at_0": "params:lower_bound_forecast_at_0",
                "headline_prompt": "params:headline.prompt",
                "headline_temperature": "params:headline.temperature",
                "analysis_temperature": "params:analysis.temperature",
                "model_name": "params:credentials.azure_openai_llm_credentials.deployment_name",
                "target": "params:project.analyze_and_model_config.target",
                "datetime_partition_column": "params:project.datetime_partitioning_config.datetime_partition_column",
                "multiseries_id_column": "params:project.datetime_partitioning_config.multiseries_id_columns",
                "prediction_interval": "params:deployment.prediction_interval",
                "scoring_data": "prediction_data_id",
            },
            outputs="app_parameters",
        ),
        node(
            name="make_app_assets",
            func=make_app_assets,
            inputs={
                "folder_path": "folder_path",
                "app_parameters_yaml": "app_parameters",
            },
            outputs="app_assets",
        ),
        # node(
        #     name="make_app_assets",
        #     func=make_app_assets,
        #     inputs={
        #         "app_py": "app_code",
        #         "helpers_py": "app_helpers",
        #         "app_parameters_yml": "app_parameters",
        #         "requirements": "app_requirements",
        #         "dockerfile": "app_dockerfile",
        #         "logo": "app_logo",
        #         "style_css": "app_style",
        #         "config_toml": "app_config",
        #         "secrets_toml": "app_secrets",
        #     },
        #     outputs="app_assets",
        # ),
    ]
    pipeline_inst = pipeline(nodes)
    return pipeline(
        pipeline_inst,
        namespace="deploy_streamlit_app",
        parameters={
            "params:credentials.datarobot.endpoint": "params:credentials.datarobot.endpoint",
            "params:credentials.datarobot.api_token": "params:credentials.datarobot.api_token",
            "params:credentials.azure_openai_llm_credentials.azure_endpoint": "params:credentials.azure_openai_llm_credentials.azure_endpoint",
            "params:credentials.azure_openai_llm_credentials.api_key": "params:credentials.azure_openai_llm_credentials.api_key",
            "params:credentials.azure_openai_llm_credentials.api_version": "params:credentials.azure_openai_llm_credentials.api_version",
            "params:credentials.azure_openai_llm_credentials.deployment_name": "params:credentials.azure_openai_llm_credentials.deployment_name",
            "params:project.name": "params:deploy_forecast.project.name",
            "params:project.analyze_and_model_config.target": "params:deploy_forecast.project.analyze_and_model_config.target",
            "params:project.datetime_partitioning_config.multiseries_id_columns": "params:deploy_forecast.project.datetime_partitioning_config.multiseries_id_columns",
            "params:project.datetime_partitioning_config.datetime_partition_column": "params:deploy_forecast.project.datetime_partitioning_config.datetime_partition_column",
            "params:deployment.label": "params:deploy_forecast.deployment.label",
            "params:deployment.prediction_interval": "params:deploy_forecast.deployment.prediction_interval",
            "params:use_case.name": "params:setup.use_case.name",
        },
        inputs={
            "project_id",
            "recommended_model_id",
            "deployment_id",
        },
        outputs={"application_id", "custom_application_source_version_id"},
    )
