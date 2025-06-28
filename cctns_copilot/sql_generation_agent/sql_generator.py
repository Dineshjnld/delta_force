import os
import vanna
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDBVectorStore

# Configuration (Ideally, load from .env or a config file)
# Ensure Ollama is running and the model is pulled (e.g., `ollama pull mistral`)
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "mistral") # Replace with your preferred Ollama model
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db_cctns") # Path to persist ChromaDB

# Oracle Connection Details - TO BE PROVIDED BY USER
# These should be securely managed, e.g., via environment variables
ORACLE_USER = os.getenv("ORACLE_USER", "your_oracle_user")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "your_oracle_password")
ORACLE_DSN = os.getenv("ORACLE_DSN", "your_oracle_host:your_oracle_port/your_oracle_service_name") # e.g., localhost:1521/XEPDB1

class SQLGenerationAgent:
    def __init__(self, model_name=OLLAMA_MODEL_NAME, collection_name="cctns_copilot_vanna"):
        """
        Initializes the SQLGenerationAgent with Vanna AI.
        Args:
            model_name (str): The name of the Ollama model to use.
            collection_name (str): Name of the collection in ChromaDB for this agent.
        """
        print(f"Initializing SQLGenerationAgent with Ollama model: {model_name} and Chroma collection: {collection_name}")

        self.ollama_llm = Ollama(config={'model': model_name})
        self.chroma_vector_store = ChromaDBVectorStore(path=CHROMA_DB_PATH, collection_name=collection_name)

        self.vn = vanna.Vanna(
            llm=self.ollama_llm,
            vectorstore=self.chroma_vector_store
        )

        self.oracle_connected = False
        self._connect_oracle()

        if not self.vn.get_training_data().empty:
            print("Existing training data found in vector store.")
        else:
            print("No existing training data found. Agent will need training.")

    def _connect_oracle(self):
        """
        Connects Vanna to the Oracle database.
        """
        if ORACLE_USER == "your_oracle_user" or ORACLE_PASSWORD == "your_oracle_password" or ORACLE_DSN == "your_oracle_host:your_oracle_port/your_oracle_service_name":
            print("WARNING: Oracle credentials are set to default placeholders.")
            print("Please set ORACLE_USER, ORACLE_PASSWORD, and ORACLE_DSN environment variables or update the script.")
            print("Oracle connection will not be established for training from DB.")
            self.oracle_connected = False
            return

        try:
            # Vanna uses a DSN format for Oracle like: oracle_user/oracle_password@oracle_dsn
            # However, the vanna.connect_to_oracle method expects individual parameters.
            self.vn.connect_to_oracle(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
            print(f"Successfully connected to Oracle database: {ORACLE_DSN}")
            self.oracle_connected = True
        except Exception as e:
            print(f"Failed to connect to Oracle: {e}")
            print("Please ensure Oracle client libraries are installed and configured correctly, and credentials are valid.")
            self.oracle_connected = False

    def train_from_ddl_string(self, ddl_string: str):
        """
        Trains Vanna using DDL statements provided as a string.
        Args:
            ddl_string (str): A string containing DDL statements (CREATE TABLE, etc.).
        """
        if not ddl_string.strip():
            print("DDL string is empty. Nothing to train.")
            return
        print("Training Vanna from DDL string...")
        try:
            self.vn.train(ddl=ddl_string)
            print("Training from DDL string completed.")
        except Exception as e:
            print(f"Error during training from DDL string: {e}")

    def train_from_ddl_file(self, file_path: str):
        """
        Trains Vanna using DDL statements from a file.
        Args:
            file_path (str): Path to the .sql file containing DDL statements.
        """
        print(f"Training Vanna from DDL file: {file_path}...")
        try:
            with open(file_path, 'r') as f:
                ddl_content = f.read()
            self.vn.train(ddl=ddl_content)
            print(f"Training from DDL file {file_path} completed.")
        except FileNotFoundError:
            print(f"Error: DDL file not found at {file_path}")
        except Exception as e:
            print(f"Error during training from DDL file: {e}")

    def train_from_sql_queries(self, queries_data: list[dict]):
        """
        Trains Vanna with sample SQL queries and their corresponding questions.
        Args:
            queries_data (list[dict]): A list of dictionaries, where each dict has
                                       'question' (natural language) and 'sql' (SQL query).
                                       Optionally, 'documentation' can be added.
        """
        if not queries_data:
            print("No queries data provided. Nothing to train.")
            return
        print(f"Training Vanna with {len(queries_data)} sample SQL queries...")
        for item in queries_data:
            try:
                question = item.get('question')
                sql = item.get('sql')
                documentation = item.get('documentation') # Optional
                if question and sql:
                    self.vn.train(question=question, sql=sql, ddl=item.get('ddl'), documentation=documentation)
                    print(f"Trained with: Q: {question} -> SQL: {sql[:100]}...")
                else:
                    print(f"Skipping invalid training item: {item}")
            except Exception as e:
                print(f"Error training with item {item}: {e}")
        print("Training with sample SQL queries completed.")

    def train_from_documentation(self, documentation_text: str, data_type: str = "documentation"):
        """
        Trains Vanna with general documentation or text snippets.
        Args:
            documentation_text (str): Text content for training.
            data_type (str): The type of data being trained (e.g., "documentation", "glossary").
        """
        if not documentation_text.strip():
            print(f"No {data_type} text provided. Nothing to train.")
            return
        print(f"Training Vanna from {data_type}...")
        try:
            self.vn.train(documentation=documentation_text) # Vanna's train method handles 'documentation' type
            print(f"Training from {data_type} completed.")
        except Exception as e:
            print(f"Error during training from {data_type}: {e}")

    def train_from_information_schema(self):
        """
        Trains Vanna using the information schema from the connected database.
        This is a powerful way to get table names, column names, types, and relationships.
        """
        if not self.oracle_connected:
            print("Cannot train from information schema: Oracle database not connected.")
            return False

        print("Training Vanna from Oracle information schema...")
        try:
            # This will extract DDL-like information (table names, columns, types)
            # The exact information extracted depends on Vanna's Oracle connector implementation
            df_information_schema = self.vn.run_sql("SELECT table_name, column_name, data_type FROM all_tab_columns WHERE owner = SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA')") # Example query, adjust for Oracle

            if df_information_schema is None or df_information_schema.empty:
                print("Could not retrieve information schema, or it was empty.")
                # Fallback or alternative: Try to get DDL for tables if possible
                # For Oracle, getting DDL programmatically can be complex.
                # vn.train(ddl=vn.get_table_info(table_name="YOUR_TABLE")) might be an option if Vanna supports it well for Oracle.
                # For now, we rely on what vn.train() with DDLs does or manual DDL provision.
                # A more direct approach if Vanna supports it for Oracle:
                # self.vn.train(information_schema=True) # Check Vanna documentation for Oracle specific support
                print("Attempting to train with DDLs from all tables in the schema (if supported by Vanna for Oracle)...")
                # This part is speculative based on typical Vanna behavior, may need adjustment for Oracle
                # It's often better to provide DDLs explicitly for Oracle.
                # tables = self.vn.run_sql("SELECT table_name FROM all_tables WHERE owner = SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA')")
                # if tables is not None and not tables.empty:
                #     for table_name in tables['table_name']:
                #         try:
                #             # This is a generic Vanna function, its Oracle effectiveness can vary
                #             ddl = self.vn.get_ddl(table_name)
                #             if ddl:
                #                self.vn.train(ddl=ddl)
                #                print(f"Trained with DDL for table: {table_name}")
                #         except Exception as e_table:
                #             print(f"Could not get/train DDL for table {table_name}: {e_table}")
                # else:
                #    print("No tables found to extract DDLs from.")
                print("Information schema training (DDL extraction part) for Oracle is complex; manual DDL training is often more reliable.")
                return False # Indicate that full schema training might not have happened

            # Reformat the schema info into a string that Vanna can understand as DDL or documentation
            # This is a simplified representation.
            schema_doc = ""
            for table_name, group in df_information_schema.groupby('table_name'):
                schema_doc += f"Table {table_name}:\n"
                for _, row in group.iterrows():
                    schema_doc += f"  Column: {row['column_name']}, Type: {row['data_type']}\n"
                schema_doc += "\n"

            if schema_doc:
                self.vn.train(documentation=schema_doc) # Train this extracted info as documentation
                print("Training from extracted schema information (as documentation) completed.")
                return True
            else:
                print("No schema information extracted to train as documentation.")
                return False

        except Exception as e:
            print(f"Error during training from information schema: {e}")
            return False

    def generate_sql(self, question: str) -> str:
        """
        Generates SQL query from a natural language question.
        Args:
            question (str): The natural language question.
        Returns:
            str: The generated SQL query, or None if generation fails.
        """
        print(f"Generating SQL for question: '{question}'")
        try:
            sql_query = self.vn.ask(question=question, print_results=False) # print_results=False to just get SQL
            if sql_query:
                print(f"Generated SQL: {sql_query}")
                return sql_query
            else:
                print("SQL generation returned no result.")
                return None
        except Exception as e:
            print(f"Error during SQL generation: {e}")
            return None

# Example Usage (Illustrative - requires setup and data)
if __name__ == '__main__':
    print("Starting SQLGenerationAgent example...")
    print("IMPORTANT: Ensure Ollama is running with a model (e.g., 'ollama run mistral').")
    print("IMPORTANT: Set ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN environment variables for Oracle connection.")

    agent = SQLGenerationAgent()

    # --- Training Phase ---
    # You MUST provide your Oracle schema and sample queries for effective use.

    # Option 1: Train with DDL from a string
    # example_ddl_string = """
    // CREATE TABLE EMPLOYEES (
    //     ID INT PRIMARY KEY,
    //     NAME VARCHAR(100),
    //     DEPARTMENT_ID INT,
    //     SALARY REAL
    // );
    // CREATE TABLE DEPARTMENTS (
    //     ID INT PRIMARY KEY,
    //     NAME VARCHAR(100)
    // );
    // """
    # agent.train_from_ddl_string(example_ddl_string)

    # Option 2: Train with DDL from a .sql file
    # Create a file 'schema.sql' with your DDL statements first.
    # try:
    #     with open('schema.sql', 'w') as f:
    #         f.write("CREATE TABLE MY_TABLE (id INT, name VARCHAR(50));\n")
    #         f.write("CREATE TABLE ANOTHER_TABLE (value REAL, notes VARCHAR(200));\n")
    #     agent.train_from_ddl_file('schema.sql')
    # except Exception as e:
    #     print(f"Could not create/write schema.sql for example: {e}")


    # Option 3: Train with sample questions and SQL queries (CRITICAL for good performance)
    # This is where you provide your 8 texts and their SQL queries.
    sample_queries = [
        {
            "question": "Show total crimes and breakdown by type for District Guntur.",
            "sql": "SELECT CRIME_TYPE, COUNT(*) FROM FIR_RECORDS R JOIN DISTRICT_MASTER D ON R.DISTRICT_ID = D.DISTRICT_ID WHERE D.DISTRICT_NAME = 'Guntur' GROUP BY CRIME_TYPE;"
            # "documentation": "This query retrieves crime statistics for Guntur district." # Optional
        },
        {
            "question": "List arrests made by Officer XYZ between January 1 2025 and June 1 2025.",
            "sql": "SELECT A.* FROM ARREST_RECORDS A JOIN OFFICER_MASTER O ON A.OFFICER_ID = O.OFFICER_ID WHERE O.OFFICER_NAME = 'XYZ' AND A.ARREST_DATE BETWEEN TO_DATE('2025-01-01', 'YYYY-MM-DD') AND TO_DATE('2025-06-01', 'YYYY-MM-DD');"
        },
        # ... Add your other 6+ sample queries here ...
    ]
    # agent.train_from_sql_queries(sample_queries)

    # Option 4: Train with general documentation
    # crime_docs = """
    // FIR stands for First Information Report. It is a written document prepared by police organizations.
    // Arrest records contain details of individuals apprehended by the police.
    // """
    # agent.train_from_documentation(crime_docs, data_type="Crime Terminology")

    # Option 5: Train from connected DB's information schema (if connected and supported well)
    # if agent.oracle_connected:
    #    agent.train_from_information_schema()
    # else:
    #    print("Skipping training from information_schema as Oracle is not connected.")

    print("\n--- Querying Phase (Example) ---")
    # Ensure some training data exists for Vanna to work with.
    # If no training data is added, Vanna will likely not produce useful SQL.
    if agent.vn.get_training_data().empty:
        print("WARNING: No training data loaded into Vanna. SQL generation will likely fail or be inaccurate.")
        print("Please uncomment and adapt the training sections above with your actual schema and data.")

    test_question_1 = "How many FIRs were filed in Guntur district?"
    sql1 = agent.generate_sql(test_question_1)
    if sql1:
        print(f"Q: {test_question_1}\nSQL: {sql1}")
    else:
        print(f"Q: {test_question_1}\nSQL: Could not generate SQL.")

    test_question_2 = "which officer made most arrests last month" # More complex query
    sql2 = agent.generate_sql(test_question_2)
    if sql2:
        print(f"Q: {test_question_2}\nSQL: {sql2}")
    else:
        print(f"Q: {test_question_2}\nSQL: Could not generate SQL.")

    print("\nSQLGenerationAgent example finished.")
    print("Remember to provide actual DDL, sample queries, and documentation for effective use.")
