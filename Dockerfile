# start by pulling the python image
FROM python:3.8-alpine

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

#Required for psutil
RUN apk add musl-dev
RUN apk add py-configobj libusb py-pip python3-dev gcc linux-headers
RUN pip install --upgrade pip
# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt
RUN apk add --update nodejs npm
RUN npm install -g localtunnel
# copy every content from the local file to the image
COPY . /app

# configure the container to run in an executed manner
ENV PORT=5009
ENV CONFIG=log_config.txt
STOPSIGNAL SIGINT
CMD ["sh", "-c", "python main.py -config $CONFIG -port $PORT"]
