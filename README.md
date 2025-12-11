# Telegram Store Channel Manager

This is a desktop application for managing a Telegram store channel, built with Python, PyQt6, and Telethon.

## Getting Started

Follow these instructions to get the application up and running on your local machine.

### Prerequisites

*   Python 3.8 or higher
*   pip

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  **Create a `config.ini` file:**

    Make a copy of the `config.ini.example` file and rename it to `config.ini`.

    ```bash
    cp config.ini.example config.ini
    ```

2.  **Add your Telegram API credentials:**

    Open the `config.ini` file and replace the placeholder values with your own `api_id` and `api_hash`. You can obtain these from [my.telegram.org](https://my.telegram.org).

    ```ini
    [telegram]
    api_id = 1234567
    api_hash = 0123456789abcdef0123456789abcdef
    ```

### Running the Application

Once you have completed the installation and configuration steps, you can run the application with the following command:

```bash
python src/main.py
```
