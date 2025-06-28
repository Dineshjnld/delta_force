# Neuro SAN: Agent Orchestration Platform

Neuro SAN is a comprehensive platform for developing, deploying, and managing sophisticated AI agents and multi-agent systems. It provides a robust framework for building agents that can leverage a variety of tools and interact with different services.

## Overview

This project enables developers to:

*   Create autonomous AI agents for diverse tasks.
*   Integrate agents with external tools and APIs (e.g., search engines, email services).
*   Define and manage complex agent networks and workflows.
*   Run agents locally or deploy them as services.
*   Utilize different web client interfaces (Flask, Nsflow) for interaction and visualization.

## Key Features

*   **Agent Framework:** Core components for building individual agents.
*   **Tool Integration:** A collection of "coded tools" that agents can use to perform actions (e.g., `gmail`, `brave_search`, `website_search`).
*   **Agent Registries:** Configuration-driven setup for agents and agent networks using HOCON files.
*   **Multiple Server Components:** Includes the main Neuro SAN server and potentially other specialized servers (e.g., `servers/a2a`, `servers/mcp`).
*   **Web Client Options:**
    *   **Nsflow:** A modern web client for interacting with agents and visualizing networks.
    *   **Flask Web Client:** An alternative web client for simpler use cases.
*   **Example Applications:** A rich set of example agents and applications in the `apps/` directory to demonstrate capabilities and provide starting points.
*   **Deployment Ready:** Includes Docker configurations (`deploy/Dockerfile`) for containerized deployments.
*   **Testing and Linting:** Comprehensive `Makefile` for easy setup, linting, and testing.
*   **Documentation:** Includes user guides, developer guides, and examples in the `docs/` directory.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.8 or higher
*   `make` utility (common on Linux/macOS; Windows users might need to install it separately, e.g., via Chocolatey or WSL)

### Installation and Setup

1.  **Clone the repository:**
    If you haven't already, clone the repository to your local machine:
    ```bash
    # Replace with the actual URL of this repository
    git clone https://github.com/example-user/neuro-san-project.git
    cd neuro-san-project
    ```

2.  **Create a virtual environment and install dependencies:**
    The `Makefile` provides a convenient way to set up the environment and install all necessary packages.
    ```bash
    make install
    ```
    This command will:
    *   Create a Python virtual environment in a directory named `venv` if it doesn't already exist.
    *   Install all dependencies listed in `requirements.txt` and `requirements-build.txt`.

3.  **Activate the virtual environment:**
    Before running the application or development tasks, activate the virtual environment:
    *   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

### Running the Platform

The main entry point for running the Neuro SAN platform is `run.py`.

1.  **Ensure your virtual environment is activated.**

2.  **Run the script:**
    ```bash
    python run.py
    ```
    By default, this will attempt to start the Neuro SAN server and the Nsflow web client.

3.  **Common Runtime Options:**
    The `run.py` script accepts several command-line arguments to customize its behavior:

    *   `--server-only`: Run only the Neuro SAN server without any client.
        ```bash
        python run.py --server-only
        ```
    *   `--client-only`: Run only the Nsflow client (useful if the server is running elsewhere).
        ```bash
        python run.py --client-only
        ```
    *   `--use-flask-web-client`: Use the alternative Flask-based web client instead of Nsflow.
        ```bash
        python run.py --use-flask-web-client
        ```
    *   `--server-host <host>`: Specify the host for the server (default: `localhost`).
    *   `--server-grpc-port <port>`: Specify the gRPC port for the server (default: `30011`).
    *   `--server-http-port <port>`: Specify the HTTP port for the server (default: `8080`).
    *   `--nsflow-port <port>`: Specify the port for the Nsflow client (default: `4173`).
    *   `--web-client-port <port>`: Specify the port for the Flask web client when `--use-flask-web-client` is active (default: `5003`).

    For a full list of options, you can try:
    ```bash
    python run.py --help
    ```

4.  **Accessing the Web Client:**
    *   **Nsflow:** If running, typically accessible at `http://localhost:4173` (or the port specified by `--nsflow-port`).
    *   **Flask Web Client:** If running, typically accessible at `http://localhost:5003` (or the port specified by `--web-client-port`).

## Project Structure

The project is organized into several key directories:

*   `apps/`: Contains example applications and agents built using the Neuro SAN platform. These serve as practical examples and starting points for new projects.
*   `cctns_copilot/`: Appears to contain components for a "Cognizant CCTNS Copilot", possibly a specialized set of agents or tools.
*   `coded_tools/`: A library of reusable tools that agents can utilize to perform specific actions or interact with external services (e.g., web search, file operations, API interactions).
*   `deploy/`: Holds deployment-related files, such as `Dockerfile` for building container images and shell scripts for build and run processes.
*   `docs/`: Contains detailed documentation, including user guides, developer guides, examples, and diagrams.
*   `logs/`: Default directory where runtime logs are stored (created automatically).
*   `registries/`: Stores HOCON (`.hocon`) configuration files that define agents, agent networks, and their properties. `manifest.hocon` is a key file that lists available agent configurations.
*   `run.py`: The main executable script to start the Neuro SAN server and web client(s).
*   `servers/`: Contains the source code for the core Neuro SAN server and potentially other specialized server components.
*   `tests/`: Includes unit tests and integration tests for various parts of the platform.
*   `toolbox/`: Contains information about the available tools for agents, likely used by the platform to understand tool capabilities.
*   `Makefile`: Provides convenient commands for common development tasks like installation, linting, and testing.
*   `.env.example`: An example environment file. Copy this to `.env` to set local environment variables for configuration (e.g., API keys, default ports).
*   `AGENTS.md`: May contain instructions or tips for AI agents working with this codebase.

