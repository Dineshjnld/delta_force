# CCTNS Copilot - AGENTS.md

This document outlines the architecture and responsibilities of the different agents
within the CCTNS Copilot system. This system is designed to provide a voice-enabled
natural language interface for querying the CCTNS database.

## Project Goal

To create an intelligent, voice-enabled system that allows police personnel at all
levels to seamlessly access and interact with the CCTNS database using natural
language voice commands.

## Architecture Overview

The system will follow a modular agent-based architecture, with each agent
responsible for a specific part of the workflow:

1.  **Voice Input Agent**: Captures voice input, transcribes it to text.
2.  **Text Processing Agent**: Cleans, translates (if necessary), and prepares the text for SQL generation.
3.  **SQL Generation Agent**: Converts the processed text into a safe SQL query.
4.  **Database Interaction Agent**: Executes the SQL query against the Oracle CCTNS database and retrieves results.
5.  **Reporting and Visualization Agent**: Formats the results, generates reports (tables, charts), and provides export options.

## Agent Responsibilities

### 1. Voice Input Agent (`cctns_copilot/voice_input_agent/transcriber.py`)
   - **Input**: Microphone audio stream.
   - **Processing**:
     - Captures audio using `SpeechRecognition` library.
     - Placeholder logic for transcription:
       - Primary: IndicConformer (model integration TBD).
       - Fallback: Whisper Medium model (model integration TBD, `transformers` library).
     - Currently uses `recognizer.recognize_google` as a temporary fallback for demonstration if main models aren't loaded.
   - **Output**: Transcribed text string.
   - **Key Libraries/Technologies**: `SpeechRecognition`, `transformers` (for Whisper), `torch`, `torchaudio`. (IndicConformer library TBD).
   - **Status**: Basic structure implemented; model integration and full functionality pending.

### 2. Text Processing Agent (`cctns_copilot/text_processing_agent/processor.py`)
   - **Input**: Raw transcribed text from the Voice Input Agent.
   - **Processing**:
     - Grammar Correction: Uses `language-tool-python` (requires Java runtime).
     - Telugu to English Translation: Uses a T5 model via `transformers` library.
       - Currently uses `'t5-small'` as a placeholder. For effective translation, a model like `'ai4bharat/IndicT5-base'` should be configured.
   - **Output**: Cleaned and translated English text query.
   - **Key Libraries/Technologies**: `language-tool-python`, `transformers` (for T5), `torch`, `sentencepiece`.
   - **Status**: Core logic implemented with placeholder T5 model. Requires Java for grammar correction and a suitable Te-En T5 model for effective translation.

### 3. SQL Generation Agent (`cctns_copilot/sql_generation_agent/sql_generator.py`)
   - **Input**: Cleaned English text query from the Text Processing Agent.
   - **Processing**:
     - Leverages Vanna AI (`vanna` library).
     - Language Model: Uses Ollama to serve a local LLM (e.g., Mistral, Llama). Configurable via `OLLAMA_MODEL_NAME` env var. Ollama must be running separately.
     - Vector Store: Uses ChromaDB (`chromadb` library) for storing training data (DDL, SQL samples, documentation). Path configurable via `CHROMA_DB_PATH` env var.
     - Oracle Connection: Connects to Oracle DB (`oracledb` library) to fetch schema for training if specified. Credentials via env vars (`ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN`).
     - Training: Methods provided to train Vanna with DDLs, SQL question-answer pairs, and general documentation. **User must provide this training data for the agent to be effective.**
     - Converts natural language to SQL (`SELECT` statements only).
   - **Output**: SQL query string.
   - **Key Libraries/Technologies**: `vanna`, `oracledb`, `chromadb`. (Ollama runs as a separate service).
   - **Status**: Core logic implemented. Effectiveness is highly dependent on user-provided Oracle credentials and comprehensive training data (DDLs, Q&A pairs).

### 4. Database Interaction Agent (`cctns_copilot/database_interaction_agent/db_connector.py`)
   - **Input**: SQL query string (expected to be a `SELECT` statement) from the SQL Generation Agent.
   - **Processing**:
     - Connects to the Oracle CCTNS database using `oracledb` driver. Credentials from env vars.
     - Executes the SQL query. **Includes a safety check to only allow `SELECT` statements.**
     - Retrieves query results.
   - **Output**: Query results as a Pandas DataFrame.
   - **Key Libraries/Technologies**: `oracledb`, `pandas`.
   - **Status**: Implemented and functional, assuming correct Oracle setup and credentials.

