# FlyFast - Data Generator

This repository contains the source code for the Load Generator of FlyFast.

To view the full source code and to run the whole application through Docker, head over to [FlyFast](https://github.com/Aternity/FlyFast).

## Requirements

1. [Git](https://git-scm.com/) (Optional)
2. a Docker host, for example [Docker Desktop](https://www.docker.com/products/docker-desktop) (Optional)
3. [Python 3.7](https://www.python.org/downloads/release/python-370/) (Required)
4. [WebUI](https://github.com/Aternity/FlyFast-WebUI) (Required Only For Having A UI)
5. [FlightSearch](https://github.com/Aternity/FlyFast-FlightSearch) (Required Only For Making Backend Calls)

## Getting Started
1. You can either start the application using [Python](#step-by-step-using-python) or [Docker](#step-by-step-using-docker).

## Step by Step Using Python
1. Start the application.
    ```
    py main.py -host localhost -p 80 -steps 10 20 30 40 30 20 -num_minutes 2
    ```

## Step by Step Using Docker
1. Build our docker:
    ```
    docker build . -t flyfast-load-generator
    ```
2. Run our docker container:
    ```
    docker run --rm -e FLYFAST_HOST_URL=http://localhost -e FLYFAST_HOST_PORT=80 flyfast-load-generator
    ```