# Copyright 2024 DataRobot, Inc. and its affiliates.
# All rights reserved.
# DataRobot, Inc.
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
# Released under the terms of DataRobot Tool and Utility Agreement.

from kedro.pipeline import node, Pipeline
from kedro.pipeline.modular_pipeline import pipeline

import datarobot as dr
from datarobotx.idp.autopilot import get_or_create_autopilot_run
from datarobotx.idp.deployments import (
    get_replace_or_create_deployment_from_registered_model,
)

from datarobotx.idp.registered_model_versions import (
    get_or_create_registered_leaderboard_model_version,
)
from datarobotx.idp.retraining_policies import get_update_or_create_retraining_policy

from .nodes import (
    ensure_deployment_settings,
    put_forecast_distance_into_registered_model_name,
    find_existing_dataset,
    get_date_format,
    setup_batch_prediction_job_definition,
)


def create_pipeline(**kwargs) -> Pipeline:
    nodes = [
        node(
            name="get_modeling_dataset_id",
            func=find_existing_dataset,
            inputs={"dataset_name": "params:dataset_name", "use_cases": "use_case_id"},
            outputs="preprocessed_timeseries_data_id",
        ),
        # node(
        #     name="set_known_in_advance",
        #     func=set_known_in_advance_features,
        #     inputs={
        #         "known_in_advance": "params:project.known_in_advance",
        #         "not_known_in_advance": "params:project.not_known_in_advance",
        #         "existing_datetime_partitioning_config": "params:project.datetime_partitioning_config"
        #     },
        #     outputs="updated_datetime_partitioning_config"
        # ),
        node(
            name="make_autopilot_run",
            func=get_or_create_autopilot_run,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "name": "params:project.name",
                "dataset_id": "preprocessed_timeseries_data_id",
                "analyze_and_model_config": "params:project.analyze_and_model_config",
                "datetime_partitioning_config": "params:project.datetime_partitioning_config",
                # "feature_settings_config": "params:project.feature_settings_config",
                "advanced_options_config": "params:project.advanced_options_config",
                "use_case": "use_case_id",
            },
            outputs="project_id",
        ),
        node(
            name="get_recommended_model",
            func=lambda project_id: dr.Project.get(project_id).get_top_model().id,
            inputs="project_id",
            outputs="recommended_model_id",
        ),
        node(
            name="make_registered_model_name",
            func=put_forecast_distance_into_registered_model_name,
            inputs={
                "registered_model_name": "params:registered_model.name",
                "forecast_window_start": "params:project.datetime_partitioning_config.forecast_window_start",
                "forecast_window_end": "params:project.datetime_partitioning_config.forecast_window_end",
            },
            outputs="modified_registered_model_name",
        ),
        node(
            name="make_registered_model",
            func=get_or_create_registered_leaderboard_model_version,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "model_id": "recommended_model_id",
                "registered_model_name": "modified_registered_model_name",
            },
            outputs="registered_model_version_id",
        ),
        node(
            name="make_deployment",
            func=get_replace_or_create_deployment_from_registered_model,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "registered_model_version_id": "registered_model_version_id",
                "registered_model_name": "modified_registered_model_name",
                "label": "params:deployment.label",
                "description": "params:deployment.description",
                "prediction_environment_id": "params:credentials.datarobot.prediction_environment_id",
            },
            outputs="deployment_id",
        ),
        node(
            name="get_date_format",
            func=get_date_format,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "project_id": "project_id",
            },
            outputs="date_format",
        ),
        node(
            name="ensure_deployment_settings",
            func=ensure_deployment_settings,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "deployment_id": "deployment_id",
                "datetime_partitioning_column": "params:project.datetime_partitioning_config.datetime_partition_column",
                "prediction_interval": "params:deployment.prediction_interval",
                "date_format": "date_format",
            },
            outputs=None,
        ),
        node(
            name="set_up_batch_prediction_job",
            func=setup_batch_prediction_job_definition,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "deployment_id": "deployment_id",
                "dataset_id": "preprocessed_timeseries_data_id",
                "enabled": "params:batch_prediction_job_definition.enabled",
                "name": "params:batch_prediction_job_definition.name",
                "batch_prediction_job": "params:batch_prediction_job_definition.batch_prediction_job",
                "schedule": "params:batch_prediction_job_definition.schedule",
            },
            outputs=None,
        ),
        node(
            name="set_up_retraining_job",
            func=lambda endpoint,
            token,
            deployment_id,
            name,
            dataset_id,
            retraining_settings: get_update_or_create_retraining_policy(
                endpoint, token, deployment_id, name, dataset_id, **retraining_settings
            ),
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "deployment_id": "deployment_id",
                "name": "params:retraining_policy.name",
                "dataset_id": "preprocessed_timeseries_data_id",
                "retraining_settings": "params:retraining_policy.retraining_settings",
            },
            outputs=None,
        ),
    ]
    pipeline_inst = pipeline(nodes)
    return pipeline(
        pipeline_inst,
        namespace="deploy_forecast",
        parameters={
            "params:credentials.datarobot.endpoint",
            "params:credentials.datarobot.api_token",
            "params:credentials.datarobot.prediction_environment_id",
        },
        inputs={"use_case_id"},
        outputs={
            "project_id",
            "recommended_model_id",
            "deployment_id",
        },
    )
