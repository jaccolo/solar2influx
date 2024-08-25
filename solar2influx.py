#!/usr/bin/env python3
#
# Required environment variables (no defaults):
# - INFLUXDB_HOSTNAME: hostname or ip-address of influxdb server
# - INFLUXDB_TOKEN: token with write-access to influxdb bucket
# - INFLUXDB_ORG: influxdb organization
# - INVERTER_HOSTNAME: hostname or ip-address of GoodWe solar inverter
# Optional environment variables:
# - INFLUXDB_PORT: TCP-port of InfluxDB server, default: 8086
# - INFLUXDB_BUCKET: bucketname to store data in InfluxDB, default: solar
# - SCAN_INTERVAL: interval in seconds to access the inverter, default: 30
# Optional environment variables for debugging:
# - ENABLE_LOGGING: true (log data to stdout) or false (no data to stdout, default)
# - ENABLE_INFLUXDB: true (write data to InfluxDB, default) or false (do not write to InfluxDB)

import os
import sys
import time
import datetime
import asyncio
import goodwe
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

async def get_runtime_data(inverterhost):

    # runtime_data example:
    # {'timestamp': datetime.datetime(2023, 6, 19, 20, 51, 57), 'vpv1': 313.3, 'ipv1': 0.5, 'ppv1': 157, 
    # 'vpv2': 0.0, 'ipv2': 0.0, 'ppv2': 0, 'vline1': -0.1, 'vgrid1': 232.9, 'igrid1': 1.0, 'fgrid1': 50.02, 
    # 'pgrid1': 233, 'ppv': 182, 'work_mode': 1, 'work_mode_label': 'Normal', 'error_codes': 0, 
    # 'warning_code': 0, 'temperature': 36.9, 'e_day': 19.2, 'e_total': 8863.7, 'h_total': 11486, 
    # 'safety_country': 20, 'safety_country_label': 'Holland', 'funbit': 320, 'vbus': 374.9, 'vnbus': -0.1}

    try:
        inverter = await goodwe.connect(inverterhost)
        runtime_data = await inverter.read_runtime_data()
        return runtime_data
    except Exception as e:
        print(f"Warning: error reading from solar inverter {inverterhost}: {e}", file=sys.stderr)

def write_influx(influxserver, influxport, influxorg, influxtoken,influxbucket, enable_logging, enable_influxdb, inverterdata):

    if enable_influxdb == "TRUE":
        try:
            influxdbclient = InfluxDBClient(url=f"http://{influxserver}:{influxport}", token=influxtoken, org=influxorg)
            write_api = influxdbclient.write_api(write_options=SYNCHRONOUS)
            _p1 = Point("vpv1").field("volt", inverterdata.get('vpv1'))
            _p2 = Point("ipv1").field("ampere", inverterdata.get('vpv1'))
            _p3 = Point("ppv1").field("watt", inverterdata.get('ppv1'))
            _p4 = Point("vpv2").field("volt", inverterdata.get('vpv2'))
            _p5 = Point("ipv2").field("ampere", inverterdata.get('vpv2'))
            _p6 = Point("ppv2").field("watt", inverterdata.get('ppv2'))
            _p7 = Point("vline1").field("volt", inverterdata.get('vline1'))
            _p8 = Point("vgrid1").field("volt", inverterdata.get('vgrid1'))
            _p9 = Point("igrid1").field("ampere", inverterdata.get('igrid1'))
            _p10 = Point("fgrid1").field("hz", inverterdata.get('fgrid1'))
            _p11 = Point("pgrid1").field("watt", inverterdata.get('pgrid1'))
            _p12 = Point("ppv").field("watt", inverterdata.get('ppv'))
            _p13 = Point("h_total").field("hours", inverterdata.get('h_total'))
            _p14 = Point("e_total").field("kwh", inverterdata.get('e_total'))
            _p15 = Point("e_day").field("kwh", inverterdata.get('e_day'))
            write_api.write(bucket=influxbucket, org=influxorg, record=[_p1, _p2, _p3, _p4, _p5, _p6, _p7, _p8, _p9, _p10, _p11, _p12, _p13, _p14, _p15])           
            influxdbclient.__del__()
        except Exception as e:
            print(f"Fatal error accessing InfluDB: {e}", file=sys.stderr)

    if enable_logging == "TRUE":
        print(f"Date + time: {inverterdata.get('timestamp')}")
        print(f"PV1 Voltage (V) (vpv1): {inverterdata.get('vpv1')}")
        print(f"PV1 Current (A) (ipv1): {inverterdata.get('ipv1')}")
        print(f"PV1 Power (W) (ppv1): {inverterdata.get('ppv1')}")
        print(f"PV2 Voltage (V) (vpv2): {inverterdata.get('vpv2')}")
        print(f"PV2 Current (A) (ipv2): {inverterdata.get('ipv2')}")
        print(f"PV2 Power (W) (ppv2): {inverterdata.get('ppv2')}")
        print(f"On-grid L1-L2 Voltage (V) (vline1): {inverterdata.get('vline1')}")
        print(f"Grid Voltage (V) (vgrid1): {inverterdata.get('vgrid1')}")
        print(f"Grid Current (A) (igrid1): {inverterdata.get('igrid1')}")
        print(f"Grid Frequency (Hz) (fgrid1): {inverterdata.get('fgrid1')}")
        print(f"Grid Power (W) (pgrid1): {inverterdata.get('pgrid1')}")
        print(f"PV Power (W) (ppv): {inverterdata.get('ppv')}")
        print(f"Temperature (degrees celcius) (temperature): {inverterdata.get('temperature')}")
        print(f"Total hours (hours) (h_total): {inverterdata.get('h_total')}")
        print(f"Total load (kWH) (e_total): {inverterdata.get('e_total')}")
        print(f"Today's load (kWH) (e_day): {inverterdata.get('e_day')}")
        if enable_influxdb == "TRUE":
            print(f"==> Data written to InfluxDB host {influxserver}")


def main():

    # Required environment variables
    try:
        influxserver = os.environ['INFLUXDB_HOSTNAME']
        influxorg = os.environ['INFLUXDB_ORG']
        influxtoken = os.environ['INFLUXDB_TOKEN']
        inverterhost = os.environ['INVERTER_HOSTNAME']
    except KeyError as e:
        print(f"Fatal error: variable not set: {e}", file=sys.stderr)
        sys.exit(1)

    # Variables with a default value
    influxport = os.environ.get('INFLUXDB_PORT', 8086)
    influxbucket = os.environ.get('INFLUXDB_BUCKET', 'solar')
    enable_logging = str(os.environ.get('ENABLE_LOGGING', 'false')).upper()
    enable_influxdb = str(os.environ.get('ENABLE_INFLUXDB', 'true')).upper()
    scan_interval = os.environ.get('SCAN_INTERVAL', 30)

    while True:
        
        ret = os.system(f"ping -c 3 -W 3000 {inverterhost} >/dev/null 2>&1")
        if ret == 0:
            try:
                inverterdata = asyncio.run(get_runtime_data(inverterhost))
            except Exception as e:
                print(f"Error reading from solar inverter {inverterhost}: {e}", file=sys.stderr)
            try:
                write_influx(influxserver, influxport, influxorg, influxtoken, influxbucket, enable_logging, enable_influxdb, inverterdata)
            except Exception as e:
                print(f"Error writing to influxdb server {influxserver}: {e}", file=sys.stderr)
        else:
            ts = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
            print(f"{ts} - Error connecting to solar inverter {inverterhost}", file=sys.stderr)
        
        time.sleep(scan_interval)


if __name__ == "__main__":
    main()

