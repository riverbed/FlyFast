# FlyFast

This cookbook contains the full source code for FlyFast, utilizing both the [FlyFast-WebUI](https://github.com/riverbed/FlyFast-WebUI) and [FlyFast-FlightSearch](https://github.com/riverbed/FlyFast-FlightSearch) to demonstrates how works [OpenTelemetry](https://opentelemetry.io/) with [Riverbed APM](https://www.riverbed.com/products/application-performance-monitoring/).

![diagram](/images/Riverbed-FlyfFast-diagram.png)

> [!NOTE]
> The FlyFast demo app is instrumented with OpenTelemetry configured to send the OpenTelemetry traces to the [APM OpenTelemetry Collector](https://hub.docker.com/r/aternity/apm-collector), which in turns exports traces to the Riverbed APM backend (whether APM SaaS or APM Analysis Server).
> In the app, both the WebUI frontend and the FlighSearch API backend are instrumented: the frontend instrumentation uses an experimental OpenTelemetry for Javascript in the browser, and the FlightSearch API uses OpenTelemetry for Python. 

## Prerequisites

1. an APM SaaS account, or an APM Analysis Server
2. *optional* an account for Aternity UJI
3. a Docker host, for example [Docker Desktop](https://www.docker.com/products/docker-desktop)
4. git ([Git](https://git-scm.com/))

## Step 1. Get a local copy
    
```shell
git clone --recurse-submodules https://github.com/riverbed/FlyFast.git --depth 1
```

## Step 2. Get your information for Riverbed APM

Open the APM web console and navigate to Agents > Install Agents (for example [https://apm.myaccount.aternity.com](https://apm.myaccount.aternity.com))

1. Grab the **Analysis Server Host**, for example *agents.apm.myaccount.aternity.com*
2. Find your **CustomerID**, for example *12341234-12341234-13241234*

Those information are required to activate the [APM OpenTelemetry Collector](https://hub.docker.com/r/aternity/apm-collector) with an APM  account.
The CustomerID is not required when it is not an APM SaaS.

## Step 3. *optional* Get your information for Aternity UJI

<details>
  <summary>*optional* See details for Aternity UJI</summary>


1. Open [Aternity UJI](https://portals.bluetriangle.com) and navigate to Settings & Administration > Sites
2. Find the site configured for FlyFast and get the **UJI Tag Prefix**, for example *my-UJI-Tag-Prefix-FlyFast*

</details>

## Step 4. Start the containers

Start the containers using the [docker-compose.yaml](docker-compose.yaml), using the snipppet below
and replacing the values with the information collected at step 2. and step 3.

For example in Bash:

```bash
cd FlyFast

# Configure the APM OpenTelemetry Collector
export RIVERBED_APM_SERVER_HOST="agents.apm.myaccount.aternity.com"
export RIVERBED_APM_CUSTOMER_ID="12341234-12341234-13241234"

# Start the containers
docker compose up
```

or in PowerShell:

```PowerShell
cd FlyFast

# Configure the APM OpenTelemetry Collector
$env:RIVERBED_APM_SERVER_HOST="agents.apm.myaccount.aternity.com"
$env:RIVERBED_APM_CUSTOMER_ID="12341234-12341234-13241234"

# Start the containers
docker-compose up
```

<details>
  <summary>*optional* Add configuration for Aternity UJI</summary>

in Bash:

```bash
cd FlyFast

# Configure the APM OpenTelemetry Collector
export RIVERBED_APM_SERVER_HOST="agents.apm.myaccount.aternity.com"
export RIVERBED_APM_CUSTOMER_ID="12341234-12341234-13241234"

# Optional - Configure the Aternity UJI tag
# Replace "my-UJI-Tag-Prefix-FlyFast" with your UJI Tag Prefix collected at step 3.
export ALLUVIO_UJI_TAG='<script id=\"ALLUVIO-Aternity-UJI\" src=\"https:\/\/your-UJI-Tag-Prefix-FlyFast\.btttag\.com\/btt\.js\"><\/script>'

# Start the containers
docker compose up
```

or in PowerShell

```PowerShell
cd FlyFast

# Configure the APM OpenTelemetry Collector
# Replace the value with your information collected at step 2.
$env:RIVERBED_APM_SERVER_HOST="agents.apm.myaccount.aternity.com"
$env:RIVERBED_APM_CUSTOMER_ID="12341234-12341234-13241234"

# Optional - Configure the Aternity UJI tag
# Replace "your-UJI-Tag-Prefix-FlyFast" with your UJI Tag Prefix collected at step 3.
$env:ALLUVIO_UJI_TAG='<script id=\"ALLUVIO-Aternity-UJI\" src=\"https:\/\/your-UJI-Tag-Prefix-FlyFast\.btttag\.com\/btt\.js\"><\/script>'

# Start the containers
docker-compose up
```

</details>

## Step 5. Navigate through The Application And Monitor

The web application should now be available on [http://localhost](http://localhost).

Open the url in your browser and navigate through the application a few times to generate page views and transaction that will be monitored by APM.

## Step 6. Open Riverbed APM web console

Go to the APM web console to monitor the instance and observe every transaction.

![APM OpenTelemetry Traces](/images/transaction.png)

View details of a specific transaction as a waterfall chart:

![APM OpenTelemetry Transaction-Detail](/images/transaction-detail.png)


## Notes

<details>
  <summary>See Notes</summary>


### Add Synthetic Test

In the [Riverbed Community Toolkit](https://github.com/riverbed/Riverbed-Community-Toolkit), the cookbook [Synthetic-004-Browse-FlyFast](https://github.com/riverbed/Riverbed-Community-Toolkit/tree/master/NetIM/Synthetic-Test/Synthetic-004-Browse-FlyFast) show how to set up a synthetic test for FlyFast on a Windows machine.

### Stop The App and All The Containers

Press `CTRL + C` in the shell where it is running.

Or in a shell, go to the folder where you keep the [docker-compose.yml](docker-compose.yml) and run:

```shell
docker-compose stop
```

### Rebuild

```shell
docker compose build --no-cache
```

### Updating Based On Future Changes

Stay up to date with the latest changes.

```shell
git submodule update --remote
```

### Clone FlyFast and update submodules

```shell
git clone https://github.com/riverbed/FlyFast.git
cd FlyFast
git submodule init
git submodule update
```

</details>

## License
Copyright (c) 2022 - 2024 Riverbed Technology, Inc.

The contents provided here are licensed under the terms and conditions of the MIT License accompanying the software ("License"). The scripts are distributed "AS IS" as set forth in the License. The script also include certain third party code. All such third party code is also distributed "AS IS" and is licensed by the respective copyright holders under the applicable terms and conditions (including, without limitation, warranty and liability disclaimers) identified in the license notices accompanying the software.
