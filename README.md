# 553FinalBackend

This is a client-side back-end monitoring application written in Python using the Flask framework using the psutil library that gathers system data and uses HTTP GET requests to send them in the 
form of JSON response bodies.

The steps to setup the application are as follows:
1) After cloning the repo, cd into the folder and run this command: 'sudo docker image build -t flask_docker .'
2) The docker build command takes two environment variables, PORT (Defaults to 5009) and CONFIG (Defaults to log_config.txt, already included in the repo).
3) After installing the required dependencies, run the command 'sudo docker run flask_docker' to run the server in command line
4) After the server begins running, localtunnel will display the internet-facing URL of the server, which you can copy, and then replace it in the front-end dashboard

The log_config.txt file can be changed by appending the absolute path to the desired log as a key-value pair in the [Logs] section.
Additionally, the modules /network_info (hostname=), /process_info (length=), and /logs_info (length=) take optional URL parameters.
