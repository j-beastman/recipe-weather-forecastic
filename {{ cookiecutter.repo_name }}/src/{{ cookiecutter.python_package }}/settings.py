# Copyright 2024 DataRobot, Inc. and its affiliates.
# All rights reserved.
# DataRobot, Inc.
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
# Released under the terms of DataRobot Tool and Utility Agreement.

"""Project settings. There is no need to edit this file unless you want to change values
from the Kedro defaults. For further information, including these default values, see
https://docs.kedro.org/en/stable/kedro_project_setup/settings.html."""

# Instantiated project hooks.
# For example, after creating a hooks.py and defining a ProjectHooks class there, do
# from {{cookiecutter.python_package}}.hooks import ProjectHooks
from datarobotx.idp.common.credentials_hooks import CredentialsHooks
from datarobotx.idp.common.checkpoint_hooks import CheckpointHooks
{% if cookiecutter.analytics_trace_id %}
from datarobotx.idp.common.analytics_hooks import AnalyticsHooks
{% endif %}


# Hooks are executed in a Last-In-First-Out (LIFO) order.
# HOOKS = (ProjectHooks(),)
HOOKS = (CredentialsHooks(), CheckpointHooks())
{% if cookiecutter.analytics_trace_id %}
# Comment the below line out if you do not wish for recipe usage analytics
# to be reported to DR. No customer code or datasets are included in the
# reported analytics.
HOOKS = (AnalyticsHooks("{{ cookiecutter.analytics_trace_id }}"),) + HOOKS
{% endif %}

# Installed plugins for which to disable hook auto-registration.
# DISABLE_HOOKS_FOR_PLUGINS = ("kedro-viz",)

# Class that manages storing KedroSession data.
# from kedro.framework.session.store import BaseSessionStore
# SESSION_STORE_CLASS = BaseSessionStore
# Keyword arguments to pass to the `SESSION_STORE_CLASS` constructor.
# SESSION_STORE_ARGS = {
#     "path": "./sessions"
# }

# Directory that holds configuration.
# CONF_SOURCE = "conf"

# Class that manages how configuration is loaded.
from kedro.config import OmegaConfigLoader  # noqa: E402

CONFIG_LOADER_CLASS = OmegaConfigLoader
# Keyword arguments to pass to the `CONFIG_LOADER_CLASS` constructor.
CONFIG_LOADER_ARGS = {
      "base_env": "base",
      "default_run_env": "local",
#       "config_patterns": {
#           "spark" : ["spark*/"],
#           "parameters": ["parameters*", "parameters*/**", "**/parameters*"],
#       }
}

# Class that manages Kedro's library components.
# from kedro.framework.context import KedroContext
# CONTEXT_CLASS = KedroContext

# Class that manages the Data Catalog.
# from kedro.io import DataCatalog
# DATA_CATALOG_CLASS = DataCatalog