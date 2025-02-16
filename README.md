# Merlin AI

Explain Merlin AI here
---

## Getting Started

### Prerequisites

- **Docker Desktop:**  
  [Download and install Docker Desktop](https://www.docker.com/products/docker-desktop) and make sure it's running.

- **Repository Cloning Options:**
  - **Preferred:** Use GitHub Desktop or the command-line Git tool.
  - **Alternative:** Directly download the repository as a ZIP file.

### Steps

[Copy the template by clicking this link](https://github.com/new?template_name=merlin-ai&template_owner=jacoby149)

1. **Create or Download Your Repository:**  
   - **Self-Clone with Template:**  
     Click the button above to automatically create a new repository based on the template. Then go to your 
     repository and clone that repo locally!
     
   - **Download ZIP (The Easy Way For Non Software Developers)**  
     If you don’t have Git installed, download the repository as a ZIP file using this URL:  
     [Download ZIP](https://github.com/jacoby149/merlin-ai/archive/refs/heads/main.zip)  
     *Note: Adjust the branch name if needed.*

2. **Set Up Your Local Environment:**  
   - **If Cloning:**  
     Clone your repository using:
     ```bash
     git clone https://github.com/<your-username>/<your-repo>.git
     ```
   - **If Using the ZIP File:**  
     Extract the ZIP file to your desired directory.

3. **Run the Application:**

   #### For CLI Users:
   Open your terminal, navigate into your repository directory, and run:
   ```bash
   docker compose up --build
   ```
   
   #### For Non-CLI Users:
   We've included executable scripts for a more user-friendly experience:

   Windows Users:
   Double-click the start.bat file included in the repository. This batch file will open a terminal and run the 
   command automatically.
  
  macOS/Linux Users:
  Double-click the start.command file included in the repository. (If needed, mark it as executable by running 
  chmod +x start.command in Terminal.)
  
4. Access Your App:
  Once the build is complete, open your web browser and visit: http://localhost:3001
