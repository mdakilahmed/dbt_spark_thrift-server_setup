from pyspark.sql import SparkSession
from pyspark.sql.types import *
import shutil
import os

def load_csv_to_table(csv_path, table_name, schema):
    # Drop the table if it exists
    spark.sql(f"DROP TABLE IF EXISTS {table_name}")

    # Remove the existing directory if it exists
    # Split the table name into database and table components
    if '.' in table_name:
        database_name, table_name_only = table_name.split('.', 1)
    else:
        database_name = 'default'
        table_name_only = table_name

    # Construct the correct path to the table directory
    table_path = f"/opt/sparkwarehouse/{database_name}.db/{table_name_only}"

    # Remove the directory if it exists
    if os.path.exists(table_path):
        shutil.rmtree(table_path)

    # Read the CSV file into a DataFrame
    df = spark.read.csv(
        csv_path,
        header=True,
        schema=schema,
        inferSchema=False,
        sep=','
    )

    # Write the DataFrame to a managed table
    df.write.mode('overwrite').saveAsTable(f"{database_name}.{table_name_only}")

# Initialize Spark session with Hive support and configurations
spark = SparkSession.builder \
    .appName("Load CSV Data") \
    .enableHiveSupport() \
    .config("spark.sql.warehouse.dir", "/opt/sparkwarehouse") \
    .config("javax.jdo.option.ConnectionURL", "jdbc:derby:;databaseName=/opt/hivemetastore/metastore_db;create=true") \
    .getOrCreate()

# Create the raw_data database
spark.sql("CREATE DATABASE IF NOT EXISTS raw_data")

# Define schemas for each CSV file

# Applicant Schema
applicant_schema = StructType([
    StructField('applicant_id', IntegerType(), True),
    StructField('first_name', StringType(), True),
    StructField('last_name', StringType(), True),
    StructField('date_of_birth', DateType(), True),
    StructField('gender', StringType(), True),
    StructField('marital_status', StringType(), True),
    StructField('number_of_dependents', IntegerType(), True)
])

# Contact Information Schema
contact_schema = StructType([
    StructField('contact_id', IntegerType(), True),
    StructField('applicant_id', IntegerType(), True),
    StructField('home_address', StringType(), True),
    StructField('city', StringType(), True),
    StructField('state_province', StringType(), True),
    StructField('postal_code', StringType(), True),
    StructField('country', StringType(), True),
    StructField('primary_phone_number', StringType(), True),
    StructField('email_address', StringType(), True),
    StructField('move_in_date', DateType(), True)
])

# Credit Information Schema
credit_schema = StructType([
    StructField('credit_id', IntegerType(), True),
    StructField('applicant_id', IntegerType(), True),
    StructField('credit_score', IntegerType(), True),
    StructField('credit_history_length', IntegerType(), True),
    StructField('number_of_late_payments', IntegerType(), True),
    StructField('bankruptcies_filed', IntegerType(), True),
    StructField('foreclosures', IntegerType(), True),
    StructField('credit_card_debt', FloatType(), True),
    StructField('total_credit_limit', FloatType(), True),
    StructField('number_of_hard_inquiries', IntegerType(), True)
])

# Employment Information Schema
employment_schema = StructType([
    StructField('employment_id', IntegerType(), True),
    StructField('applicant_id', IntegerType(), True),
    StructField('employment_status', StringType(), True),
    StructField('employer_name', StringType(), True),
    StructField('job_title', StringType(), True),
    StructField('employment_start_date', DateType(), True),
    StructField('years_in_current_job', IntegerType(), True)
])

# Financial Information Schema
financial_schema = StructType([
    StructField('applicant_id', IntegerType(), True),
    StructField('post_tax_annual_income', FloatType(), True),
    StructField('total_monthly_expenses', FloatType(), True),
    StructField('monthly_emi_amount', FloatType(), True),
    StructField('other_debts', FloatType(), True)
])

# Loan Application Schema
loan_schema = StructType([
    StructField('loan_application_id', IntegerType(), True),
    StructField('applicant_id', IntegerType(), True),
    StructField('application_date', DateType(), True),
    StructField('loan_amount_requested', FloatType(), True),
    StructField('loan_purpose', StringType(), True),
    StructField('loan_type', StringType(), True),
    StructField('loan_term', IntegerType(), True),
    StructField('interest_rate_type', StringType(), True)
])

# Load data into Spark tables

# Load applicant_raw.csv
load_csv_to_table(
    csv_path='/opt/data/applicant_raw.csv',
    table_name='raw_data.applicant_raw',
    schema=applicant_schema
)

# Load contact_information_raw.csv
load_csv_to_table(
    csv_path='/opt/data/contact_information_raw.csv',
    table_name='raw_data.contact_information_raw',
    schema=contact_schema
)

# Load credit_information_raw.csv
load_csv_to_table(
    csv_path='/opt/data/credit_information_raw.csv',
    table_name='raw_data.credit_information_raw',
    schema=credit_schema
)

# Load employment_information_raw.csv
load_csv_to_table(
    csv_path='/opt/data/employment_information_raw.csv',
    table_name='raw_data.employment_information_raw',
    schema=employment_schema
)

# Load financial_information_raw.csv
load_csv_to_table(
    csv_path='/opt/data/financial_information_raw.csv',
    table_name='raw_data.financial_information_raw',
    schema=financial_schema
)

# Load loan_application_raw.csv
load_csv_to_table(
    csv_path='/opt/data/loan_application_raw.csv',
    table_name='raw_data.loan_application_raw',
    schema=loan_schema
)

# Stop the Spark session
spark.stop()
