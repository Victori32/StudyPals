# StudyPals

A Streamlit application that uses CrewAI to provide educational resources and study planning assistance.

## Features

- **Learning Resources**: Get curated high-quality learning resources for any topic
- **Study Planner**: Receive a personalized study schedule based on your chosen topic

## Setup

1. Make sure you have Python installed (Python 3.8+ recommended)

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables by creating a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SERPER_API_KEY=your_serper_api_key
   ```

## Running the Application

You can run the application using the provided shell script:
```
./run_app.sh
```

Or directly with Streamlit:
```
streamlit run app.py
```

## Usage

1. Enter the topic you want to learn about in the sidebar
2. Choose whether to consider recent developments in the field
3. Navigate between the tabs to:
   - Find learning resources for your topic
   - Create a personalized study plan

## Project Structure

- `app.py`: The main Streamlit application
- `utils.py`: Utility functions for API key management and formatting
- `ssl_config.py`: SSL configuration for secure API requests
- `requirements.txt`: List of Python dependencies
- `run_app.sh`: Shell script to run the application

## Dependencies

- Streamlit: Web application framework
- CrewAI: Multi-agent framework for educational assistants
- LangChain: Framework for LLM applications
- OpenAI: API for language models

## License

This project is licensed under the MIT License. 