# Weather Forecastic

Weather Forecastic allows users to track and predict their favorite cities' weather using Datarobot. This template allows users to connect their data to DataRobot's functionality seamlessly with automated data updates and real-time forecasting. We deploy a model trained on your data, then create a streamlit application for clear visualizations of the deployment's capabilities. We can ensure accurate model performance through scheduled batch predictions and automatic retraining if our model's accuracy drops below a set threshold.

## Getting started -- Pulling Data
1. Create a Use Case on [DataRobot](app.datarobot.com)
   - Click on "DataRobot NextGen"
   - Select Workbench
   - In the top right, click "Create New Use Case"

2. Create a new Code Space and navigate into it
   - Click the blue "Add" button

3. Open up a terminal (in the bottom-left corner you'll see a ">_" icon) and type the following commands.
   ```bash
   pip install kedro
   ```
   ```bash
   kedro new --starter=https://github.com/j-beastman/WeatherForecastic.git --checkout master
   ```
   ```bash
   pip install -r your_project_name/requirements.txt
   ```

4. `cd` into your project folder, then open `conf/local/credentials.yml`
   - Fill in your datarobot and OpenAI credentials
   - Note: Notebook environment API keys are automatically recycled. It is recommended to use a DataRobot API Token from developer tools rather than from the notebook environment.

5. Navigate to `conf/base/parameters.yml`
   - Add in the cities along with the weather features you want to collect

6. Now, in the terminal type 
   ```bash
   kedro run -p "setup"
   ```
   This subpipeline...
   - Collects historical weather data from the cities you inputted so that we have modeling data ready from the get-go.
   - Sets up a scheduled notebook to pull weather data from your cities every 2 hours to ensure your data is up-to-date.
      - This incoming data also allows us to pair actuals with predictions made via our batch prediction job which will be setup in the next step.

7. Once the setup pipeline has run, open up the terminal again to type
   ```bash
   kedro run
   ```

8. Sit back and watch your Datarobot deploy your model, your deployment, and your custom application. 

![Running App](https://s3.amazonaws.com/datarobot_public/drx/recipe_gifs/forecastic-weather.gif)

## <a name="gh-auth"></a> Authenticating with GitHub
How to install `gh` [GitHub CLI][GitHub CLI-link]

[GitHub CLI-link]: https://github.com/cli/cli

Run `gh auth login` in the terminal and answer the following questions with:
- `? What account do you want to log into?` **GitHub.com**
- `? What is your preferred protocol for Git operations on this host?` **HTTPS**
- `? Authenticate Git with your GitHub credentials?` **Yes**
- `? How would you like to authenticate GitHub CLI?` **Login with a web browser**

Copy the code in: `! First copy your one-time code:` **XXXX-XXXX**

Open a web browser at https://github.com/login/device and enter the above code manually.

You should see in the terminal:
- `✓ Authentication complete.`
- `✓ Logged in as YOUR_USERNAME`

More details on GitHub authentication [here][gh-docs].

[gh-docs]: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github#https

## Making changes to the pipeline
The following files govern pipeline execution. In general, you will not need to modify
any other boilerplate files as you customize the pipeline.:

- `conf/base/parameters.yml`: pipeline configuration options and hyperparameters
- `conf/local/credentials.yml`: API tokens and other secrets
- `conf/base/catalog.yml`: file storage locations that can be used as node inputs or outputs,
  including locations of supporting assets to build DR custom models, execution environments
- `src/your_project_name/pipelines/*/nodes.py`: function definitions for the pipeline nodes
- `src/your_project_name/pipelines/*/pipeline.py`: node names, inputs and outputs
- `src/datarobotx/idp`: directory contains function definitions for for reusable idempotent DR nodes
- `include/your_project_name`: directory contains raw assets and templates used by the pipeline

For a deeper orientation to kedro principles and project structure visit the [Kedro][kedro-docs]
documentation.

[kedro-docs]: https://docs.kedro.org/en/stable/

## For contributors

1. Install datarobotx-idp locally
   ```bash
   git clone https://github.com/datarobot-community/datarobotx-idp
   cd datarobotx-idp
   pip install -e .
   ```

2. Install kedro, install requirements from requirements.txt

3. Fill in your credentials.yml, ensure globals.yml is filled in.

4. Run
   ```bash
   kedro run -p "setup"
   ```

5. Once this is complete, run 
   ```bash
   kedro run
   ```

### Running Tests
To ensure that your assets are set up properly, we have tests set up.
1. `pip install pytest pytest-cov datarobot-predict`

2. navigate to root of project directory and run `pytest` from the terminal