### 5. Reporting and Visualization Agent (`cctns_copilot/reporting_visualization_agent/reporter_ui.py`)
   - **Input**: Query results (Pandas DataFrame) from the Database Interaction Agent.
   - **Processing (UI via Streamlit)**:
     - Displays query results in a paginated table.
     - Allows users to assign a name and tags to the dataset (metadata stored in Streamlit session state).
     - Generates visualizations (bar, line, pie, scatter charts) using Plotly Express. Users can select chart types and relevant columns.
     - Allows users to queue selected charts for inclusion in a PDF report.
     - Export Options:
       - Download raw data as CSV.
       - Generate and download a PDF report containing:
         - Report title (dataset name).
         - Generated SQL query (if available).
         - A summary data table (currently basic, truncates long content/rows).
         - Queued charts (embedded as images).
   - **Output**: Interactive web UI for displaying reports; downloadable CSV and PDF files.
   - **Key Libraries/Technologies**: `streamlit`, `pandas`, `plotly`, `matplotlib` (as a fallback or for specific plot types if needed by Plotly), `fpdf2` (for PDF generation).
   - **Status**: Core UI and functionalities implemented. PDF table generation is basic. Integration with other agents for data flow is pending.

## Development Guidelines & Integration Notes
- **Modularity**: Each agent is in its own Python module.
- **Data Flow**:
    1. Voice Input Agent: Speech -> Text
    2. Text Processing Agent: Raw Text -> Processed (Translated/Corrected) Text
    3. SQL Generation Agent: Processed Text -> SQL Query
    4. Database Interaction Agent: SQL Query -> Pandas DataFrame
    5. Reporting Agent: Pandas DataFrame -> UI Display, Charts, Exports (CSV/PDF)
- **Configuration**: Key configurations (Ollama model, DB credentials, paths) are expected to be managed via environment variables (e.g., using a `.env` file and `python-dotenv`). Placeholder values are present in scripts.
- **Security**:
    - The Database Interaction Agent restricts execution to `SELECT` queries.
    - Database credentials should be securely managed.
    - The Vanna AI setup relies on the LLM not generating malicious SQL; further output validation could be added if necessary.
- **Dependencies**: All Python dependencies are listed in `cctns_copilot/requirements.txt`. External dependencies include:
    - Java Runtime Environment (for `language-tool-python`).
    - Ollama service running with a downloaded model.
    - Oracle Database accessible with client libraries correctly configured if `oracledb` thin mode is insufficient.
- **Testing**: Each agent script includes a basic `if __name__ == '__main__':` block for standalone testing or demonstration. Comprehensive unit and integration tests are recommended.

## Setup and Running
1.  **Install Dependencies**:
    ```bash
    pip install -r cctns_copilot/requirements.txt
    ```
2.  **Setup External Services**:
    - Install and run Ollama: `ollama serve` (and `ollama pull <model_name>` e.g., `ollama pull mistral`).
    - Ensure Java JRE is installed.
    - Ensure Oracle DB is accessible and Oracle client (if needed by `oracledb`) is configured.
3.  **Environment Variables**: Create a `.env` file in the project root or set environment variables for:
    - `OLLAMA_MODEL_NAME`
    - `CHROMA_DB_PATH` (optional, defaults to `./chroma_db_cctns`)
    - `ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN`
4.  **Train SQL Generation Agent**:
    - Modify and run `cctns_copilot/sql_generation_agent/sql_generator.py` to train Vanna with your specific Oracle schema DDLs, Q&A pairs, and documentation. This step is **critical**.
5.  **Run the Application**:
    - The primary user interface is the Reporting and Visualization Agent (Streamlit app).
    - To run it (after other agents are integrated or data is manually fed):
      ```bash
      streamlit run cctns_copilot/reporting_visualization_agent/reporter_ui.py
      ```
    - A master script or orchestration logic would be needed to tie all agents together for a seamless voice-to-report flow.

This `AGENTS.md` will be updated as the project evolves further, especially regarding agent integration.
