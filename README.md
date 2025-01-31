# Lagoon Action

This action interacts with the Lagoon API to allow you to currently
* Create and deploy environments based on Branch name or PR
* Upsert project/environment variables

## Requirements

To use this GitHub Action, you'll need to set up the following:

### GitHub Action Secret

* You will want to contact your Lagoon API administrator to set up a user with the [developer role](https://docs.lagoon.sh/concepts-basics/building-blocks/roles/) on the project you're going to be interacting with using this action.
* You should then add an SSH key to this user's account that will _only_ be used by this action.
* Create a secret in your GitHub repository that contains the private SSH key for authenticating with Lagoon. To add a secret:

   - Navigate to your GitHub repository.
   - Go to the "Settings" tab.
   - In the left sidebar, click on "Secrets and Variables"
   - Click on "Actions".
   - Click on "New repository secret."
   - Name the secret, e.g., `LAGOON_SSH_PRIVATE_KEY`.
   - Paste the contents of your private SSH key into the "Value" field.
   - Click on "Add secret."

## Inputs

### General

#### `action`

**Description:** One of the following actions: deploy (default), upsert_variable.

**Required:** Yes

**Default:** 'deploy'

#### `ssh_private_key`

**Description:** SSH private key for Lagoon authentication.

**Required:** Yes

#### `lagoon_graphql_endpoint`

**Description:** Lagoon GraphQL endpoint.

**Required:** No

**Default:** https://api.lagoon.amazeeio.cloud/graphql

#### `lagoon_ssh_hostname`

**Description:** Lagoon SSH hostname.

**Required:** No

**Default:** ssh.lagoon.amazeeio.cloud

#### `lagoon_port`

**Description:** Lagoon SSH port.

**Required:** No

**Default:** 32222

#### `lagoon_project`

**Description:** Lagoon project name.

**Required:** No

#### `lagoon_environment`

**Description:** Lagoon environment name.

**Required:** No

#### `debug`

**Description:** Enable debug output.

**Required:** No

**Default:** false



### Action: deploy

#### `wait_for_deployment`

**Description:** Wait for deployment to finish.

**Action:** `deploy`

**Required:** No

**Default:** false

#### `max_deployment_timeout`

**Description:** Maximum time (minutes) to wait for deployment - defaults to 30 minutes.

**Required:** No

**Action:** `deploy`

**Default:** 30

#### `build_vars`

**Description:** Provides a mechanism to send build variables to be consumed in a deployment (these are not persisted) - format is `KEYNAME=VALUE[,KEY2NAME=VALUE2]`

**Required:** No

### Action: upsert_variable

#### `variable_scope`

**Description:** If action is upsert_variable, this is the variable scope (runtime, build).

**Required:** For `upsert_variable`

**Action:** `upsert_variable`

**Default:** 'runtime'

#### `variable_name`

**Description:** If action is upsert_variable, this is the variable name.

**Required:** For `upsert_variable`

**Action:** `upsert_variable`

#### `variable_value`

**Description:** If action is upsert_variable, this is the variable value.

**Required:** For `upsert_variable`

**Action:** `upsert_variable`


## Example Usage

```yaml
name: Lagoon Deployment

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Repository
      uses: actions/checkout@v2

    - name: Lagoon Deployment
      uses: uselagoon/lagoon-action@v1.0.1
      with:
        action: 'deploy'
        ssh_private_key: ${{ secrets.LAGOON_SSH_PRIVATE_KEY }}
        lagoon_project: 'your-project-name'
        lagoon_environment: 'your-environment-name'
        wait_for_deployment: 'true'
        build_vars: "VARIABLE1=VALUE1,VARIABLE2=VALUE2"

  upsert-variable:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Repository
      uses: actions/checkout@v2

    - name: Lagoon Upsert Variable
      uses: uselagoon/lagoon-action@v1.0.1
      with:
        action: 'upsert_variable'
        ssh_private_key: ${{ secrets.LAGOON_SSH_PRIVATE_KEY }}
        lagoon_project: 'your-project-name'
        lagoon_environment: 'your-environment-name'
        variable_scope: 'runtime'
        variable_name: 'your-variable-name'
        variable_value: 'your-variable-value'

