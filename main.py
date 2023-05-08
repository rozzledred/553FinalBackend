import configparser
import json
from datetime import datetime
import socket
import os
import re
import time
import shutil
from threading import Timer, Thread
import psutil
from file_read_backwards import FileReadBackwards
from flask import Flask, request, current_app
from flask_cors import CORS
from ping3 import ping
from contextlib import redirect_stdout

app = Flask(__name__)


def get_size(num_bytes):
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if num_bytes < 1024:
            return f"{num_bytes:.2f}{unit}B"
        num_bytes /= 1024


@app.route("/cpu_info")
def get_cpu_info():
    current_time = datetime.now()
    time_stamp = current_time.timestamp()
    date_time = str(datetime.fromtimestamp(time_stamp))

    cpu_count = os.cpu_count()
    cpu_load_avg = psutil.cpu_percent(interval=None)
    cpu_load = psutil.cpu_percent(interval=None, percpu=True)

    last_boot = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "host": socket.gethostname(),
        "timestamp": date_time,
        "cpu_count": cpu_count,
        "avg_cpu_load": cpu_load_avg,
        "last_boot": last_boot,
        "cpu_load_per_core": cpu_load
    }

    response = app.response_class(response=json.dumps(data),
                                  status=200,
                                  mimetype='application/json')
    return response


@app.route("/mem_info")
def get_mem_info():
    current_time = datetime.now()
    time_stamp = current_time.timestamp()
    date_time = str(datetime.fromtimestamp(time_stamp))

    memory_info = psutil.virtual_memory()

    data = {
        "host": socket.gethostname(),
        "timestamp": date_time,
        "current_memory_used": get_size(memory_info.used),
        "current_memory_free": get_size(memory_info.available),
        "memory_usage_percent": memory_info.percent,
        "total_available_memory": get_size(memory_info.total),
    }

    response = app.response_class(response=json.dumps(data),
                                  status=200,
                                  mimetype='application/json')
    return response


@app.route("/disk_info")
def get_disk_info():
    current_time = datetime.now()
    time_stamp = current_time.timestamp()
    date_time = str(datetime.fromtimestamp(time_stamp))

    disk_stats = psutil.disk_usage('/')
    total_disk_counters = psutil.disk_io_counters(perdisk=False)
    disk_counters = psutil.disk_io_counters(perdisk=True)
    disk_partitions = psutil.disk_partitions()

    partition_list = []
    for item in disk_partitions:
        part_dict = dict()
        part_dict['device'] = item.device
        part_dict['mount_point'] = item.mountpoint
        partition_list.append(part_dict)

    counter_list = []
    for disk in disk_counters.keys():
        part_dict = dict()
        part_dict['device'] = disk
        part_dict['read_count'] = disk_counters[disk].read_count
        part_dict['write_count'] = disk_counters[disk].write_count
        part_dict['bytes_read'] = get_size(disk_counters[disk].read_bytes)
        part_dict['bytes_written'] = get_size(disk_counters[disk].write_bytes)
        counter_list.append(part_dict)

    data = {
        "host": socket.gethostname(),
        "timestamp": date_time,
        "total_disk_usage": get_size(disk_stats[0]),
        "used_disk_usage": get_size(disk_stats[1]),
        "free_disk_usage": get_size(disk_stats[2]),
        "percent_disk_usage": disk_stats[3],
        "disk_num_reads": total_disk_counters.read_count,
        "disk_num_writes": total_disk_counters.write_count,
        "disk_read_bytes": get_size(total_disk_counters.read_bytes),
        "disk_write_bytes": get_size(total_disk_counters.write_bytes),
        "disk_partitions": partition_list,
        "disk_statistics": counter_list,
    }
    response = app.response_class(response=json.dumps(data),
                                  status=200,
                                  mimetype='application/json')
    return response


@app.route("/network_info")
def get_network_info():
    current_time = datetime.now()
    time_stamp = current_time.timestamp()
    date_time = str(datetime.fromtimestamp(time_stamp))

    hostname = 'google.com'

    if request.args.get("hostname"):
        hostname = request.args.get("hostname")

    avg_ping = round(ping(hostname, unit='ms'), 2)

    if not avg_ping:
        avg_latency = 'Hostname unreachable!'
    else:
        avg_latency = str(avg_ping) + "ms"

    io = psutil.net_io_counters(pernic=True)
    addrs = psutil.net_if_addrs()
    nic_list = []
    for nic in io.keys():
        nic_dict = dict()
        nic_dict['interface'] = nic

        address_list = []
        for item in addrs[nic]:
            address_list.append(item.address)

        nic_dict['address'] = address_list
        nic_dict['bytes_sent'] = get_size(io[nic].bytes_sent)
        nic_dict['bytes_recv'] = get_size(io[nic].bytes_recv)
        nic_list.append(nic_dict)

    net_connections = psutil.net_connections()

    connection_list = []
    for connection in net_connections:
        connection_dict = dict()
        if connection.raddr and connection.status:
            connection_dict['ip'] = connection.raddr.ip
            connection_dict['port'] = connection.raddr.port
            connection_dict['status'] = connection.status
            if connection.pid:
                connection_dict['pid'] = connection.pid
                curr_process = psutil.Process(connection.pid)
                connection_dict['process_name'] = curr_process.name()
            connection_list.append(connection_dict)

    current_users = psutil.users()
    current_user_list = []

    for user in current_users:
        current_user_dict = dict()
        current_user_dict['username'] = user.name
        current_user_dict['terminal'] = user.terminal
        current_user_dict['host'] = user.host
        start_time = str(datetime.fromtimestamp(user.started))
        current_user_dict['start_time'] = start_time
        current_user_list.append(current_user_dict)

    data = {
        "host": socket.gethostname(),
        "timestamp": date_time,
        "avg_latency": avg_latency,
        "nic_data": nic_list,
        "net_connections": connection_list,
        "connected_users": current_user_list
    }
    response = app.response_class(response=json.dumps(data),
                                  status=200,
                                  mimetype='application/json')
    return response


