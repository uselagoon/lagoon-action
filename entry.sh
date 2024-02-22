#!/bin/sh

# Create SSH directory
mkdir -p ~/.ssh/

# Copy SSH private key from environment variable
echo -e "$INPUT_SSH_PRIVATE_KEY" > ~/.ssh/id_rsa

# Set correct permissions
chmod 600 ~/.ssh/id_rsa

# Add Lagoon host to known hosts
# ssh-keyscan your-lagoon-hostname >> ~/.ssh/known_hosts

# Set correct permissions for known_hosts
touch ~/.ssh/known_hosts
chmod 644 ~/.ssh/known_hosts

cp /rootcp/.lagoon.yml ~/.lagoon.yml


# envplate the .lagoon.yaml file
ep ~/.lagoon.yml


# Run the action
python3 /action.py


