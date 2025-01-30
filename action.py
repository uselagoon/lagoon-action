import os
import subprocess
import json
import time
from helpers import build_buildvar_strings, parse_key_value_string

global LAGOON_NAME
LAGOON_NAME = os.environ.get("INPUT_LAGOON_NAME", "lagoon")

class LagoonCLIError(Exception):
    pass


def driver():
    # Read environment variables
    mode = os.environ.get("INPUT_ACTION", "default")
        # Get project and environment names from environment variables
    project_name = os.environ.get("INPUT_LAGOON_PROJECT", "")
    environment_name = os.environ.get("INPUT_LAGOON_ENVIRONMENT", "")
    wait_till_deployed = os.environ.get("INPUT_WAIT_FOR_DEPLOYMENT", "true").lower().strip() == "true"

    # Perform actions based on the value of the 'mode' variable
    try:
        if mode == "deploy":
            buildVarString = os.environ.get("INPUT_BUILD_VARS")
            buildVars = {}
            if(buildVarString != ""):
                buildVars = parse_key_value_string(buildVarString)
            # We grab the event data from the payload file Github injects
            json_data = process_github_event_file()
            if json_data.get("pull_request") is not None:
                # now we pull the relevant details
                baseBranchName = json_data["pull_request"]["base"]["ref"]
                baseBranchRef = json_data["pull_request"]["base"]["sha"]
                headBranchName = json_data["pull_request"]["head"]["ref"]
                headBranchRef = json_data["pull_request"]["head"]["sha"]
                prTitle = json_data["pull_request"]["title"]
                prNumber = json_data["pull_request"]["number"]
                # if any of the four above are empty, we should fail
                if baseBranchName == "":
                    print("Error: Base branch name is missing.")
                if baseBranchRef == "":
                    print("Error: Base branch ref is missing.")
                if headBranchName == "":
                    print("Error: Head branch name is missing.")
                if headBranchRef == "":
                    print("Error: Head branch ref is missing.")
                if prTitle == "":
                    print("Error: Pull request title is missing.")
                if prNumber == "":
                    print("Error: Pull request number is missing.")

                # Exit with an error code if any required details are missing
                if baseBranchName == "" or baseBranchRef == "" or headBranchName == "" or headBranchRef == "" or prTitle == "" or prNumber == "":
                    exit(1)
                
                print(f"Deploying PR: {prTitle} (#{prNumber}) from {headBranchName} to {baseBranchName}")

                deploy_pull_request(project_name, prTitle, prNumber, baseBranchName, baseBranchRef, headBranchName, headBranchRef, buildVars, wait_till_deployed)
            else:
                #we're dealing with a branch
                print(f"Deploying branch: {project_name} (environment{environment_name})")
                deploy_environment(project_name, environment_name, buildVars, wait_till_deployed)
        elif mode == "upsert_variable":
            variable_scope = os.environ.get("INPUT_VARIABLE_SCOPE","runtime")
            variable_name = os.environ.get("INPUT_VARIABLE_NAME", "")
            variable_value = os.environ.get("INPUT_VARIABLE_VALUE", "")
            
            upsert_variable(project_name, environment_name, variable_scope, variable_name, variable_value)
        else:
            default_process()
    except LagoonCLIError as e:
        print(f"Error: {e}")
        exit(1)

def deploy_environment(project_name, environment_name, buildVars, wait_till_deployed=True):
    
    if not project_name or not environment_name:
        raise LagoonCLIError("Missing project or environment name.")

    #generate build vars from keyval array
    stringMap = build_buildvar_strings(buildVars)
    buildVarArgumentString = ' '.join(stringMap)
    # Lagoon CLI command to deploy the latest version with --output-json flag
    lagoon_command = (
        f"lagoon -l {LAGOON_NAME} --skip-update-check --returndata --force --output-json -i ~/.ssh/id_rsa deploy branch "
        f"-p {project_name} -b {environment_name} {buildVarArgumentString}"
    )

    debugLog(f"Running Lagoon CLI command: {lagoon_command}")

    # Call the Lagoon CLI command and capture the output
    output = run_lagoon_command(lagoon_command)

    # grab buildid
    result_json = json.loads(output)
    build_id = result_json["result"]

    debugLog(f"Deployment initiated. Build ID: {build_id}")

    if wait_till_deployed:
        debugLog(f"Waiting for deployment to complete.")
        wait_for_deployment(project_name, environment_name, build_id)

    return build_id

def deploy_pull_request(project_name, pr_title, pr_number, baseBranchName, baseBranchRef, headBranchName, headBranchRef, buildVars, wait_till_deployed=True):
    
    if not project_name:
        raise LagoonCLIError("Missing project name.")

    #generate build vars from keyval array
    stringMap = build_buildvar_strings(buildVars)
    buildVarArgumentString = ' '.join(stringMap)

    # Lagoon CLI command to deploy the latest version with --output-json flag
    lagoon_command = (
        f"lagoon -l {LAGOON_NAME} --skip-update-check --returndata --force --output-json -i ~/.ssh/id_rsa deploy pullrequest "
        f"-p '{project_name}' --base-branch-name '{baseBranchName}' --base-branch-ref '{baseBranchRef}' "
        f"--head-branch-name '{headBranchName}' --head-branch-ref {headBranchRef} "
        f"--title '{pr_title}' --number {pr_number} {buildVarArgumentString}"
    )

    debugLog(f"Running Lagoon CLI command: {lagoon_command}")  

    # Call the Lagoon CLI command and capture the output
    output = run_lagoon_command(lagoon_command)
    result_json = json.loads(output)
    build_id = result_json["result"]

    debugLog(f"Deployment initiated. Build ID: {build_id}")

    if wait_till_deployed:
        debugLog(f"Waiting for deployment to complete.")
        wait_for_deployment(project_name, f"pr-{pr_number}", build_id)

    return build_id


