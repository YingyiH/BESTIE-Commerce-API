FROM python:3.11

LABEL maintainer="hedoris8@gmail.com"

WORKDIR /Receiver/

COPY . .

# Install Python and Pip
RUN apt-get update -y && apt-get install -y python3 python3-pip
# Install Python dependencies
RUN pip3 install -r ./requirements.txt

# Expose the port on which your application will run
EXPOSE 8080

ENTRYPOINT [ "python3" ]

# Command to run your application
CMD ["app.py"]