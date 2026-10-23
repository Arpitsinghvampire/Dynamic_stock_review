
# 1. Choose the base Python environment
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /dynamic_websearch

# 3. Copy the dependency list
COPY requirements.txt .

# 4. Install all required libraries
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the project files
COPY . .

#port for running the streamlit 
EXPOSE 8501 


# 6. Start the application
CMD ["streamlit" , "run", "rag_agent.py" , "--server.address=0.0.0.0"]
