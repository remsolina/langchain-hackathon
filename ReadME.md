# Project Setup & Execution Guide

Welcome to our group hackathon project! This guide will help you set up the environment, create the necessary database, and run the application that performs Mentee→Preceptor matching with LangChain and ChromaDB.

## 1. Create a Conda Environment

1. Make sure you have [Anaconda](https://www.anaconda.com/products/distribution) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed.
2. Open your terminal or Anaconda Prompt, navigate to the project folder, and create a new environment:

   ```bash
   conda create -n my_mentor_match_env python=3.9

2. Activate the environment:

```bash
conda activate my_mentor_match_env
export PATH=/opt/anaconda3/envs/my_mentor_match_env/bin:$PATH

```
# 2. Install Dependencies

Inside your activated environment, install all required packages:
```bash
pip install -r requirements.txt
````
If you have additional packages to install or want to pin different versions, update the requirements.txt accordingly. 

# 3. Set Up MySQL Credentials

1. In utils/db_connection.py and create_dummy_data.py, locate this section:
```bash
connection = pymysql.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", "password"),  # Replace "password"!
    database=os.getenv("MYSQL_DB", "mentee_db"),
    ...
)
```
2. Replace "password" with your own MySQL Workbench or local MySQL root password (or another valid MySQL user’s password).
3. If desired, also adjust MYSQL_DB, MYSQL_USER, or other parameters to match your local environment.
4. Alternatively, you can set environment variables. For example (Linux/macOS/bash):
```bash
export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PASSWORD=YourSecurePassword
export MYSQL_DB=mentee_db
```
# 4. Add Your OpenAI API Key
Inside app.py:
1. We’ll be using OpenAI embeddings, so you need to provide an API key.
2. If you are given a key (e.g., on Discord), set it as an environment variable:
```bash
export OPENAI_API_KEY="sk-YourOpenAIKey..."
```
Or, if you prefer, you can place it directly in the code in app.py.
# 5. Create and Populate the Database

1. Run the script that creates (if needed) your MySQL database and populates it with dummy mentee data:
```bash
python create_dummy_data.py
```
2. This script will:
* Connect to MySQL using the credentials you configured.

* Create a database named mentee_db (or your MYSQL_DB env variable) if it doesn’t exist.

* Create a mentees table if it doesn’t exist.

* Insert three sample rows with dummy data.

# 6. Run the Application

Finally, launch the FastAPI server with Uvicorn. In your project folder (still in your conda env):
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
The application will:
* Load or create the Chroma vector database from the preceptors.pdf.
* Listen on port 8000 for requests (e.g., http://localhost:8000).
# 7. Test the Matching Endpoint

1. Open your browser or use a tool like Postman or cURL to call the endpoint:
GET http://localhost:8000/match_mentor/1
2. You should see a JSON response containing the best‐fit preceptor(s) for the mentee with id=1. You can always chnage this to 2 or 3 depending on the mentee_id you're parsing

# Troubleshooting
* Cannot connect to MySQL: Ensure MySQL is running locally and your credentials (host, user, password) match your setup.
* OPENAI_API_KEY not set: Make sure you’ve correctly set your environment variable or replaced it in app.py.
* Chroma DB issues: If you see an empty store error, the code will rebuild the store. You might need to delete the persistent folder in embeddings/chromadb if you want a clean start.