# SQL Chat Application

A Streamlit-based interactive application that allows users to query SQL databases using natural language. Powered by LangChain and Groq LLM, this application enables users to upload SQL files and ask questions about their data without writing SQL queries directly.

## 🌐 Live Demo

Access the live application at: [https://chat-sql-langchain.streamlit.app/](https://chat-sql-langchain.streamlit.app/)

## ✨ Features

- **Natural Language Queries**: Ask questions about your database in plain English
- **Dynamic Database Loading**: Upload any SQL file to create an in-memory SQLite database
- **Interactive Chat Interface**: Stream responses in real-time
- **Chat History**: Keep track of previous questions and answers
- **Schema Visibility**: Examine your database structure through the schema viewer
- **Clear and Intuitive UI**: Easy-to-use interface with helpful tooltips

## 🚀 Getting Started

### Prerequisites

```bash
pip install requirements.txt
```

### Environment Variables

Create a `.env` file in your project root with:

```
GROQ_API_KEY=your_groq_api_key_here
```

### Running Locally

1. Clone the repository
2. Install dependencies
3. Set up your environment variables
4. Run the application:

```bash
streamlit run sqlchat.py
```

## 📖 How to Use

1. **Upload SQL File**
   - Click the "Upload SQL File" button
   - Select a valid SQL file containing your database schema and data

2. **Ask Questions**
   - Type your question in the text area
   - View the generated response in real-time
   - See the chat history below

3. **View Schema**
   - Expand the "Database Schema" section to see available tables and columns

4. **Manage History**
   - Use the "Clear History" button to reset the chat
   - Use "Clear Input" to reset the question field

## 🛠️ Technical Details

- **Framework**: Streamlit
- **Database**: SQLite (in-memory)
- **LLM Integration**: Groq (llama-3.1-8b-instant model)
- **Query Processing**: LangChain for SQL query generation and natural language processing

## ⚠️ Limitations

- Only supports SQLite-compatible SQL files
- Database is stored in-memory and resets on page refresh
- Requires proper SQL file formatting
- Limited to the capabilities of the Groq llama-3.1-8b-instant model

## 💡 Tips for Best Results

- Ensure your SQL file is properly formatted
- Reference the schema viewer to understand available data
- Be specific in your questions
- Use clear, concise natural language queries
