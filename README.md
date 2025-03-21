# CI/CD Pipeline Documentation
-------------------------------------------------------------------------------phase 3-------------------------------------
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


                                                                                  
---------------------------------------------------------------phase 4---------------------------------------------------

                                                                                                        
                                                                                                         
                                                                                                         
## 1. Code Implementation               
- **Implemented the Flask APIs:**
  - `/metrics` – Returns Prometheus default metrics.
  - `/temperature` – Fetches temperature from OpenWeather API and adds a status based on average value.
- **Configured** `OPENWEATHER_API_KEY` 
- **Tested** the endpoints locally and confirmed functionality.

## 2. Containerization
- **Created Dockerfiles** for both APIs:
  - `sensor_api/Dockerfile`
  - `basic_versioning/Dockerfile`
- **Built and pushed versioned Docker images** to GitHub Container Registry (GHCR):
  - `ghcr.io/ayushi024/hivebox-sensor-api`
  - `ghcr.io/ayushi024/hivebox-basic-versioning`

## 3. KIND Configuration and Ingress-Nginx Setup
- **Created a KIND cluster** with Ingress-Nginx for local Kubernetes testing.
- **Configured KIND** to map container ports to host ports 


## 4. Kubernetes Core Manifests
- **Created Kubernetes manifests:**
  - `deployment.yaml` (for both APIs)
  - `service.yaml` (exposing services)
  - `ingress.yaml` (Ingress to route traffic to APIs)
- **Implemented security hardening:**
  - Enabled AppArmor profiles.
  - Configured `seccompProfile` as `RuntimeDefault`.
  - Enforced running containers as non-root with `runAsNonRoot`.
  - Disabled `allowPrivilegeEscalation` and dropped all capabilities.
  - Applied liveness and readiness probes.
- **Updated manifests** dynamically using image digests.

## 5. Continuous Integration (CI)

- **Created a GitHub Actions workflow:**
  - **Linting:** Using `flake8` to check code quality.
  - **Unit Tests:** Using `pytest` to run tests for both APIs.
  - **Integration Tests:** Added integration tests with mocks.
  - **SonarQube Analysis:** Ensured code quality and security best practices using SonarQube.
  - **Terrascan Security Scan:** Validated Kubernetes manifests for security misconfigurations.

## 6. Continuous Delivery (CD)
- **Enhanced the CI workflow** to include CD steps:
  - Built and pushed versioned Docker images.
  - Updated Kubernetes manifests with image digests.
  - Opened a Pull Request to merge updated manifests.
  - Deployed to a KIND cluster as part of the staging environment.


## 7. Security and Best Practices

- **Conducted Terrascan Security Audit:**
  - Scanned Kubernetes manifests for misconfigurations.
  - Fixed issues related to AppArmor, seccomp, image digests, and privilege escalation.
- **Performed SonarQube Analysis:**
  - Scanned for code quality, vulnerabilities, and potential bugs.
- **Hardened security practices** in Dockerfiles and Kubernetes manifests.

## 8. API Testing & Endpoint Verification

- **Verified the following endpoints:**
  - `/temperature` – Returns temperature and status.
  - `/metrics` – Exposes Prometheus metrics.
  - `/version` – Returns application version.
- **Debugged and fixed endpoint errors** during initial tests.



**SonarQube**                                      
SonarQube is an open-source platform developed by SonarSource for continuous inspection of code quality. It performs automatic reviews through static code analysis to detect bugs, vulnerabilities, and code smells across various programming languages. 
                                                                                        
**Terrascan**                                                     
Terrascan is a static code analyzer developed by Tenable for Infrastructure as Code (IaC). It enables developers and DevOps teams to scan IaC templates for security vulnerabilities and compliance violations before deploying infrastructure, ensuring that cloud resources are provisioned securely.
