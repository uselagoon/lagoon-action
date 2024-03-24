# Use the uselagoon/lagoon-cli as a base image
# FROM uselagoon/lagoon-cli as base
FROM ghcr.io/uselagoon/lagoon-cli:v0.21.0 as base


RUN apk update && apk upgrade && apk add python3 py3-pip

# Grab envplate so we can sort out the configuration files
RUN wget -q https://github.com/kreuzwerker/envplate/releases/download/v1.0.2/envplate_1.0.2_$(uname -s)_$(uname -m).tar.gz -O - | tar xz && mv envplate /usr/local/bin/ep && chmod +x /usr/local/bin/ep

# Copy the entry script and set correct permissions
COPY entry.sh /entry.sh
COPY *.py /
RUN chmod +x /entry.sh

# copy across the lagoon.yaml file
COPY lagoon.yml /rootcp/.lagoon.yml

# let's set up a symlink to the lagoon cli into the /usr/local/bin directory
RUN ln -s /lagoon /usr/local/bin/lagoon

# Set up environment variable for the SSH key
ENV INPUT_SSH_PRIVATE_KEY ""
ENV INPUT_LAGOON_GRAPHQL_ENDPOINT "https://api.lagoon.amazeeio.cloud/graphql"
ENV INPUT_LAGOON_SSH_HOSTNAME "ssh.lagoon.amazeeio.cloud"
ENV INPUT_LAGOON_PORT "32222"
ENV INPUT_LAGOON_COMMAND "whoami"

WORKDIR /

# Entry point to run the custom script
ENTRYPOINT ["/entry.sh"]