def wait_for_deployment(project_name, environment_name, build_id):
    timeout_minutes = int(os.environ.get("INPUT_MAX_DEPLOYMENT_TIMEOUT", "30"))
    interval_seconds = 60
    start_time = time.time()
    iterations = 0
    failed_checks = 0
    max_failed_checks = 5

    while True:
        # Lagoon CLI command to get deployment status
        status_command = (
            f"lagoon get deployment --output-json -l {LAGOON_NAME} -p {project_name} -e {environment_name} -N {build_id}"
        )

        debugLog(f"Running Lagoon CLI command: {status_command}")
        
        # Call the Lagoon CLI command and capture the output
        output = run_lagoon_command(status_command)
        
        # Process the JSON output and check the status
        if output:
            try:
                status_data = json.loads(output)
                deployment_status = status_data["data"][0]["status"]
                debugLog(f"Waiting for deployment to complete. Iteration: {iterations}. Status: {deployment_status}")
            
                # TODO: are there any other terminal states?
                if deployment_status in ["complete"]:
                    return deployment_status
                    break  # Exit the loop if status is complete or failed
                if deployment_status in ["failed", "cancelled"]:
                    raise LagoonCLIError(f"Deployment status: {deployment_status}")
                    break
                # Let's keep track of how many times we've done this
                iterations += 1                
            except json.JSONDecodeError as e:
                if failed_checks >= max_failed_checks:
                    raise LagoonCLIError(f"Error decoding JSON output: {e}")
                else:
                    failed_checks += 1
                    debugLog(f"Error decoding JSON output: {e}")
                    debugLog(f"Failed checks incremented: {failed_checks}")

        # Check for timeout
        elapsed_time = time.time() - start_time
        if elapsed_time >= timeout_minutes * 60:
            raise LagoonCLIError("Timeout reached. Deployment status check aborted.")

        # Wait for the specified interval before checking the status again
        debugLog(f"Waiting for {interval_seconds} seconds before checking status again.")
        time.sleep(interval_seconds)


def process_github_event_file():
    # Step 1: Check if the environment variable GITHUB_EVENT_PATH exists
    github_event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not github_event_path:
        raise LagoonCLIError("Environment variable GITHUB_EVENT_PATH is not set.")

    # Step 2: Check if the file specified by GITHUB_EVENT_PATH exists
    if not os.path.isfile(github_event_path):
        raise LagoonCLIError(f"File specified by GITHUB_EVENT_PATH does not exist: {github_event_path}")

    try:
        # Step 3: Read the file into a variable
        with open(github_event_path, "r") as file:
            event_data = file.read()

        # Step 4: Parse the JSON into a traversable structure
        json_data = json.loads(event_data)
        return json_data

    except json.JSONDecodeError as e:
        raise LagoonCLIError(f"Error decoding JSON from file: {e}")
    except Exception as e:
        raise LagoonCLIError(f"Error processing GitHub event file: {e}")

def upsert_variable(project_name, environment_name, variable_scope, variable_name, variable_value):

    if variable_scope not in ["global", "build", "runtime", "container_registry", "internal_container_registry"]:
        raise LagoonCLIError("Invalid variable scope. Must be one of: global, build, runtime, container_registry, internal_container_registry")
    
    if variable_name == "":
        raise LagoonCLIError("Variable name cannot be empty.")
    
    if variable_value == "":
        raise LagoonCLIError("Variable value cannot be empty.")

    
    # Lagoon CLI command to deploy the latest version with --output-json flag
    lagoon_command = (
        f"lagoon -l {LAGOON_NAME} --skip-update-check --force --output-json -i ~/.ssh/id_rsa update variable "
        f"-p {project_name} -e {environment_name} -N '{variable_name}' -V '{variable_value}' -S {variable_scope}"
    )

    debugLog(f"Running Lagoon CLI command: {lagoon_command}")  

    # Call the Lagoon CLI command and capture the output
    output = run_lagoon_command(lagoon_command)

    debugLog(f"Variable upsert output: {output}")
    return output


def debugLog(message):
    input_debug = os.environ.get("INPUT_DEBUG", "false")
    if input_debug.lower().strip() == "true":
        print(f"debug: {message}")

def default_process():
    print("Set an 'action' value of 'deploy' or 'upsert_variable' to use this action.")
    exit(1)

def run_lagoon_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True)
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Error executing Lagoon CLI command: {e}")
        print(f"Command output: {e.output.decode('utf-8')}")
        print(f"Command error: {e.stderr.decode('utf-8')}")
        raise LagoonCLIError(f"Error executing Lagoon CLI command: {e}")

if __name__ == "__main__":
    driver()
