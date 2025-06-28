import os
import oracledb
import pandas as pd

# Oracle Connection Details - Should be consistent with SQLGenerationAgent
# Load from .env or a config file in a real application
ORACLE_USER = os.getenv("ORACLE_USER", "your_oracle_user")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "your_oracle_password")
ORACLE_DSN = os.getenv("ORACLE_DSN", "your_oracle_host:your_oracle_port/your_oracle_service_name") # e.g., localhost:1521/XEPDB1

class DatabaseInteractionAgent:
    def __init__(self):
        """
        Initializes the DatabaseInteractionAgent.
        """
        print("Initializing DatabaseInteractionAgent...")
        self.connection = None
        self.is_connected = False
        self._connect()

    def _connect(self):
        """
        Establishes a connection to the Oracle database.
        """
        if ORACLE_USER == "your_oracle_user" or ORACLE_PASSWORD == "your_oracle_password" or ORACLE_DSN == "your_oracle_host:your_oracle_port/your_oracle_service_name":
            print("WARNING: Oracle credentials are set to default placeholders in DatabaseInteractionAgent.")
            print("Please set ORACLE_USER, ORACLE_PASSWORD, and ORACLE_DSN environment variables.")
            self.is_connected = False
            return

        try:
            print(f"Attempting to connect to Oracle database: {ORACLE_DSN} as user {ORACLE_USER}")
            # For thick mode, you might need to initialize the client:
            # oracledb.init_oracle_client(lib_dir="/path/to/your/instantclient_XX_Y")

            self.connection = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
            self.is_connected = True
            print("Successfully connected to Oracle database.")
        except oracledb.DatabaseError as e:
            error_obj, = e.args
            print(f"Oracle Database Error connecting: {error_obj.message} (Code: {error_obj.code})")
            print("Ensure Oracle client libraries are installed and accessible (e.g., instant client in PATH or LD_LIBRARY_PATH).")
            print("Verify DSN format, username, and password.")
            self.is_connected = False
            self.connection = None
        except Exception as e:
            print(f"An unexpected error occurred during Oracle connection: {e}")
            self.is_connected = False
            self.connection = None

    def execute_query(self, sql_query: str, params: dict = None) -> pd.DataFrame | None:
        """
        Executes a given SQL query (SELECT statements only) and returns the results as a Pandas DataFrame.
        Args:
            sql_query (str): The SQL query to execute.
            params (dict, optional): Parameters for the SQL query (for bind variables).
        Returns:
            pd.DataFrame: A DataFrame containing the query results, or None if an error occurs or no data.
        """
        if not self.is_connected:
            print("Cannot execute query: Not connected to the database.")
            return None

        if not sql_query.strip().upper().startswith("SELECT"):
            print("Error: Only SELECT queries are allowed for execution by this agent.")
            # This is a safety measure as per the problem description (all select statements)
            return None

        print(f"Executing SQL query: {sql_query[:200]}...") # Log snippet of query
        if params:
            print(f"With parameters: {params}")

        cursor = None
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(sql_query, params)
            else:
                cursor.execute(sql_query)

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            df = pd.DataFrame(rows, columns=columns)
            print(f"Query executed successfully. Retrieved {len(df)} rows.")
            return df
        except oracledb.DatabaseError as e:
            error_obj, = e.args
            print(f"Oracle Database Error executing query: {error_obj.message} (Code: {error_obj.code})")
            # You might want to log the full query and params here for debugging
            return None
        except Exception as e:
            print(f"An unexpected error occurred during query execution: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def close_connection(self):
        """
        Closes the database connection.
        """
        if self.connection:
            print("Closing Oracle database connection.")
            self.connection.close()
            self.is_connected = False
            self.connection = None

    def __del__(self):
        """
        Ensures the connection is closed when the object is garbage collected.
        """
        self.close_connection()

# Example Usage (Illustrative - requires Oracle DB and credentials)
if __name__ == '__main__':
    print("Starting DatabaseInteractionAgent example...")
    print("IMPORTANT: Set ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN environment variables for Oracle connection.")

    db_agent = DatabaseInteractionAgent()

    if db_agent.is_connected:
        print("\n--- Example Query 1: Simple SELECT (replace with a valid table in your schema) ---")
        # Replace 'dual' with a table name that exists in your schema, e.g., 'YOUR_TABLE_NAME'
        # list all tables: SELECT table_name FROM all_tables WHERE owner = SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA')
        # For this example, we'll try a universally available table if possible, or a common system table.
        # If you have a DISTRICT_MASTER table, you could use:
        # query1 = "SELECT district_id, district_name FROM DISTRICT_MASTER WHERE ROWNUM <= 5"
        query1 = "SELECT SYSDATE FROM DUAL" # DUAL is a special one-row, one-column table in Oracle

        results_df1 = db_agent.execute_query(query1)
        if results_df1 is not None:
            if not results_df1.empty:
                print("Query 1 Results:")
                print(results_df1.to_string())
            else:
                print("Query 1 executed but returned no data.")
        else:
            print("Query 1 failed.")

        print("\n--- Example Query 2: SELECT with a non-existent table (to show error handling) ---")
        query2 = "SELECT * FROM NON_EXISTENT_TABLE_XYZ"
        results_df2 = db_agent.execute_query(query2)
        if results_df2 is None:
            print("Query 2 failed as expected (table likely does not exist).")

        print("\n--- Example Query 3: Non-SELECT statement (to show safety check) ---")
        query3 = "DROP TABLE DUAL" # Malicious attempt
        results_df3 = db_agent.execute_query(query3)
        if results_df3 is None:
            print("Query 3 was blocked by the agent as it's not a SELECT statement.")

        db_agent.close_connection()
    else:
        print("Could not connect to the database. Please check your credentials and Oracle client setup.")

    print("\nDatabaseInteractionAgent example finished.")