## Running Tests

The project uses `pytest` for running tests. The `Makefile` provides a simple command to execute them.

1.  **Ensure your virtual environment is activated** (see Installation section).
2.  **Run the tests:**
    ```bash
    make test
    ```
    This command will also run linters before executing the tests and provide a coverage report.

## Linting

The project uses `isort`, `black`, `flake8`, and `pylint` for code formatting and linting. You can run these checks using the `Makefile`.

1.  **Ensure your virtual environment is activated.**
2.  **Run linters:**
    ```bash
    make lint
    ```
    This will format and lint the code in `run.py`, `apps/`, and `coded_tools/`.
    To lint test files, use:
    ```bash
    make lint-tests
    ```

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1.  **Fork the Project.**
2.  **Create your Feature Branch:**
    ```bash
    git checkout -b feature/AmazingFeature
    ```
3.  **Implement your changes.**
    *   Ensure your code adheres to the project's coding style.
    *   Run linters before committing: `make lint` (and `make lint-tests` if you modify tests).
    *   Add tests for any new features or bug fixes. Ensure all tests pass: `make test`.
4.  **Commit your Changes:**
    ```bash
    git commit -m 'Add some AmazingFeature'
    ```
    Follow conventional commit messages if applicable.
5.  **Push to the Branch:**
    ```bash
    git push origin feature/AmazingFeature
    ```
6.  **Open a Pull Request** against the `main` (or appropriate) branch of the original repository.

Please ensure your pull request describes the changes clearly.

## License

This project is licensed under the terms of the Academic Public License.
See the `LICENSE.txt` file for more details.

Note: According to the `run.py` header, "Purchase of a commercial license is mandatory for any use of the neuro-san-studio SDK Software in commercial settings." Please review the license carefully.

## What We've Done in This Code (Example)

This section is intended to be updated by the project maintainers to highlight key features, development milestones, or specific functionalities implemented in the codebase.

*   **Initial Project Scaffolding:** Set up the basic directory structure and build tools.
*   **Core Agent Framework:** Implemented the foundational classes for agent creation and execution.
*   **Implemented Tool X:** Added `coded_tools/tool_x.py` for enhanced agent capabilities.
*   **Developed Example App Y:** Created `apps/app_y/` to showcase a specific use case.

*(Please replace this example content with actual project achievements.)*

---

## Hackathon Use Case: AI-Powered CCTNS Voice Querying

This section details a specific application of the Neuro SAN platform developed for a hackathon: an AI-powered, voice-based system for natural language querying and report generation from CCTNS (Crime and Criminal Tracking Network & Systems) data.

### Objective

To create an intelligent, voice-enabled system that allows police personnel at all levels to seamlessly access and interact with the CCTNS database using natural language voice commands. This solution aims to democratize data access by removing technical barriers such as SQL query formulation, enabling officers—from constables to senior officials—to retrieve accurate and timely crime and investigation data effortlessly. The system will interpret spoken queries, translate them into precise database requests, and generate structured, easy-to-understand reports. By incorporating real-time error detection, step-by-step clarifications, and multi-language support, the system ensures reliable communication and enhances user confidence in accessing critical information, thereby improving decision-making and operational efficiency.

### Scope

The solution encompasses a voice command interface supporting English and optionally Telugu, integrated with an AI-powered natural language processing engine that converts spoken queries into safe SQL statements for accessing the CCTNS database. A middleware layer ensures secure data handling, input sanitization, and access control. The system will generate readable reports featuring tables, charts, and summaries suitable for field operations, intelligence review, and management meetings. Interactive error handling will assist users in refining queries through clarifications and suggestions, preventing misinterpretation or data inaccuracies. This prototype will demonstrate a scalable client-server architecture adaptable to various police stations, paving the way for comprehensive AI-assisted utilization of CCTNS by police personnel across Andhra Pradesh.

### Our Approach & Agent Functionalities

This solution leverages the Neuro SAN platform by orchestrating a series of specialized agents, primarily located within the `cctns_copilot/` directory. Each agent performs a distinct step in the voice-to-report pipeline:

1.  **Voice Input Agent (`cctns_copilot/voice_input_agent/transcriber.py`)**
    *   **Functionality:** Captures audio input from the user's microphone. It supports both English (`en-IN`) and Telugu (`te-IN`) languages.
    *   The agent is designed to first attempt transcription using an "IndicConformer" model (placeholder, requires full integration) for potentially higher accuracy in Indian languages, and then fall back to an OpenAI "Whisper" model (placeholder, requires full integration) if needed or for broader language support.
    *   Currently, as a temporary measure, it may use `speech_recognition.recognize_google` if the primary models are not fully configured.

