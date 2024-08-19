# Copyright 2024 DataRobot, Inc. and its affiliates.
# All rights reserved.
# DataRobot, Inc.
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
# Released under the terms of DataRobot Tool and Utility Agreement.

from __future__ import annotations
from typing import Any, Dict, List, TYPE_CHECKING, Union

import tempfile
import datarobot as dr
from pathlib import Path

if TYPE_CHECKING:
    import pathlib


def prepare_yaml_content(*args: Any, **kwargs: Any) -> Union[Dict[str, Any], List[Any]]:
    """Passthrough node for gathering content to be serialized to yaml from upstream node(s).

    Parameters
    ----------
    args : Any
        Positional arguments to be passed as a list to the yaml renderer. If
        specified, all keyword arguments will be ignored.
    kwargs : Any
        Keyword arguments to be passed as a dict to the yaml render. Ignored
        if any positional arguments are passed.

    Returns
    -------
    list or dict :
        The yaml-serializable python object to pass to the yaml renderer.
    """
    if len(args):
        return list(args)
    else:
        return kwargs


def get_or_create_custom_application_source_version_with_secrets(
    endpoint: str,
    token: str,
    azure_endpoint: str,
    azure_api_key: str,
    azure_api_version: str,
    custom_application_source_id: str,
    base_environment_id: str,
    secrets_template: str,
    app_assets: pathlib.Path,
) -> str:
    """Get or create the DR execution environment for the streamlit app.

    Bundles the secrets just in time before uploading so we don't accidentally
    persist them locally.

    Parameters
    ----------
    execution_environment_id : str
        DataRobot exeuction environment id in which a new version will be created
    app_assets : pathlib.Path
        Path to a directory containing all assets to be uploaded when creating the
        execution environment

    Returns
    -------
    str :
        DataRobot id of the created or retrieved execution environment version
    """
    from datarobotx.idp.custom_application_source_version import (
        get_or_create_custom_application_source_version,
    )

    secrets_file = (
        secrets_template.replace("<azure_endpoint>", azure_endpoint)
        .replace("<azure_api_key>", azure_api_key)
        .replace("<azure_api_version>", azure_api_version)
        .replace("<datarobot_endpoint>", endpoint)
        .replace("<datarobot_api_token>", token)
    )

    # Overwrite the placeholder secrets.toml with real secrets
    with open(app_assets / ".streamlit/secrets.toml", "w") as f:
        f.write(secrets_file)

    return get_or_create_custom_application_source_version(
        endpoint=endpoint,
        token=token,
        custom_application_source_id=custom_application_source_id,
        base_environment_id=base_environment_id,
        folder_path=app_assets,
    )


def log_outputs(
    endpoint: str,
    project_id: str,
    model_id: str,
    deployment_id: str,
    application_id: str,
    project_name: str,
    deployment_name: str,
    app_name: str,
) -> None:
    """Log URLs for DR deployments and app.

    Parameters
    ----------
    project_id : str
        DataRobot id of the project
    model_id : str
        DataRobot id of the model
    deployment_id : str
        DataRobot id of the deployment
    application_id : str
        DataRobot id of the custom application
    project_name : str
        Name of the project
    deployment_name : str
        Name of the deployment
    app_name : str
        Name of the deployed custom application
    """
    import logging
    from urllib.parse import urljoin

    base_url = urljoin(endpoint, "/")
    project_url = base_url + "projects/{project_id}/models/{model_id}/"
    deployment_url = base_url + "deployments/{deployment_id}/overview"
    application_url = base_url + "custom_applications/{application_id}/"

    logger = logging.getLogger(__name__)
    logger.info("Application is live!")
    msg = (
        "AutoPilot Project: "
        f"[link={project_url.format(project_id=project_id, model_id=model_id)}]"
        f"{project_name}[/link]"
    )
    logger.info(msg)
    msg = (
        "Deployment: "
        f"[link={deployment_url.format(deployment_id=deployment_id)}]"
        f"{deployment_name}[/link]"
    )
    logger.info(msg)
    msg = (
        "Custom application: "
        f"[link={application_url.format(application_id=application_id)}]"
        f"{app_name}[/link]"
    )
    logger.info(msg)


