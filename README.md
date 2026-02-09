# Cooking AI Agent

A web-based AI cooking assistant that helps with recipe search and ingredient extraction using GitHub models.

## Features

- **Recipe Search**: Find recipes based on ingredients, cuisine type, or keywords
- **Ingredient Extraction**: Extract ingredients from recipe texts
- **Interactive Console**: Chat with the AI assistant in real-time
- **Multi-turn Conversations**: Maintains context across interactions

## Prerequisites

- Python 3.10 or higher
- GitHub Personal Access Token with access to GitHub Models

## Setup

1. **Clone or download** this project to your local machine.

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up GitHub Token**:
   - Create a GitHub Personal Access Token (PAT) with access to GitHub Models
   - Edit the `.env` file and replace `your_github_token_here` with your actual token:
     ```
     GITHUB_TOKEN=ghp_your_actual_token_here
     ```

## Deployment

### Local Development
Run locally:
```bash
pip install -r requirements.txt
streamlit run main.py
```

### Deploy to Streamlit Cloud
1. Push this repo to a public GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your GitHub account
3. Select your repository and set the main file path to `main.py`
4. In app settings, add your GitHub token as a secret:
   - Key: `GITHUB_TOKEN`
   - Value: `ghp_your_token_here`
5. Deploy and get your public URL!

The app will be accessible from anywhere with a web browser.

## How It Works

The application uses Microsoft's Agent Framework with OpenAI's GPT-4o model hosted on GitHub Models. The AI agent is equipped with specialized tools for:

- **Recipe Search**: A tool that searches for recipes based on user queries
- **Ingredient Extraction**: A tool that parses recipe text to extract ingredient lists

The agent maintains conversation context and can handle multi-turn interactions.

## Configuration

- **Model**: Currently uses `openai/gpt-4o` from GitHub Models
- **Environment Variables**: Configure your GitHub token in `.env`
- **Tools**: Custom tools for recipe search and ingredient extraction

## Troubleshooting

- **"Authentication failed"**: Check that your GitHub token is valid and has the necessary permissions
- **"Model not found"**: Ensure the model ID is correct (currently `openai/gpt-4o`)
- **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`

## Dependencies

- `agent-framework-azure-ai==1.0.0b260107`: Microsoft Agent Framework for Azure AI
- `agent-framework-core==1.0.0b260107`: Core Agent Framework components
- `openai`: OpenAI Python client
- `python-dotenv`: Environment variable management
- `streamlit`: Web app framework

## License

This project is for educational and demonstration purposes.