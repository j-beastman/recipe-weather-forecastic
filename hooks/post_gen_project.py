# Copyright 2024 DataRobot, Inc. and its affiliates.
# All rights reserved.
# DataRobot, Inc.
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
# Released under the terms of DataRobot Tool and Utility Agreement.

import os
import subprocess
import shutil
import stat

import datarobot as dr

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

yaml = YAML()

def remove_readonly(func, path, excinfo):
    """Handle windows permission error.

    https://stackoverflow.com/questions/1889597/deleting-read-only-directory-in-python/1889686#1889686
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


print("Copying latest datarobotx-idp source into project..\n")
subprocess.run(
    [
        "git",
        "clone",
        "--branch",
        "main",
        "https://github.com/datarobot-community/datarobotx-idp.git",
    ],
    check=True,
)
shutil.copytree("datarobotx-idp/src/datarobotx", "src/datarobotx")
shutil.rmtree("datarobotx-idp", onerror=remove_readonly)

try: 
    usecase_name = dr.UseCase.get(os.environ['DATAROBOT_DEFAULT_USE_CASE']).name
except KeyError:
    print("Detected local creation. Usecase name will be your selected project name.")
    usecase_name = "{{ cookiecutter.project_name }}"

print("Updating parameters.yml")

file_path = 'conf/base/parameters.yml'
with open(file_path, 'r') as file:
    yaml_content = yaml.load(file)

if not isinstance(yaml_content, CommentedMap):
    yaml_content = CommentedMap(yaml_content)

# TODO: does it make sense to dynamically create the names
# Pro: I think it prevents user error
# Con: It doesn't allow user to specify names?
yaml_content['setup']['use_case']['name'] = usecase_name

yaml_content['preprocessing']['use_case']['name'] = usecase_name

# 
yaml_content['deploy_forecast']['use_case']['name'] = usecase_name
yaml_content['deploy_forecast']['retraining_policy']['name'] = usecase_name + ' Retraining Policy'
yaml_content['deploy_forecast']['batch_prediction_job_definition']['name'] = usecase_name + ' Prediction Job'


print("Updating credentials.yml")
with open(file_path, 'w') as file:
    yaml.dump(yaml_content, file)

file_path = 'conf/local/credentials.yml'
with open(file_path, 'r') as file:
    yaml_content = yaml.load(file)

try:
    yaml_content['datarobot']['endpoint'] = os.environ['DATAROBOT_ENDPOINT']
except KeyError:
    pass

try:
    prediction_server = dr.PredictionServer.list()[0]
    yaml_content['datarobot']['default_prediction_server_id'] = prediction_server.id
except:
    pass

with open(file_path, 'w') as file:
    yaml.dump(yaml_content, file)

print('YAML file updated successfully.')