@app.route("/process_info")
def get_process_info():
    current_time = datetime.now()
    time_stamp = current_time.timestamp()
    date_time = str(datetime.fromtimestamp(time_stamp))

    process_list_length = 10

    if request.args.get("length"):
        process_list_length = request.args.get("length")

    process_iterator = psutil.process_iter(['pid', 'name', 'username', 'cpu_percent'])
    process_list = []
    for process in process_iterator:
        pinfo = process.as_dict(attrs=['pid', 'name', 'username', 'status'])
        pinfo['vms'] = get_size(process.memory_info().vms)
        pinfo['cpu_time'] = sum(process.cpu_times()[:2])
        process_list.append(pinfo)

    sorted_process_list = sorted(process_list, key=lambda process_object: process_object['cpu_time'], reverse=True)
    sorted_process_list = sorted_process_list[:process_list_length]
    data = {
        "host": socket.gethostname(),
        "timestamp": date_time,
        "process_list": sorted_process_list
    }

    response = app.response_class(response=json.dumps(data),
                                  status=200,
                                  mimetype='application/json')
    return response


@app.route("/logs_info")
def post_logs_info():
    current_time = datetime.now()
    time_stamp = current_time.timestamp()
    date_time = str(datetime.fromtimestamp(time_stamp))

    read_length = 10

    if request.args.get("length"):
        read_length = int(request.args.get("length"))

    config_path = current_app.config['file_path']

    config_parser = configparser.ConfigParser()
    config_parser.read(config_path)

    log_list = []
    for item in config_parser['Logs']:
        curr_path = config_parser['Logs'][item]

        curr_log_dict = dict()
        curr_log_dict['log_name'] = curr_path

        log_lines = []
        line_count = 0
        with FileReadBackwards(curr_path, encoding="utf-8") as frb:
            for log_line in frb:
                if line_count >= read_length:
                    break
                else:
                    log_lines.append(log_line)
                    line_count = line_count + 1

        curr_log_dict['log'] = log_lines
        log_list.append(curr_log_dict)

    data = {
        "host": socket.gethostname(),
        "timestamp": date_time,
        "config_paths": log_list
    }

    response = app.response_class(response=json.dumps(data),
                                  status=200,
                                  mimetype='application/json')
    return response


def run_lt_pipe(port: int, subdomain: str = None):
    if not shutil.which('lt'):
        os.system('npm install -g localtunnel')
    command = f'lt -p {port}'
    if subdomain != None:
        subdomain = subdomain.strip()
        subdomain = subdomain.replace('.', '-')
        subdomain = subdomain.replace(' ', '-')
        if re.match(r"^[\w-]+$", subdomain):
            command += f' -s {subdomain.lower()}'
    output = os.system(command + "> file.txt")
    return output


def run_lt(port: int, subdomain: str = None):
    if not shutil.which('lt'):
        os.system('npm install -g localtunnel')
    command = f'lt -p {port}'
    if subdomain != None:
        subdomain = subdomain.strip()
        subdomain = subdomain.replace('.', '-')
        subdomain = subdomain.replace(' ', '-')
        if re.match(r"^[\w-]+$", subdomain):
            command += f' -s {subdomain.lower()}'
    output = os.system(command)
    return output


def start_lt(port: int, subdomain: str = None):
    lt_adress = run_lt(port, subdomain)
    print(lt_adress)


def run_with_lt(app, subdomain: str = None):
    old_run = app.run

    def new_run(*args, **kwargs):
        port = kwargs.get('port', 5000)
        thread = Timer(1, start_lt, args=(port, subdomain,))
        thread.setDaemon(True)
        thread.start()
        old_run(*args, **kwargs)

    app.run = new_run


def find_url(output_file_path):
    while not os.path.exists(output_file_path):
        time.sleep(0.1)

    while os.path.getsize(output_file_path) <= 0:
        time.sleep(0.1)
    output_file = open(output_file_path, "r")
    text = output_file.read()
    url_regex = re.compile(r'https?://\S+')
    match = url_regex.search(text)
    if match:
        url = match.group()
        os.remove(output_file_path)
        print(url)
        return url


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-config', required=True)
    parser.add_argument('-port', required=True)
    args = parser.parse_args()
    file_path = args.config
    port = 5000
    if args.port:
        port = args.port

    app.config["file_path"] = file_path
    run_with_lt(app)
    CORS(app)

    url_send = False
    if url_send:
        thread = Thread(target=find_url, args=("file.txt",))
        thread.start()

    app.run(host='0.0.0.0', port=port)
