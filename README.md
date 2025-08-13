# SpaceNews Agents 🌌🛰️ v0.3.0

A Python-based project designed to collect and pitch and summarize recent news about space and satellites. The project categorizes news by country/region and selects the top news for each region, providing a concise summary for easy reading.

This project was deployed in a docker container.


## Features ✨

- 📰 Collects news articles about space and satellites from the past week
- 🌍 Categorizes news by country/region
- 🏆 Utilizes a Pitcher Agent to select the top news for each region
- 📝 Uses a Scripter Agent to summarize the selected news in under 150 words
- ⚙️ Compiles the Pitcher Agent & Scripter Agent by LangGraph
- 🌐 Develops a Streamlit web interface
- 📄 Generates a downloadable docx document of filtered news with all formation
- 🤖 Sends summarized news that weren't in the database to Dingtalk using markdown. 
- 🗄️ Stores articles and events in MySQL database to prevent duplicates
- 📊 Includes a database explorer interface to browse and filter stored content

![Project Banner](./NewsAgents.jpg)

## Installation (Conda) 🛠️

To install and set up the project, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/Zifeng-Jiang/News_agent.git
    ```
2. Navigate to the project directory:
    ```bash
    cd News_agent
    ```
3. Create and activate a virtue environment(Conda):
    ```bash
    conda create --name news_agent
    conda activate news_agent
    ```
4. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5. Make sure you have Google Chrome browser and the corresponding version of ChromeDriver.
6. Ensure you have an LLM API that can be invoked by LangChain.
7. Set up MySQL database:
   ```bash
   # Install MySQL server (if not already installed)
   # For Windows: Download and install from https://dev.mysql.com/downloads/installer/
   # For Linux (Ubuntu/Debian):
   sudo apt update
   sudo apt install mysql-server
   
   # Create database and user
   mysql -u root -p
   CREATE DATABASE news_agent;
   CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'news_password';
   GRANT ALL PRIVILEGES ON news_agent.* TO 'news_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```
8. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the MySQL connection details in the `.env` file

## Usage 🚀

To start using the News Agent, run the following command:

```bash
streamlit run main.py
```

## Installation(Docker) 🐳 *Recommended*
Use Docker Compose to set up both the application and the MySQL database:

```bash
# Start the containers
docker-compose up -d

# To view logs
docker-compose logs -f

# To stop containers
docker-compose down
```

You can change the port number from 8502 to any port number in the docker-compose.yml file.

### Environment Variables

The application uses the following environment variables in the `.env` file:

| Variable Name              | Description                                                        |
|----------------------------|--------------------------------------------------------------------|
| DISPLAY                    | Display server for Xvfb (used for headless Chrome)                 |
| DASHSCOPE_API_KEY          | API key for DashScope LLM service                                  |
| OPENAI_API_VERSION         | Version of the OpenAI API to use                                   |
| AZURE_OPENAI_API_KEY       | API key for Azure OpenAI service                                   |
| AZURE_OPENAI_ENDPOINT      | Endpoint URL for Azure OpenAI service                              |
| DINGTALK_BOT_ACCESS_TOKEN  | Access token for DingTalk bot integration                          |
| MYSQL_HOST                 | Hostname for MySQL database (use 'db' for Docker Compose setup)    |
| MYSQL_DATABASE             | Name of the MySQL database                                         |
| MYSQL_USER                 | Username for MySQL database                                        |
| MYSQL_PASSWORD             | Password for MySQL database                                        |

Example `.env` file (fill in your own values):

```
DISPLAY=
DASHSCOPE_API_KEY=
OPENAI_API_VERSION=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
DINGTALK_BOT_ACCESS_TOKEN=
MYSQL_HOST=
MYSQL_DATABASE=
MYSQL_USER=
MYSQL_PASSWORD=
```

> **Note**: For production deployments, never commit sensitive credentials to your repository. Use environment variables or secrets management appropriate for your deployment platform.

## Database Features 🗄️

The project now uses MySQL to store all articles and events:

- **Prevents Duplicates**: Articles and events are checked against the database before being added
- **Database Explorer**: View and search through stored articles and events using the Database Explorer page
- **Filtering**: Filter articles by region, tag, and date range
- **Export**: Download article and event data as CSV files
- **Detail View**: View complete article and event details

To access the Database Explorer, navigate to the "Database Explorer" page from the sidebar in the Streamlit app.


## Contributing 🤝
Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository
2. Create a new branch  `git checkout -b feature-branch`
3. Commit your changes  `git commit -m 'Add new feature'`
4. Push to the branch  `git push origin feature-branch`
5. Open a pull request

## Contact 📧

For any inquiries or feedback, please contact Zifeng Jiang at `jiang.zifeng@star.vision`.

