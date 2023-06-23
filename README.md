# GoodWe Solar inverter

A wifi enabled Goodwe Solar Inverter XS-series via a wifi network.  

- [Python goodwe module](https://github.com/marcelblijleven/goodwe)


# Docker container

The container connects to the Goodwe Solar Inverter on port UDP/8899.  
It reads the values every 30 seconds.  
The readings are exported to InfluxDB and/or stdout (container logging), check variables *ENABLE_LOGGING* and *ENABLE_INFLUXDB*.  

The container uses the following variables, some are mandatory:  

Required environment variables (no defaults):  
- `INFLUXDB_HOSTNAME`: hostname or ip-address of influxdb server
- `INFLUXDB_TOKEN`: token with write-access to influxdb bucket
- `INFLUXDB_ORG`: influxdb organization
- `INVERTER_HOSTNAME`: hostname or ip-address of the GoodWe Solar inverter

Optional environment variables:  
- `INFLUXDB_PORT`: TCP-port of InfluxDB server, default: *8086*
- `INFLUXDB_BUCKET`: bucketname to store data in InfluxDB

Optional environment variables for debugging:  
- `ENABLE_LOGGING`: *true* (log p1 data to stdout) or *false* (no p1 data to stdout, default)
- `ENABLE_INFLUXDB`: *true* (write p1 data to InfluxDB, default) or *false* (do not write to InfluxDB)

## Build the container image

```
docker build -t solar2influx:1.0.1 .
```

or [download from Dockerhub](https://hub.docker.com/r/jaccol/solar2influx).  

### Cross-platform building

On Apple Silicon you can build an amd64 container with
```
docker buildx build --platform linux/amd64 --push -t jaccol/solar2influx:1.0.1 .
```

## Run the container

Because some variables are mandatory, you can use a environment file to make
variables available to the container.  
Do NOT use single/double quotes, because the quotes will be included in the values.  

Example *envfile*:
```
# Mandatory variables
INFLUXDB_HOSTNAME=influxdb.mydomain
INFLUXDB_TOKEN=ThisTokenIsGeneratedAtTheInfluxDBhostAndGivesWriteAccessToTheBucketToStoreSolarData
INFLUXDB_ORG=Home
P1METER_HOSTNAME=solar.mydomain
# Optional variables
#INFLUXDB_PORT=8086
#INFLUXDB_BUCKET=solar
#ENABLE_LOGGING=false
#ENABLE_INFLUXDB=true
```

Execute the container with:
```
docker run -d --env-file envfile solar2influx:1.0.1
```

## Python requirements

Version:  
- >= 3.x
- tested with 3.9.2

Modules:
- asyncio
- goodwe
- influxdb-client