# def make_app_assets(
#     app_py: str,
#     helpers_py: str,
#     app_parameters_yml: Any,
#     requirements: str,
#     dockerfile: str,
#     logo: str,
#     style_css: str,
#     config_toml: str,
#     secrets_toml: str,
# ) -> tempfile.TemporaryDirectory:
#     """Assemble directory of streamlit assets to be uploaded for a new DR execution environment.

#     Parameters
#     ----------
#     app_py : str
#         app.py contents to be included in execution environment
#     helpers_py : str
#         helpers.py contents to be included in execution environment
#     app_parameters_yaml : dict or list
#         app_parameters.yaml contents to be included in execution environment
#     requirements_txt : str
#         requirements.txt contents to be included in execution environment
#     dockerfile : str
#         Dockerfile contents to be included in execution environment
#     logo : str
#         location of logo to be included in execution environment
#     style_css : str
#         style.css contents to be included in execution environment
#     config_toml : str
#         config.toml contents to be included in execution environment
#     secrets_toml : str
#         secrets.toml contents to be included in execution environment

#     Returns
#     -------
#     tempfile.TemporaryDirectory :
#         Temporary directory containing the contents to be uploaded to DR
#     """
#     import os
#     import pathlib
#     import tempfile

#     import yaml

#     d = tempfile.TemporaryDirectory()
#     path_to_d = d.name

#     files = zip(
#         [
#             app_py,
#             helpers_py,
#             yaml.dump(app_parameters_yml),
#             requirements,
#             dockerfile,
#             style_css,
#         ],
#         [
#             "app.py",
#             "helpers.py",
#             "app_parameters.yaml",
#             "requirements.txt",
#             "Dockerfile",
#             "style.css",
#         ],
#     )
#     for file, name in files:
#         with open(os.path.join(path_to_d, name), "w") as f:
#             f.write(file)

#     logo.save(os.path.join(path_to_d, "DataRobot.png"))

#     dot_streamlit_dir = pathlib.Path(d.name) / ".streamlit"
#     dot_streamlit_dir.mkdir()

#     with open(dot_streamlit_dir / "config.toml", "w") as f:
#         f.write(config_toml)

#     with open(dot_streamlit_dir / "secrets.toml", "w") as f:
#         f.write(secrets_toml)

#     return d


def make_app_assets(
    folder_path: Path, app_parameters_yaml: Any
) -> tempfile.TemporaryDirectory:
    """
    Assemble directory of streamlit assets to be uploaded for a new DR execution environment,
    ignoring files and directories specified in a .datarobot_ignore file.

    Parameters
    ----------
    folder_path : Path
        Path to the directory containing the streamlit app assets.
    app_parameters_yaml : dict or list
        app_parameters.yaml contents to be included in execution environment.

    Returns
    -------
    tempfile.TemporaryDirectory :
        Temporary directory containing the contents to be uploaded to DR.
    """
    import pathspec
    import shutil
    import yaml

    # Create a temporary directory
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name)

    # Read and parse the .datarobot_ignore file
    try:
        with open(folder_path / ".datarobotignore") as f:
            ignore_spec_text = f.readlines()
        ignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", ignore_spec_text)
    except FileNotFoundError:
        ignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", [])

    # Define the ignore function using pathspec
    def ignore_patterns(path, names):
        # Convert path to Path object for relative path calculation
        full_path = Path(path)
        return [
            name
            for name in names
            if ignore_spec.match_file((full_path / name).relative_to(folder_path))
        ]

    # Copy everything from the folder_path to the temporary directory using the ignore function
    shutil.copytree(folder_path, temp_path, dirs_exist_ok=True, ignore=ignore_patterns)

    # Save the app_parameters_yaml contents into a yaml file in the temporary directory
    yaml_file_path = temp_path / "app_parameters.yaml"
    with open(yaml_file_path, "w") as file:
        yaml.dump(app_parameters_yaml, file)

    return temp_dir


def get_dataset_id(dataset_name: str, use_case_id: str) -> Union[str, None]:
    """Retrieve the ID of the dataset

    Parameters
    ----------
    dataset_name : str

    Returns
    -------
    str:
        The ID of the scoring dataset
    """

    datasets = dr.Dataset.list(use_cases=use_case_id)
    return next(
        (dataset.id for dataset in datasets if dataset.name == dataset_name), None
    )
