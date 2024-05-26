# Use an official Python runtime as a parent image
FROM python:3.11-slim
# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY /backend /app
RUN ls -la /*
# Run the command to install any necessary dependencies
RUN pip install --no-cache-dir -U pydantic fastapi uvicorn pyautogui spotipy rich mutagen starlette 
EXPOSE 8000
CMD python main.py