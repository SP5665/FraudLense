import os
import mysql.connector
from dotenv import load_dotenv

# Load database configuration from the .env file.
load_dotenv()

# ---------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------

# Get a connection to the MySQL database.
def get_connection():

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

# ---------------------------------------------------------
# INSERT TRANSACTION
# ---------------------------------------------------------

# Insert a transaction into the transactions table.
def insert_transaction(
    transaction,
    source_file=None
):

    # Open a database connection.
    connection = get_connection()

    # Create a cursor for executing SQL statements.
    cursor = connection.cursor()

    # Define the 28 PCA feature names.
    feature_columns = [
        "V1", "V2", "V3", "V4", "V5", "V6", "V7",
        "V8", "V9", "V10", "V11", "V12", "V13", "V14",
        "V15", "V16", "V17", "V18", "V19", "V20", "V21",
        "V22", "V23", "V24", "V25", "V26", "V27", "V28"
    ]

    # Build the database column names.
    columns = [
        "transaction_time",
        "amount"
    ]

    # Convert V1...V28 into the lowercase database column names.
    columns.extend(
        column.lower()
        for column in feature_columns
    )

    # Add the source CSV filename.
    columns.append(
        "source_file"
    )

    # Build the values in exactly the same order as the columns.
    values = [
        transaction["Time"],
        transaction["Amount"]
    ]

    values.extend(
        transaction[column]
        for column in feature_columns
    )

    # Add the source CSV filename.
    values.append(
        source_file
    )

    # Create one SQL placeholder for every value.
    placeholders = ", ".join(
        ["%s"] * len(values)
    )

    # Build the INSERT query.
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

    # Get the automatically generated transaction ID.
    transaction_id = cursor.lastrowid

    # Close database resources.
    cursor.close()
    connection.close()

    # Return the generated transaction ID.
    return transaction_id

# ---------------------------------------------------------
# INSERT PREDICTION
# ---------------------------------------------------------

# Store a model prediction in the predictions table.
def insert_prediction(
    transaction_id,
    fraud_probability,
    risk_level,
    model_version
):

    # Open a database connection.
    connection = get_connection()

    # Create a cursor.
    cursor = connection.cursor()

    # Define the INSERT query.
    query = """
        INSERT INTO predictions (
            transaction_id,
            fraud_probability,
            risk_level,
            model_version
        )
        VALUES (%s, %s, %s, %s)
    """

    # Values to insert.
    values = (
        transaction_id,
        fraud_probability,
        risk_level,
        model_version
    )

    # Execute the query.
    cursor.execute(
        query,
        values
    )

    # Save the prediction.
    connection.commit()

    # Get the generated prediction ID.
    prediction_id = cursor.lastrowid

    # Close database resources.
    cursor.close()
    connection.close()

    # Return the generated prediction ID.
    return prediction_id

# ---------------------------------------------------------
# INSERT INVESTIGATION
# ---------------------------------------------------------

# Create an investigation for a transaction.
def insert_investigation(
    transaction_id,
    status,
    analyst_decision=None,
    analyst_notes=None
):

    # Open a database connection.
    connection = get_connection()

    # Create a cursor.
    cursor = connection.cursor()

    # Define the INSERT query.
    query = """
        INSERT INTO investigations (
            transaction_id,
            status,
            analyst_decision,
            analyst_notes
        )
        VALUES (%s, %s, %s, %s)
    """

    # Values to insert.
    values = (
        transaction_id,
        status,
        analyst_decision,
        analyst_notes
    )

    # Execute the query.
    cursor.execute(
        query,
        values
    )

    # Save the investigation.
    connection.commit()

    # Get the generated investigation ID.
    investigation_id = cursor.lastrowid

    # Close database resources.
    cursor.close()
    connection.close()

    # Return the generated investigation ID.
    return investigation_id

# ---------------------------------------------------------
# INSERT AUDIT LOG
# ---------------------------------------------------------

