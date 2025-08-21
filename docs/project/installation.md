# Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd mds7
    ```
2.  **Install project dependencies:**
    This project uses Poetry. Ensure it is installed (`pip install poetry`).
    ```bash
    poetry install
    ```
3.  **Set up Environment Variables:**
    Create a `.env` file in the project root. The application is configured to use Google Cloud Vertex AI, so you must provide your project details.

    **Example `.env` configuration:**
    ```.env
    GOOGLE_GENAI_USE_VERTEXAI=TRUE
    GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION"
    ```

4.  **Authenticate with Google Cloud:**
    The application uses Application Default Credentials (ADC) to authenticate with Google Cloud. Run the following command:
    ```bash
    gcloud auth application-default login
    ```
