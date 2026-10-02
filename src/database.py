import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# Database connection and insertion functions
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

# Insert a transaction into the transactions table
def insert_transaction(transaction):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO transactions (
        transaction_time,
        amount,
        v1, v2, v3, v4, v5, v6, v7,
        v8, v9, v10, v11, v12, v13, v14,
        v15, v16, v17, v18, v19, v20, v21,
        v22, v23, v24, v25, v26, v27, v28
    )
    VALUES (
        %s, %s,
        %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s
    )
    """

    values = (
        transaction["Time"],
        transaction["Amount"],
        transaction["V1"],
        transaction["V2"],
        transaction["V3"],
        transaction["V4"],
        transaction["V5"],
        transaction["V6"],
        transaction["V7"],
        transaction["V8"],
        transaction["V9"],
        transaction["V10"],
        transaction["V11"],
        transaction["V12"],
        transaction["V13"],
        transaction["V14"],
        transaction["V15"],
        transaction["V16"],
        transaction["V17"],
        transaction["V18"],
        transaction["V19"],
        transaction["V20"],
        transaction["V21"],
        transaction["V22"],
        transaction["V23"],
        transaction["V24"],
        transaction["V25"],
        transaction["V26"],
        transaction["V27"],
        transaction["V28"]
    )

    cursor.execute(query, values)
    connection.commit()
    transaction_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return transaction_id

# Insert a prediction into the predictions table
def insert_prediction(
    transaction_id,
    fraud_probability,
    risk_level,
    model_version
):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO predictions (
        transaction_id,
        fraud_probability,
        risk_level,
        model_version
    )
    VALUES (%s, %s, %s, %s)
    """

    values = (
        transaction_id,
        fraud_probability,
        risk_level,
        model_version
    )

    cursor.execute(query, values)

    connection.commit()

    prediction_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return prediction_id