# Store an action in the audit log.
def insert_audit_log(
    transaction_id,
    action,
    details=None
):

    # Open a database connection.
    connection = get_connection()

    # Create a cursor.
    cursor = connection.cursor()

    # Define the INSERT query.
    query = """
        INSERT INTO audit_logs (
            transaction_id,
            action,
            details
        )
        VALUES (%s, %s, %s)
    """

    # Values to insert.
    values = (
        transaction_id,
        action,
        details
    )

    # Execute the query.
    cursor.execute(
        query,
        values
    )

    # Save the audit log entry.
    connection.commit()

    # Get the generated log ID.
    log_id = cursor.lastrowid

    # Close database resources.
    cursor.close()
    connection.close()

    # Return the generated log ID.
    return log_id

# ---------------------------------------------------------
# UPDATE INVESTIGATION DECISION
# ---------------------------------------------------------

# Update an investigation with the analyst's final decision and notes.
def update_investigation_decision(
    investigation_id,
    analyst_decision,
    analyst_notes=None
):

    # Open a database connection.
    connection = get_connection()

    # Create a cursor.
    cursor = connection.cursor()

    # Define the UPDATE query.
    query = """
        UPDATE investigations
        SET
            status = %s,
            analyst_decision = %s,
            analyst_notes = %s
        WHERE investigation_id = %s
    """

    # Values for the UPDATE query.
    values = (
        "CLOSED",
        analyst_decision,
        analyst_notes,
        investigation_id
    )

    # Execute the UPDATE query.
    cursor.execute(
        query,
        values
    )

    # Save the changes.
    connection.commit()

    # Store the number of rows affected.
    affected_rows = cursor.rowcount

    # Close database resources.
    cursor.close()
    connection.close()

    # Return the number of affected rows.
    return affected_rows

# ---------------------------------------------------------
# CHECK TRANSACTION EXISTS
# ---------------------------------------------------------

# Check whether a transaction exists in the database.
def transaction_exists(
    transaction_id
):

    # Open a database connection.
    connection = get_connection()

    # Create a cursor.
    cursor = connection.cursor()

    # Define the SELECT query.
    query = """
        SELECT transaction_id
        FROM transactions
        WHERE transaction_id = %s
    """

    # Execute the query.
    cursor.execute(
        query,
        (transaction_id,)
    )

    # Get the first matching row.
    result = cursor.fetchone()

    # Close database resources.
    cursor.close()
    connection.close()

    # Return True if the transaction was found.
    return result is not None

# ---------------------------------------------------------
# GET TRANSACTION ID FOR INVESTIGATION
# ---------------------------------------------------------

# Find the transaction associated with an investigation.
def get_transaction_id_for_investigation(
    investigation_id
):

    # Open a database connection.
    connection = get_connection()

    # Create a cursor.
    cursor = connection.cursor()

    # Define the SELECT query.
    query = """
        SELECT transaction_id
        FROM investigations
        WHERE investigation_id = %s
    """

    # Execute the query.
    cursor.execute(
        query,
        (investigation_id,)
    )

    # Get the matching row.
    result = cursor.fetchone()

    # Close database resources.
    cursor.close()
    connection.close()

    # Return None if the investigation was not found.
    if result is None:
        return None

    # Return the associated transaction ID.
    return result[0]

# ---------------------------------------------------------
# GET ALL TRANSACTIONS
# ---------------------------------------------------------

# Retrieve all transactions from the database.
def get_transactions():

    # Open a database connection.
    connection = get_connection()

    # Use a dictionary cursor so column names are included.
    cursor = connection.cursor(
        dictionary=True
    )

    # Retrieve transactions from newest to oldest.
    query = """
        SELECT *
        FROM transactions
        ORDER BY transaction_id DESC
    """

    # Execute the query.
    cursor.execute(
        query
    )

    # Fetch all matching transactions.
    transactions = cursor.fetchall()

    # Close database resources.
    cursor.close()
    connection.close()

    # Return the transactions.
    return transactions

# ---------------------------------------------------------
# GET SINGLE TRANSACTION
# ---------------------------------------------------------

