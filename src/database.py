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

# Insert a transaction into the database.
def insert_transaction(transaction, source_file=None):
    """
    Insert a transaction into MySQL.

    source_file stores the CSV filename that the transaction
    came from.
    """

    # Open a database connection.
    connection = get_connection()

    # Create a cursor.
    cursor = connection.cursor()

    # Define the 28 PCA feature names.
    feature_columns = [
        "V1", "V2", "V3", "V4", "V5", "V6", "V7",
        "V8", "V9", "V10", "V11", "V12", "V13", "V14",
        "V15", "V16", "V17", "V18", "V19", "V20", "V21",
        "V22", "V23", "V24", "V25", "V26", "V27", "V28"
    ]

    # Build the column names.
    columns = [
        "transaction_time",
        "amount"
    ]

    columns.extend(
        column.lower()
        for column in feature_columns
    )

    columns.append("source_file")

    # Build the values in exactly the same order as the columns.
    values = [
        transaction["Time"],
        transaction["Amount"]
    ]

    values.extend(
        transaction[column]
        for column in feature_columns
    )

    values.append(source_file)

    # Create exactly one placeholder for every value.
    placeholders = ", ".join(
        ["%s"] * len(values)
    )

    # Create the INSERT query.
    query = f"""
        INSERT INTO transactions (
            {", ".join(columns)}
        )
        VALUES (
            {placeholders}
        )
    """

    # Execute the INSERT query.
    cursor.execute(
        query,
        tuple(values)
    )

    # Save the transaction.
    connection.commit()

    # Get the generated transaction ID.
    transaction_id = cursor.lastrowid

    # Close database resources.
    cursor.close()
    connection.close()

    # Return the generated ID.
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

def insert_investigation(
    transaction_id,
    status,
    analyst_decision=None,
    analyst_notes=None
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO investigations (
        transaction_id,
        status,
        analyst_decision,
        analyst_notes
    )
    VALUES (%s, %s, %s, %s)
    """

    values = (
        transaction_id,
        status,
        analyst_decision,
        analyst_notes
    )

    cursor.execute(query, values)
    connection.commit()

    investigation_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return investigation_id

def insert_audit_log(
    transaction_id,
    action,
    details=None
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO audit_logs (
        transaction_id,
        action,
        details
    )
    VALUES (%s, %s, %s)
    """

    values = (
        transaction_id,
        action,
        details
    )

    cursor.execute(query, values)
    connection.commit()

    log_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return log_id

# Update an investigation with the analyst's final decision and optional notes.
def update_investigation_decision(
    investigation_id,
    analyst_decision,
    analyst_notes=None
):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
    UPDATE investigations
    SET
        status = %s,
        analyst_decision = %s,
        analyst_notes = %s
    WHERE investigation_id = %s
    """

    values = (
        "CLOSED",
        analyst_decision,
        analyst_notes,
        investigation_id
    )

    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()

    return cursor.rowcount

# Check whether a transaction exists in the database.
def transaction_exists(transaction_id):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    SELECT transaction_id
    FROM transactions
    WHERE transaction_id = %s
    """

    # Execute the query with the provided transaction_id.
    cursor.execute(query, (transaction_id,))
    # Get the first matching row, if one exists.
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    # Return True if the transaction was found.
    return result is not None

# Find the transaction associated with an investigation.
def get_transaction_id_for_investigation(investigation_id):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    SELECT transaction_id
    FROM investigations
    WHERE investigation_id = %s
    """

    cursor.execute(query, (investigation_id,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    # Return the transaction ID, or None if not found.
    if result is None: return None

    return result[0]

# Retrieve all transactions from the database.
def get_transactions():

    connection = get_connection()
    # Use a dictionary cursor so the result has column names.
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT *
    FROM transactions
    ORDER BY transaction_id DESC
    """

    cursor.execute(query)

    # Fetch all matching transactions.
    transactions = cursor.fetchall()

    cursor.close()
    connection.close()

    return transactions

# Retrieve a single transaction by its ID.
def get_transaction(transaction_id):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT *
    FROM transactions
    WHERE transaction_id = %s
    """

    cursor.execute(query, (transaction_id,))
    transaction = cursor.fetchone()

    cursor.close()
    connection.close()

    return transaction

# Retrieve all transactions and their predictions for a given source file.
def get_batch_results_by_source_file(source_file):
    """
    Retrieve all transactions and their predictions
    belonging to a previously uploaded CSV file.

    This function only reads from MySQL.
    It does NOT insert or modify anything.
    """

    # Open a database connection.
    connection = get_connection()

    # Use a dictionary cursor so column names are available.
    cursor = connection.cursor(dictionary=True)

    # Get the latest prediction and investigation for each transaction.
    cursor.execute(
        """
        SELECT
            t.transaction_id,
            p.prediction_id,
            p.fraud_probability,
            p.risk_level,
            i.investigation_id

        FROM transactions t

        LEFT JOIN predictions p
            ON p.prediction_id = (
                SELECT MAX(p2.prediction_id)
                FROM predictions p2
                WHERE p2.transaction_id = t.transaction_id
            )

        LEFT JOIN investigations i
            ON i.investigation_id = (
                SELECT MAX(i2.investigation_id)
                FROM investigations i2
                WHERE i2.transaction_id = t.transaction_id
            )

        WHERE t.source_file = %s

        ORDER BY t.transaction_id
        """,
        (source_file,)
    )

    # Get all matching transactions.
    rows = cursor.fetchall()

    # Close database resources.
    cursor.close()
    connection.close()

    # Count HIGH-risk transactions.
    high_risk_count = sum(
        1
        for row in rows
        if row["risk_level"] == "HIGH"
    )

    # Count LOW-risk transactions.
    low_risk_count = sum(
        1
        for row in rows
        if row["risk_level"] == "LOW"
    )

    # Keep only HIGH-risk transactions for investigation.
    flagged_transactions = []

    for index, row in enumerate(rows):

        if row["risk_level"] == "HIGH":

            flagged_transactions.append({
                "index": index,
                "transaction_id": row["transaction_id"],
                "prediction_id": row["prediction_id"],
                "investigation_id": row["investigation_id"],
                "fraud_probability": float(
                    row["fraud_probability"]
                ),
                "risk_level": row["risk_level"]
            })

    # Return the same basic structure used by
    # the batch prediction endpoint.
    return {
        "source_file": source_file,
        "total_transactions": len(rows),
        "high_risk_transactions": high_risk_count,
        "low_risk_transactions": low_risk_count,
        "flagged_transactions": flagged_transactions
    }

# Retrieve the prediction associated with a transaction.
def get_prediction(transaction_id):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM predictions
        WHERE transaction_id = %s
        ORDER BY prediction_id DESC
        LIMIT 1
        """,
        (transaction_id,)
    )

    # Get the prediction, or None if it does not exist.
    prediction = cursor.fetchone()

    cursor.close()
    connection.close()

    return prediction

# Retrieve the latest investigation associated with a transaction.
def get_investigation(transaction_id):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM investigations
        WHERE transaction_id = %s
        ORDER BY investigation_id DESC
        LIMIT 1
        """,
        (transaction_id,)
    )

    investigation = cursor.fetchone()

    cursor.close()
    connection.close()

    return investigation

# etrieve audit log entries from the database
def get_audit_logs():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM audit_logs
        ORDER BY timestamp DESC
    """)

    logs = cursor.fetchall()

    cursor.close()
    connection.close()

    return logs