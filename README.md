# 🚀 CI/CD Pipeline Setup & Deployment  

This repository demonstrates a CI/CD pipeline for two services:  

1. **Versioning API** (basic_versioning/)  
2. **Sensor API** (sensor_api/)  



## 📌 Features  
✅ Linting with **flake8**  
✅ Unit Testing with **pytest**  
✅ Building & Pushing Docker Images to **DockerHub**  
✅ Managing Secrets (**GitHub Secrets** for API Keys & DockerHub)  
✅ Continuous Integration (**CI**) using **GitHub Actions**  



## 📌 1. Prerequisites  
Ensure you have:  

✅ **Git** installed  
✅ **Docker** installed & running  
✅ **Python 3.12+** installed  
✅ **GitHub repository** with Actions enabled  



## 🔐 2. Setting Up GitHub Secrets  
We use **GitHub Secrets** to store sensitive information like **DockerHub credentials** and the **OpenWeather API key**.  

### ➡️ Steps to Add Secrets:  
1. Go to your **GitHub repository**.  
2. Click on **Settings → Secrets and variables → Actions**.  
3. Click **New repository secret** and add the following:  

   - **DOCKER_USERNAME** → *(Your DockerHub username)*  
   - **DOCKER_PASSWORD** → *(Your DockerHub password or access token)*  
   - **OPENWEATHER_API_KEY** → *(Your OpenWeather API key)*  



## 📌 3. Project Setup  

➡️ **Clone the Repository**  
➡️ **Install Dependencies**  



## 📌 4. Docker Setup  
Each service has its own **Dockerfile**.  

➡️ **Create Dockerfile** for **Versioning API** (`basic_versioning/Dockerfile`)  
➡️ **Create Dockerfile** for **Sensor API** (`sensor_api/Dockerfile`)  



## 📌 5. CI/CD Workflow (GitHub Actions)  
The **CI pipeline** includes:  

✅ **Linting (flake8)** – Ensures code quality.  
✅ **Unit Testing (pytest)** – Runs automated tests.  
✅ **Building & Pushing Docker Images** – Deploys images to **DockerHub**.  



### ➡️ How to Trigger the Pipeline  
The pipeline **runs automatically** on every **push** or **pull request** to `main`.  
You can also **manually trigger** it from the **GitHub Actions tab**.  

### ➡️ How to Check CI/CD Status  
Go to **GitHub → Actions tab** to view the **pipeline logs** and **debug failures**.  



## 📌 Step-by-Step Workflow for Feature Branch Development & CI Integration     

1️⃣ Clone the Main Repository (If Not Already Cloned)                                
If you haven’t cloned your repository yet, run:                                
git clone https://github.com/your-username/HiveBox-DevOps-.git                                
cd HiveBox-DevOps-                                
                                
2️⃣ Set Up Branch Protection Rules (One-Time Setup)                                 
Before creating feature branches, enforce CI checks before merging into main:                                
Go to your repository on GitHub.                                
Navigate to Settings → Branches.                                
Under Branch Protection Rules, click Add Rule.                                
Set Branch name pattern to main.                                
Enable the following options:                                
✅ Require status checks to pass before merging.                                
✅ Select the required CI checks (GitHub will show available CI checks from Actions).                                
✅ Require branches to be up to date before merging (optional but recommended).                                
✅ Require pull request reviews before merging (optional for extra safety).                                
Click Save Changes.                                

3️⃣ Create a New Feature Branch                                
Run the following command to create and switch to a new feature branch:                                
git checkout -b feature-branch                                

4️⃣ Pull the Latest Code from Main into the Feature Branch                                
To ensure the feature branch is up to date with main:                                
git pull origin main                                
                                
5️⃣ Make Changes in the Feature Branch                                
Modify files, add new code, or update existing functionality.                                
For example, update app.py or add a new feature.                                
                                
6️⃣ Commit the Changes                                
Stage and commit your changes using Conventional Commits:                                
git add .                                
git commit -m "feat: add new feature"                                
                                
7️⃣ Push the Feature Branch to GitHub                                
git push origin feature-branch                                

8️⃣ Create a Pull Request (PR) in GitHub                                
Go to your repository on GitHub.                                
Click on Pull Requests → New Pull Request.                                
Select feature-branch as the source and main as the target.                                
Click Create Pull Request.                                
                                
9️⃣ CI Pipeline Runs Automatically on the PR                                
GitHub Actions will trigger the CI pipeline from .github/workflows/ci.yml.                                
The pipeline will:                                
✅ Checkout the code                                
✅ Install dependencies                                
✅ Run tests (pytest tests/)                                
✅ Lint code (flake8 app.py)                                

🔟 Ensure CI Passes Before Merging                                
Open the PR in GitHub.                                
Click on the Checks tab.                                
If all checks pass ✅ → The Merge button will be enabled.                                
If any check fails ❌ → You must fix errors before merging.                                

1️⃣1️⃣ Merge the PR into main (Only If CI Passes)                                
Click Merge Pull Request.                                
Delete the feature branch (optional but recommended):                                
git branch -d feature-branch                                
git push origin --delete feature-branch                                


