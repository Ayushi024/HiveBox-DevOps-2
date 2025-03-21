# CI/CD Pipeline Documentation

## 1. Introduction
This document outlines the steps taken to set up Continuous Integration (CI) and related configurations for the project. It details the tools, code implementation, containerization, and workflow setup for OpenSSF Scorecard.

## 2. Tools
- **Hadolint** and **VS Code Hadolint extension**: Used for linting Dockerfiles.
- **Pylint** and **VS Code Pylint extension**: Used for linting Python code.

## 3. Code Implementation

### 3.1 Version Endpoint
- **Endpoint**: `/version`
- **Parameters**: None
- **Functionality**: Returns the version of the deployed application.

### 3.2 Temperature Endpoint
- **Endpoint**: `/temperature`
- **Parameters**: None
- **Functionality**:
  - Returns the current average temperature based on all senseBox data.
  - Ensures the data is no older than 1 hour.

## 4. Containerization
- Followed **Docker Best Practices** to optimize and secure Docker images.
- Used **Hadolint** to ensure best practices in Dockerfile implementation.

## 5. Continuous Integration (CI)
### 5.1 GitHub Actions Workflow for CI
- **Linting**:
  - Configured `flake8` for Python code linting.
  - Configured `Hadolint` for Dockerfile linting.
- **Unit Testing**:
  - Implemented unit tests for all endpoints using `pytest`.
  - Configured GitHub Actions to run unit tests on every push and pull request.
- **Building Docker Images**:
  - Set up GitHub Actions to build and push Docker images to GitHub Container Registry (GHCR).
  - Ensured structured tagging of images based on Git commit SHA.
- **OpenSSF Scorecard**:
  - Integrated OpenSSF Scorecard GitHub Action to assess repository security and fix reported issues.

## 6. Installation of OpenSSF Scorecard
### 6.1 Workflow Setup
1. From your GitHub project's main page, click **“Security”** in the top navigation bar.
2. Select **“Code scanning”**.
3. Depending on whether the repository already has a scanning tool configured, you will see **"Add tool"** or **"Configure scanning tool"**.
   - **a.** If you see **"Add tool"**, click it and skip step **b**.
   - **b.** If you see **"Configure scanning tool"**, proceed to step **4**.
4. Click **"Explore workflows"** underneath the "Other tools" section.
5. Choose **"OSSF Scorecard"** from the list of workflows, then click **“Configure”**.
   - *(Tip: You can type "OSSF" in the search box to find it faster.)*
6. Commit the changes. *(Your button might say "Commit changes..." instead of "Start commit", it does the same thing.)*
