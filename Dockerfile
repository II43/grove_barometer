FROM python:3.11
# Additional required packages
# RUN apt-get update && apt-get install -y PACKAGE_HERE

# Python wrapper application
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY barometer.py .
CMD ["python3", "barometer.py"]

# To build it:
# docker build -t barometer-app .

# To run it:
# docker run -d --name barometer -v $(pwd)/.env:/app/.env:ro barometer-app