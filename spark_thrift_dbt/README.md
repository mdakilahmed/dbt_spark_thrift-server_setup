# **dbt Spark Project Setup Guide**

Welcome to the **dbt Spark Project**! This guide provides comprehensive instructions to set up and run your dbt project with Apache Spark using Docker and the Spark Thrift Server. You'll learn how to configure the environment, connect to Hive using Beeline, set up multiple environments, use PySpark in dbt models, and run dbt commands to manage your data transformations. Additionally, we'll cover setting up Elementary for data quality checks.

---

## **Table of Contents**

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
   - [Set Up Spark Thrift Server with Docker](#set-up-spark-thrift-server-with-docker)
   - [Connecting to Hive Using Beeline](#connecting-to-hive-using-beeline)
4. [dbt Project Initialization](#dbt-project-initialization)
   - [Create a New dbt Project](#create-a-new-dbt-project)
   - [Configure dbt Profile for Multiple Environments](#configure-dbt-profile-for-multiple-environments)
5. [dbt Models and Directory Structure](#dbt-models-and-directory-structure)
   - [Using PySpark in dbt Models](#using-pyspark-in-dbt-models)
6. [Setting Up Elementary for Data Quality Checks](#setting-up-elementary-for-data-quality-checks)
7. [Running dbt Commands](#running-dbt-commands)
8. [Conclusion](#conclusion)
9. [Appendix](#appendix)
   - [Common Issues and Solutions](#common-issues-and-solutions)
   - [References](#references)

---

## **Project Overview**

This guide helps you set up a dbt project using **Apache Spark** as the data warehouse. You'll use Docker to run a Spark Thrift Server, which allows dbt to connect to Spark via JDBC. By following these steps, you'll be able to initialize a dbt project, configure it for multiple environments, use PySpark in your models, set up data quality checks with Elementary, and run dbt commands to build and manage your data transformations.

---

## **Prerequisites**

- **Docker** (to run Spark Thrift Server)
- **Python** (version 3.7 or higher)
- **dbt-core** (compatible with your Python version)
- **dbt-spark** (dbt adapter for Spark)
- **Java Development Kit (JDK)** (required for Spark)
- **Beeline** (to connect to Hive)
- **Elementary Data** (for data quality checks)
- **PySpark** (for writing models in PySpark)

---

## **Environment Setup**

### **Set Up Spark Thrift Server with Docker**

We'll use Docker to run a Spark Thrift Server. The provided `docker-compose.yml`, `Dockerfile`, and `entrypoint.sh` files will set up the environment.

#### **1. Create the Project Directory**

Create a directory for your project and navigate into it.

```bash
mkdir dbt-spark-project
cd dbt-spark-project
```

#### **2. Create `docker-compose.yml`**

Create a `docker-compose.yml` file with the following content:

```yaml
version: '3.8'
services:
  spark-thrift-server:
    build: .
    ports:
      - "10000:10000"
    volumes:
      - ./sparkwarehouse:/opt/sparkwarehouse
      - ./data:/opt/data  # Mount the data directory
    container_name: spark-thrift-server
```

#### **3. Create `Dockerfile`**

Create a `Dockerfile` with the following content:

```dockerfile
# Use an official OpenJDK runtime as a parent image
FROM openjdk:8-jdk

# Set environment variables
ENV SPARK_VERSION=3.4.0
ENV HADOOP_VERSION=3
ENV SCALA_VERSION=2.12
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin

# Install necessary packages
RUN apt-get update && \
    apt-get install -y curl wget && \
    rm -rf /var/lib/apt/lists/*

# Download and extract Spark
RUN mkdir -p /opt && \
    wget -qO- https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz | \
    tar -xz -C /opt && \
    ln -s /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME}

# Expose necessary ports
EXPOSE 10000

# Set the working directory
WORKDIR ${SPARK_HOME}

# Copy entrypoint script
COPY entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/opt/entrypoint.sh"]
```

#### **4. Create `entrypoint.sh`**

Create an `entrypoint.sh` file with the following content:

```bash
#!/bin/bash

# Start Spark Thrift Server
${SPARK_HOME}/sbin/start-thriftserver.sh \
  --master local[*] \
  --conf spark.sql.warehouse.dir=file:///opt/sparkwarehouse \
  --conf spark.driver.memory=1g \
  --conf spark.executor.memory=1g \
  --conf spark.driver.bindAddress=0.0.0.0 \
  --packages org.apache.spark:spark-hive_${SCALA_VERSION}:${SPARK_VERSION}

# Keep the container running
tail -f /dev/null
```

Make sure the script is executable:

```bash
chmod +x entrypoint.sh
```

#### **5. Build and Run the Docker Container**

Build the Docker image and start the Spark Thrift Server.

```bash
docker-compose up -d
```

#### **6. Verify Spark Thrift Server is Running**

Check if the Spark Thrift Server is running by viewing the logs:

```bash
docker logs spark-thrift-server
```

### **Connecting to Hive Using Beeline**

Beeline is a command-line tool that allows you to connect to HiveServer2 (or the Spark Thrift Server) and execute HiveQL queries.

#### **1. Install Beeline (If Not Already Installed)**

Beeline is included with the Spark distribution. You can access it inside the Docker container or install it locally.

**To access Beeline inside the Docker container:**

```bash
docker exec -it spark-thrift-server /bin/bash
```

Once inside the container, you can run Beeline from the Spark home directory:

```bash
$SPARK_HOME/bin/beeline
```

#### **2. Connect to the Spark Thrift Server Using Beeline**

From within the container or your local installation, connect using the following command:

```bash
beeline -u "jdbc:hive2://localhost:10000"
```

#### **3. Execute HiveQL Commands**

Once connected, you can execute HiveQL commands to interact with your data.

**Example:**

```sql
SHOW DATABASES;
CREATE DATABASE IF NOT EXISTS my_database;
USE my_database;
CREATE TABLE test_table (id INT, name STRING);
INSERT INTO test_table VALUES (1, 'Alice'), (2, 'Bob');
SELECT * FROM test_table;
```

---

## **dbt Project Initialization**

### **Create a New dbt Project**

#### **1. Create a Virtual Environment**

It's recommended to use a virtual environment for your dbt project.

```bash
# Navigate to your project directory
cd dbt-spark-project

# Create a virtual environment
python -m venv dbt_venv
```

#### **2. Activate the Virtual Environment**

```bash
# On Unix or MacOS
source dbt_venv/bin/activate

# On Windows
dbt_venv\Scripts\activate
```

#### **3. Install dbt and Dependencies**

Install `dbt-core` and `dbt-spark`.

```bash
pip install --upgrade pip
pip install dbt-core dbt-spark[PyHive]
```

**Note:** The `[PyHive]` extra installs the `pyhive` package, which allows dbt to connect to Spark via the Hive Thrift Server.

#### **4. Initialize a New dbt Project**

Use the `dbt init` command to create a new project.

```bash
dbt init my_dbt_spark_project
```

#### **5. Navigate to the Project Directory**

```bash
cd my_dbt_spark_project
```

### **Configure dbt Profile for Multiple Environments**

To manage different environments—**development (dev)**, **quality assurance/testing (qat)**, and **production (prod)**—you need to configure your project to accommodate these environments.

#### **1. Update `profiles.yml`**

Edit the `profiles.yml` file to define multiple targets for each environment.

**Location of `profiles.yml`:**

- On Unix/MacOS: `~/.dbt/profiles.yml`
- On Windows: `%USERPROFILE%\.dbt\profiles.yml`

**Example Configuration:**

```yaml
my_dbt_spark_project:
  outputs:
    dev:
      type: spark
      method: thrift
      host: localhost
      port: 10000
      user: ''
      password: ''
      auth: NONE
      schema: dev_schema
      threads: 1

    qat:
      type: spark
      method: thrift
      host: qat-spark-thrift-server
      port: 10000
      user: ''
      password: ''
      auth: NONE
      schema: qat_schema
      threads: 1

    prod:
      type: spark
      method: thrift
      host: prod-spark-thrift-server
      port: 10000
      user: ''
      password: ''
      auth: NONE
      schema: prod_schema
      threads: 1

  target: dev  # Set default target environment
```

**Explanation:**

- **`outputs`**: Contains configurations for each environment (`dev`, `qat`, `prod`).
- **`schema`**: Specifies the schema (database) for each environment.
- **`target`**: Specifies the default environment.

#### **2. Set Environment Variables (If Necessary)**

If your environments require authentication, use environment variables to store sensitive information.

```bash
export DBT_DEV_USER='dev_user'
export DBT_DEV_PASSWORD='dev_password'
# Repeat for 'qat' and 'prod' environments
```

#### **3. Update `dbt_project.yml`**

Edit your `dbt_project.yml` file to configure model materializations and schemas per environment.

```yaml
# dbt_project.yml

name: 'my_dbt_spark_project'
version: '1.0.0'
profile: 'my_dbt_spark_project'

# Configuring file paths
model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

# Configuring models
models:
  my_dbt_spark_project:
    +schema: "{{ target.schema }}"
    +materialized: "{{ 'table' if target.name == 'prod' else 'view' }}"
```

**Explanation:**

- **`+schema`**: Uses the schema defined in the target environment.
- **`+materialized`**: Materializes models as tables in production and views in other environments.

---

## **dbt Models and Directory Structure**

Now that the dbt project is initialized and configured, you can start creating models, including those written in PySpark.

### **Project Directory Structure**

```
my_dbt_spark_project/
├── dbt_project.yml
├── models/
│   └── example/
│       ├── my_first_dbt_model.sql
│       └── my_pyspark_model.py
├── seeds/
├── analyses/
├── tests/
├── macros/
└── snapshots/
```

### **Using PySpark in dbt Models**

dbt allows you to write models in Python using PySpark. This is especially useful for complex transformations that are easier to express in Python than in SQL.

#### **1. Create a PySpark Model**

Create a file `models/example/my_pyspark_model.py` with the following content:

```python
# models/example/my_pyspark_model.py

def model(dbt, session):
    # dbt: The dbt object
    # session: The Spark session

    # Load a source table
    df = dbt.ref('my_first_dbt_model').toPandas()

    # Perform transformations using PySpark
    df['new_column'] = df['id'] * 2

    # Convert back to Spark DataFrame
    spark_df = session.createDataFrame(df)

    return spark_df
```

#### **2. Configure the PySpark Model**

Add a configuration block at the top of your Python model file:

```python
# models/example/my_pyspark_model.py

# Configuring the model
config(
    materialized='view'
)

def model(dbt, session):
    # Your code here
```

#### **3. Ensure Python Models Are Enabled**

In your `dbt_project.yml`, ensure that Python models are enabled:

```yaml
dispatch:
  - macro_namespace: dbt
    search_order: ['dbt', 'spark_python']
```

**Note:** As of dbt version 1.3 and above, Python models are supported for specific adapters like Spark.

---

## **Setting Up Elementary for Data Quality Checks**

Elementary is a data monitoring tool that helps in tracking data quality and anomalies. Follow the steps below to set up Elementary in your dbt project.

### **1. Add Elementary Package**

Create a `packages.yml` file in the root of your dbt project and add the following content:

```yaml
packages:
  - package: elementary-data/elementary
    version: 0.6.2
```

### **2. Update `dbt_project.yml`**

Add the Elementary configuration to your `dbt_project.yml`:

```yaml
models:
  elementary:
    +schema: "elementary"
```

### **3. Install Elementary and Run Models**

Install dependencies:

```bash
dbt deps
```

Run the Elementary models:

```bash
dbt run --select elementary
```

### **4. Generate the Elementary CLI Profile**

Generate the Elementary CLI profile:

```bash
dbt run-operation elementary.generate_elementary_cli_profile
```

This command will output the CLI profile configuration. Add it to your `~/.dbt/profiles.yml` file under a new profile named `elementary`.

### **5. Install the Elementary CLI**

Install the Elementary Data library for generating reports:

```bash
pip install elementary-data
```

Verify the installation:

```bash
edr --version
```

### **6. Run dbt Models and Generate Elementary Reports**

Create your dbt models in the `models/` directory and run them:

```bash
dbt run
dbt test
```

Generate an Elementary report:

```bash
edr report
```

This report provides insights into data quality, including anomalies, freshness, and test results.

---

## **Running dbt Commands**

With your dbt project set up, you can now run dbt commands to build and test your models.

### **Switching Between Environments**

Use the `--target` flag to specify the environment when running dbt commands.

**Examples:**

- **Development Environment:**

  ```bash
  dbt run  # Uses the default target (dev)
  ```

- **QAT Environment:**

  ```bash
  dbt run --target qat
  ```

- **Production Environment:**

  ```bash
  dbt run --target prod
  ```

### **dbt Compile**

Compile the project to ensure models are valid.

```bash
dbt compile
```

### **dbt Run**

Run models to build views/tables in the database.

```bash
dbt run
```

### **dbt Test**

Run tests defined in `schema.yml` files (if any).

```bash
dbt test
```

### **dbt Docs**

Generate and serve documentation.

```bash
dbt docs generate
dbt docs serve
```

---

## **Conclusion**

By following this guide, you've set up a dbt project using Apache Spark as the data warehouse, connected via a Spark Thrift Server running in a Docker container. You've configured the project for multiple environments, learned how to connect to Hive using Beeline, used PySpark in dbt models, and set up Elementary for data quality checks. You also ran dbt commands to build and manage your data transformations.

---

## **Appendix**

### **Common Issues and Solutions**

- **Connection Errors:**

  - **Issue:** Unable to connect to the Spark Thrift Server.
  - **Solution:** Ensure the Docker container is running and the ports are correctly mapped. Verify the `host` and `port` settings in your `profiles.yml`.

- **Authentication Errors:**

  - **Issue:** Authentication failure when connecting.
  - **Solution:** Check the `auth` method in `profiles.yml`. If authentication is not required, set `auth: NONE`.

- **Missing Dependencies:**

  - **Issue:** Errors related to missing Python packages.
  - **Solution:** Ensure you have installed `dbt-spark[PyHive]` to include the necessary dependencies for connecting via Thrift.

- **Spark Version Compatibility:**

  - **Issue:** Incompatibility between Spark versions.
  - **Solution:** Ensure the version of Spark in the Docker container matches the version expected by `dbt-spark`.

- **Beeline Connection Issues:**

  - **Issue:** Unable to connect to Hive using Beeline.
  - **Solution:** Check that the Spark Thrift Server is running and accessible. Verify the JDBC URL and network settings.

- **Elementary Setup Issues:**

  - **Issue:** Errors when running Elementary commands.
  - **Solution:** Ensure that the Elementary package version is compatible with your dbt version. Verify the configuration in `dbt_project.yml` and `profiles.yml`.

- **PySpark Model Errors:**

  - **Issue:** Errors when running PySpark models.
  - **Solution:** Ensure that your Spark environment supports Python models. Verify that the code in your `.py` files is correct and that all necessary packages are installed.

### **References**

- [dbt Documentation](https://docs.getdbt.com/)
- [dbt Spark Adapter Documentation](https://docs.getdbt.com/reference/warehouse-profiles/spark-profile)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [PyHive Documentation](https://github.com/dropbox/PyHive)
- [Docker Documentation](https://docs.docker.com/)
- [Beeline Documentation](https://cwiki.apache.org/confluence/display/Hive/HiveServer2+Clients#HiveServer2Clients-Beeline–CommandLineShell)
- [Elementary Data Documentation](https://docs.elementary-data.com/)
- [dbt Python Models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models/python-models)

---

**Thank you for setting up your dbt Spark project! If you have any questions or need further assistance, feel free to reach out.**