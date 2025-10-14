# FROM python:3.11

# Tells OBS how to tag the final image in the registry.
#!BuildTag: opensuse/grove_barometer:latest opensuse/grove_barometer:%PKG_VERSION%

# Use the SUSE Base Container Image for Python 3.11
# https://registry.opensuse.org/cgi-bin/cooverview
FROM opensuse/bci/python:3.11

# Define labels according to openSUSE and OCI standards.
# The 'labelprefix' helps avoid repetition but is optional.
# labelprefix=org.opensuse.grove_barometer
LABEL org.opencontainers.image.title="Grove Barometer Container"
LABEL org.opencontainers.image.description="A container for running the Grove Barometer Python application."
LABEL org.opencontainers.image.version="%PKG_VERSION%.%RELEASE%"
LABEL org.opensuse.reference="registry.opensuse.org/home:llansky3/grove_barometer:%PKG_VERSION%.%RELEASE%"
LABEL org.openbuildservice.disturl="%DISTURL%"
LABEL org.opencontainers.image.created="%BUILDTIME%"
# endlabelprefix

# Additional required packages
# RUN apt-get update && apt-get install -y PACKAGE_HERE

# Python wrapper application
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY barometer.py .
CMD ["python3", "barometer.py"]

# To build it:
# docker build -t barometer-app .

# To run it:
# docker run -d --name barometer -v $(pwd)/.env:/app/.env:ro --restart unless-stopped barometer-app