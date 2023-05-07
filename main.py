import json
import os
import subprocess
import re
from datetime import datetime

import psutil
from flask import Flask, request
from ping3 import ping, verbose_ping

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
    cpu_load = psutil.cpu_percent(interval=None)

    data = {
        "timestamp": date_time,
        "cpu_count": cpu_count,
        "cpu_load": cpu_load,
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

    mem_usage_percent = psutil.virtual_memory()[2]
    mem_usage = psutil.virtual_memory()[3]
    data = {
        "timestamp": date_time,
        "mem_usage_percent": mem_usage_percent,
        "mem_usage": get_size(mem_usage)
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
    data = {
        "timestamp": date_time,
        "total_disk_usage": get_size(disk_stats[0]),
        "used_disk_usage": get_size(disk_stats[1]),
        "free_disk_usage": get_size(disk_stats[2]),
        "percent_disk_usage": disk_stats[3]
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

    data = {
        "timestamp": date_time,
        "avg_latency": avg_latency,
        "nic_data": nic_list,
        "net_connections": connection_list
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

    process_iterator = psutil.process_iter(['pid', 'name', 'username', 'cpu_percent'])
    process_list = []
    for process in process_iterator:
        pinfo = process.as_dict(attrs=['pid', 'name', 'username', 'status'])
        pinfo['vms'] = get_size(process.memory_info().vms)
        pinfo['cpu_time'] = sum(process.cpu_times()[:2])
        process_list.append(pinfo)

    sorted_process_list = sorted(process_list, key=lambda procObj: procObj['cpu_time'], reverse=True)
    sorted_process_list = sorted_process_list[:10]
    data = {
        "timestamp": date_time,
        "process_list": sorted_process_list
    }

    response = app.response_class(response=json.dumps(data),
                                  status=200,
                                  mimetype='application/json')
    return response


@app.route("/logs_info")
def get_logs_info():
    current_time = datetime.now()
    time_stamp = current_time.timestamp()
    date_time = str(datetime.fromtimestamp(time_stamp))

    process_iterator = psutil.process_iter(['pid', 'name', 'username', 'cpu_percent'])
    process_list = []
    for process in process_iterator:
        pinfo = process.as_dict(attrs=['pid', 'name', 'username', 'status'])
        pinfo['vms'] = get_size(process.memory_info().vms)
        pinfo['cpu_time'] = sum(process.cpu_times()[:2])
        process_list.append(pinfo)

    sorted_process_list = sorted(process_list, key=lambda procObj: procObj['cpu_time'], reverse=True)
    sorted_process_list = sorted_process_list[:10]
    data = {
        "timestamp": date_time,
        "process_list": sorted_process_list
    }

    response = app.response_class(response=json.dumps(data),
                                  status=200,
                                  mimetype='application/json')
    return response
