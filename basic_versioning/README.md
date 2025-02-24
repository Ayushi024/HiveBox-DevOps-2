 # HiveBox-DevOps
A simple DevOps project to practice Git, Docker, and basic app versioning.

Project Overview   
This project focuses on:   
✅ Setting up a GitHub repository    
✅ Writing a basic Python function to print the app version    
✅ Creating a Docker container for the app   
✅ Running and testing the container locally    

Project Setup & Execution    
1. Clone the Repository    
git clone https://github.com/Ayushi024/HiveBox-DevOps-.git    
cd HiveBox-DevOps-     

2. Run the Application Locally    
python app.py                         

3. Dockerize the Application                      
a) Build the Docker Image                 
docker build -t hivebox-dev .                 
b) Run the Docker Container                    
docker run --rm hivebox-dev               
Expected Output:             
App Version: v0.0.1            