# Retrieve a single transaction by its ID.
def get_transaction(
    transaction_id
):

    # Open a database connection.
    connection = get_connection()

    # Use a dictionary cursor for named columns.
    cursor = connection.cursor(
        dictionary=True
    )

    # Define the SELECT query.
    query = """
        SELECT *
        FROM transactions
        WHERE transaction_id = %s
    """

    # Execute the query.
    cursor.execute(
        query,
        (transaction_id,)
    )

    # Get the transaction, or None if it does not exist.
    transaction = cursor.fetchone()

    # Close database resources.
    cursor.close()
    connection.close()

    # Return the transaction.
    return transaction

# ---------------------------------------------------------
# GET BATCH RESULTS BY SOURCE FILE
# ---------------------------------------------------------

# Retrieve transactions and their latest predictions belonging to a previously uploaded CSV file.
def get_batch_results_by_source_file(
    source_file
):

    # Open a database connection.
    connection = get_connection()

    # Use a dictionary cursor so column names are available.
    cursor = connection.cursor(
        dictionary=True
    )

    # Retrieve the latest prediction and investigation
    # for every transaction belonging to this CSV file.
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

    # Fetch all matching rows.
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

        # Add HIGH-risk transactions to the flagged list.
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

    # Return the screening summary.
    return {
        "source_file": source_file,
        "total_transactions": len(rows),
        "high_risk_transactions": high_risk_count,
        "low_risk_transactions": low_risk_count,
        "flagged_transactions": flagged_transactions
    }

# ---------------------------------------------------------
# GET PREDICTION
# ---------------------------------------------------------

# Retrieve the latest prediction for a transaction.
def get_prediction(
    transaction_id
):

    # Open a database connection.
    connection = get_connection()

    # Use a dictionary cursor for named columns.
    cursor = connection.cursor(
        dictionary=True
    )

    # Retrieve the newest prediction for the transaction.
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

    # Close database resources.
    cursor.close()
    connection.close()

    # Return the prediction.
    return prediction

# ---------------------------------------------------------
# GET INVESTIGATION
# ---------------------------------------------------------

# Retrieve the latest investigation for a transaction.
def get_investigation(
    transaction_id
):

    # Open a database connection.
    connection = get_connection()

    # Use a dictionary cursor for named columns.
    cursor = connection.cursor(
        dictionary=True
    )

    # Retrieve the newest investigation.
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

    # Get the investigation, or None if it does not exist.
    investigation = cursor.fetchone()

    # Close database resources.
    cursor.close()
    connection.close()

    # Return the investigation.
    return investigation

# ---------------------------------------------------------
# GET AUDIT LOGS
# ---------------------------------------------------------

# Retrieve audit log entries from the database.
def get_audit_logs():

    # Open a database connection.
    connection = get_connection()

    # Use a dictionary cursor for named columns.
    cursor = connection.cursor(
        dictionary=True
    )

    # Retrieve newest audit entries first.
    cursor.execute(
        """
        SELECT *
        FROM audit_logs
        ORDER BY timestamp DESC
        """
    )

    # Fetch all audit logs.
    logs = cursor.fetchall()

    # Close database resources.
    cursor.close()
    connection.close()

    # Return the audit logs.
    return logs

# ---------------------------------------------------------
# GET ALL TRANSACTIONS, PREDICTIONS, INVESTIGATIONS, AUDIT LOG
# ---------------------------------------------------------

# Retrieve all records from the transactions table.
def get_all_transactions():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM transactions
        ORDER BY transaction_id DESC
    """)

    transactions = cursor.fetchall()

    cursor.close()
    connection.close()

    return transactions

# Retrieve all records from the predictions table.
def get_all_predictions():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM predictions
        ORDER BY prediction_id DESC
    """)

    predictions = cursor.fetchall()

    cursor.close()
    connection.close()

    return predictions

# Retrieve all records from the investigations table.
def get_all_investigations():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM investigations
        ORDER BY investigation_id DESC
    """)

    investigations = cursor.fetchall()

    cursor.close()
    connection.close()

    return investigations

# retrieve all records from the audit_logs table.
def get_all_audit_logs():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM audit_logs
        ORDER BY log_id DESC
    """)

    logs = cursor.fetchall()

    cursor.close()
    connection.close()

    return logs