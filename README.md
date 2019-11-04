# HydroQuality
HydroQuality is an open-source web applciation for the simple configuration and execution of quality control tests for tabular time-series data. With a clean interface and a simple 6 step process this application should be usable by any researchers regardless of technical ability. By hosting it online, this software represents a necessary evolution of solutions like the GCE Toolbox or custom scripts which can only be run on desktop machines and are not accessible anywhere.

## This Repository
This repository contains the source code for this software. It is currently under development however, our most recent working build is available on the master branch. If you would like to download and host this software on a local server or on your desktop please follow the installation instructions.

## Installation
Many dependencies for this software are contained and managed inside of the docker containers provided in this repository. However, to create these containers you will require:
* [docker](https://docs.docker.com/get-started/)
* [docker-compose](https://docs.docker.com/compose/gettingstarted/)

### Instructions
On a machine that supports docker:

1. Open a command prompt/ terminal application
2. Navigate to Backend/Infrastructure/ComposeFiles/ from the project root directory
3. Type the following into your command window:
```
docker-compose up -d
```
4. Navigate to localhost:7999 in a web browser to verify the installation.
5. Begin using the application.


