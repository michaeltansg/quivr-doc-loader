# Use an official Python runtime as a parent image
FROM python:3.11-buster

# Set the working directory in the container to /app
WORKDIR /app

# Add metadata to the image to describe that the container is listening on the specified port at runtime.
EXPOSE 22

# Copy the current directory contents into the container at /app
COPY . /app

# Install Tesseract
RUN apt-get update && apt-get install -y tesseract-ocr && apt-get install -y libtesseract-dev

# Install Poppler
RUN apt-get install -y libpoppler-cpp-dev

# Install Poppler Utils
RUN apt-get install -y poppler-utils

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt --timeout 100

# Create a new user with bash as their default shell.
RUN useradd -ms /bin/bash user

# Install openssh-server and bash.
RUN apt-get update && apt-get install -y openssh-server

# Set up SSH. You may want to configure this differently in a real setup.
RUN mkdir /var/run/sshd
RUN echo 'user:password' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

# Run sshd
CMD ["/usr/sbin/sshd", "-D"]