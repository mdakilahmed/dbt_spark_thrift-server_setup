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
