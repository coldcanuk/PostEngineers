# Discord Bot with OpenAI, Flask, and Azure Deployment

## Table of Contents:
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Setup Requirements](#setup-requirements)
4. [GitHub Actions Secrets](#github-actions-secrets)
5. [Installation and Deployment](#installation-and-deployment)
6. [Overview of Functionality](#overview-of-functionality)
7. [Post-Deployment Steps](#post-deployment-steps)
8. [Contributing](#contributing)
9. [License](#license)

## Introduction
This project features a Discord bot that leverages OpenAI's GPT-4 to process and generate content based on user inputs. Developed in Python with Flask, the bot integrates with Discord's bot framework and OpenAI's API to offer a unique interactive experience. It is designed for containerization with Docker and deployment on Azure Container Instances via GitHub Actions for CI/CD, utilizing Terraform for infrastructure management.

## Prerequisites
- Python 3.11 or higher
- Docker Desktop
- An Azure subscription
- GitHub account
- An OpenAI API key

## Setup Requirements
Before deploying the bot, ensure you have:
- Installed and logged in to the Azure CLI.
- Configured Docker on your workstation.
- Terraform installed for infrastructure provisioning.
- Python 3.11 or higher, with Flask installed.

## GitHub Actions Secrets
To securely deploy and operate the bot, configure the following secrets in your GitHub repository:
- `AZURE_TENANT_ID`: Your Azure account tenant ID.
- `AZURE_CLIENT_ID`: The client ID of your Azure service principal.
- `AZURE_CLIENT_SECRET`: The secret associated with the Azure service principal.
- `AZURE_REGISTRY_USERNAME`: The username for your Azure Container Registry.
- `AZURE_REGISTRY_PASSWORD`: The password for your Azure Container Registry.
- `OPENAI_API_KEY`: Your OpenAI API key for GPT-4 access.
- `DISCORD_TOKEN`: The token for your Discord bot.
- `ASSISTANT_PENELOPE`: ID for Penelope, an assistant configured in your OpenAI application.
- `ASSISTANT_MARIECAISSIE`: ID for Marie Caissie, another assistant in your OpenAI app.
- `DEBUG_MODE`: Set to `True` for detailed logs.

## Installation and Deployment
1. **Azure and Terraform Setup**: Follow the Azure CLI and Terraform documentation to set up your infrastructure as per `postengineers.tf`.
2. **Local Testing**: Ensure `app.py` functions correctly locally by setting environment variables for the OpenAI API key, Discord token, and assistant IDs.
3. **GitHub Actions Configuration**: In your GitHub repo, adjust `.github/workflows/main.yml` for CI/CD pipeline, which automates the Docker build and push to Azure Container Registry, followed by deployment to Azure Container Instances.
4. **Deployment**: Trigger a deployment by pushing to the `main` branch. GitHub Actions will execute the defined jobs, deploying your application to Azure.

## Overview of Functionality
The bot, developed in `app.py`, integrates with Discord and OpenAI GPT-4 to process user commands. It utilizes two specialized assistants, Penelope and Marie Caissie, to generate engaging content based on the instructions embedded in the code. The content is fetched and presented within Discord, providing a seamless interaction experience. This innovative approach allows for dynamic content generation, offering a wide range of possibilities for user engagement.

## Post-Deployment Steps
- Verify the deployment through the Azure portal or CLI.
- Use Discord to interact with your bot and ensure it's responding as expected.
- Monitor logs and performance metrics within Azure and GitHub Actions for any issues.

## Contributing
We welcome contributions! Please see the project's contributing guidelines for how to propose changes.

## License
This project is licensed under the GNU General Public License v3.0. It incorporates contributions from OpenAI's GPT-4 and the development efforts of the project team.
