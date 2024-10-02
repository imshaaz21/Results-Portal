# Results Portal
A Streamlit-based web app for displaying student results.

## Local Setup
1. Clone the repository:
2. Install the required packages:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
````
3. Set the environment variables:
```bash
  export ADMIN_PASSWORD="admin"
```
4. Run the app:
```bash
streamlit run app.py
```

## Docker Setup
1. Build the Docker image:
```bash
docker build -t results-portal .
```
2. Run the Docker container:
```bash
docker run -p 8501:8501 -e ADMIN_PASSWORD="admin" results-portal
```

### Environment Variables
ADMIN_PASSWORD: Set this variable to the desired admin password.