2.  **Text Processing Agent (`cctns_copilot/text_processing_agent/processor.py`)**
    *   **Functionality:** Processes the transcribed text.
        *   If the input language is Telugu, it attempts translation to English using a T5-based model. (Note: The current default `t5-small` is a placeholder; a model like `ai4bharat/IndicT5-base` is recommended for accurate Telugu-to-English translation).
        *   Performs grammar correction on the English text (either originally English or translated) using `language_tool_python` to improve clarity and downstream processing accuracy.

3.  **SQL Generation Agent (`cctns_copilot/sql_generation_agent/sql_generator.py`)**
    *   **Functionality:** Converts the processed natural language query into an SQL query.
    *   It utilizes the Vanna AI library, interfacing with a Large Language Model (LLM) via Ollama (e.g., Mistral, Llama) and using a ChromaDB vector store for contextual information and training data.
    *   The agent can be trained with DDL schemas, question-SQL pairs, and textual documentation to understand the CCTNS database structure and common query patterns, ensuring more accurate SQL generation.

4.  **Database Interaction Agent (`cctns_copilot/database_interaction_agent/db_connector.py`)**
    *   **Functionality:** Securely connects to the CCTNS Oracle database using predefined credentials.
    *   It is responsible for executing the SQL queries generated by the `SQLGenerationAgent`.
    *   As a safety precaution, it is restricted to only execute `SELECT` statements, preventing accidental data modification or deletion.
    *   Returns the query results as a Pandas DataFrame for further processing.

5.  **Reporting & Visualization Agent (`cctns_copilot/reporting_visualization_agent/reporter_ui.py`)**
    *   **Functionality:** Presents the retrieved data to the user in a user-friendly web interface built with Streamlit.
    *   Displays data in interactive tables with pagination.
    *   Allows users to generate various types of charts (e.g., bar, line, pie, scatter plots) from the data using Plotly Express.
    *   Enables users to export the raw data as a CSV file.
    *   Provides functionality to compile and download a comprehensive PDF report containing both the data tables and the generated visualizations.

### Specific Setup for CCTNS Use Case

To run the CCTNS voice querying solution locally, in addition to the general platform setup, ensure the following:

1.  **Python Dependencies:**
    *   Install all specific dependencies for the CCTNS copilot agents. These are listed in `cctns_copilot/requirements.txt`. You might want to install them into your existing virtual environment:
        ```bash
        pip install -r cctns_copilot/requirements.txt
        ```

2.  **Environment Variables:**
    *   Set the following environment variables, typically in a `.env` file in the project root:
        *   `ORACLE_USER`: Your Oracle database username.
        *   `ORACLE_PASSWORD`: Your Oracle database password.
        *   `ORACLE_DSN`: The Oracle database connection string (e.g., `your_oracle_host:your_oracle_port/your_oracle_service_name`).
        *   `OLLAMA_MODEL_NAME`: The name of the Ollama model to be used by Vanna for SQL generation (e.g., `mistral`, `llama2`).
        *   `CHROMA_DB_PATH` (Optional): Path to persist the ChromaDB vector store for Vanna. Defaults to `./chroma_db_cctns` if not set.

3.  **External Services & Runtimes:**
    *   **Ollama:** Ensure the Ollama service is running and the specified `OLLAMA_MODEL_NAME` (e.g., `mistral`) has been pulled (`ollama pull mistral`). Vanna connects to this service for LLM capabilities.
    *   **Oracle Client:** Oracle client libraries must be installed and correctly configured on your system for the `oracledb` Python package to connect to the Oracle database.
    *   **Java Runtime Environment (JRE):** The `language-tool-python` package (used by the Text Processing Agent) requires a JRE to be installed and accessible.

4.  **Model Integration Considerations:**
    *   **Voice Input Agent:** For optimal performance, especially with Telugu, the placeholder "IndicConformer" and "Whisper" models in `cctns_copilot/voice_input_agent/transcriber.py` would need to be replaced with fully integrated, pre-trained models.
    *   **Text Processing Agent:** Similarly, for accurate Telugu-to-English translation, the placeholder `t5-small` model in `cctns_copilot/text_processing_agent/processor.py` should be replaced with a model specifically trained for this task (e.g., `ai4bharat/IndicT5-base`). This may involve downloading model weights and adjusting the loading mechanism in the script.

5.  **Vanna Training (SQL Generation Agent):**
    *   For the `SQLGenerationAgent` to be effective, it needs to be trained on the CCTNS database schema and query patterns. This involves:
        *   Providing DDL statements (e.g., `CREATE TABLE ...`) for the relevant CCTNS tables.
        *   Supplying example question-SQL pairs.
        *   Optionally, adding textual documentation about the database.
    *   The training functions are present in `cctns_copilot/sql_generation_agent/sql_generator.py` and would need to be run with appropriate data.
