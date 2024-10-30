def model(dbt, spark):
    dbt.config(materialized='table')

    data = [("Alice", 1), ("Bob", 2), ("Charlie", 3)]
    columns = ["name", "id"]
    df = spark.createDataFrame(data, columns)

    return df
