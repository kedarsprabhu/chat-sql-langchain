import streamlit as st
import sqlite3
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from langchain_groq import ChatGroq
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.chains.sql_database.query import create_sql_query_chain
from dotenv import load_dotenv
import os
import io

# Load environment variables
load_dotenv()

def initialize_database_from_sql(sql_content):
    """Initialize an in-memory SQLite database from SQL content."""
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    try:
        connection.executescript(sql_content)
        engine = create_engine(
            "sqlite://",
            creator=lambda: connection,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        return engine, None
    except sqlite3.Error as e:
        return None, f"Error initializing database: {str(e)}"

# Initialize Streamlit state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'current_question' not in st.session_state:
    st.session_state.current_question = ""

if 'database_initialized' not in st.session_state:
    st.session_state.database_initialized = False

if 'llm' not in st.session_state:
    st.session_state.llm = ChatGroq(
        groq_api_key=os.getenv('GROQ_API_KEY'),
        model="llama-3.1-8b-instant",
        temperature=0
    )

st.title("💬 Dynamic SQL Database Chat")
st.write("Upload your SQL file and ask questions about your database!")

# File upload section
uploaded_file = st.file_uploader("Upload SQL File", type=['sql'])

# Initialize or reinitialize database when file is uploaded
if uploaded_file is not None:
    sql_content = uploaded_file.getvalue().decode('utf-8')
    engine, error = initialize_database_from_sql(sql_content)
    
    if error:
        st.error(error)
        st.session_state.database_initialized = False
    else:
        st.session_state.database_initialized = True
        st.session_state.db = SQLDatabase(engine)
        st.success("Database initialized successfully!")

def create_chain(db, llm):
    """Create the LangChain pipeline."""
    sql_prompt = PromptTemplate.from_template(
        """You are a SQLite expert. Given an input question, create a syntactically correct SQLite query.
        Return only the raw SQL query, nothing else.
       
        Only use the following tables:
        {table_info}
        
        Ensure the query fully qualifies column names (i.e., include table names or aliases as prefixes) to avoid ambiguity.
        
        Unless specified, limit to {top_k} results.
       
        Question: {input}
        """
    )
    
    execute_query = QuerySQLDataBaseTool(db=db)
    write_query = create_sql_query_chain(llm, db, prompt=sql_prompt)
    
    result_format_prompt = PromptTemplate.from_template("""
    Based on the following information, provide a clear answer to the question:
    Original Question: {question}
    SQL Query Used: {query}
    Query Result: {result}
    Please provide a natural language answer:""")
    
    answer = result_format_prompt | llm | StrOutputParser()
    
    return (
        RunnablePassthrough.assign(query=write_query).assign(
            result=itemgetter("query") | execute_query
        )
        | answer
    )

# Main application logic
if st.session_state.database_initialized:
    # Create chain directly without caching
    chain = create_chain(st.session_state.db, st.session_state.llm)
    
    # Dynamic text area for user input
    user_question = st.text_area(
        "Ask a question about your database:",
        value=st.session_state.current_question,
        height=100,
        key="user_input",
        help="Type your question here about the uploaded database"
    )
    
    # Clear button
    if st.button("Clear Input"):
        st.session_state.current_question = ""
        st.experimental_rerun()

    if user_question:
        try:
            with st.spinner("Generating response..."):
                # Create placeholder for streaming
                response_placeholder = st.empty()
                
                # Stream the response
                response = ""
                for chunk in chain.stream({"question": user_question}):
                    response += chunk
                    # Update the placeholder with the accumulated response
                    response_placeholder.markdown(response + "▌")
                
                # Final update without the cursor
                response_placeholder.markdown(response)
                
                # Add to chat history
                st.session_state.chat_history.append({"question": user_question, "answer": response})
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    # Display chat history
    if st.session_state.chat_history:
        st.write("### Chat History")
        # Add a clear history button
        if st.button("Clear History"):
            st.session_state.chat_history = []
            st.experimental_rerun()
        
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.container():
                st.markdown(f"""
                **Q:** {chat['question']}
                
                **A:** {chat['answer']}
                """)
                st.divider()

    # Add database schema information
    with st.expander("Database Schema"):
        st.code(st.session_state.db.get_table_info())

else:
    st.info("Please upload a SQL file to begin.")

# Add a footer with helpful information
st.markdown("""
---
💡 **Tips:**
- Upload any SQL file containing your database schema and data
- View the database schema to understand available tables and columns
- Questions are stored in chat history during your session
- Make sure your SQL file is properly formatted and contains valid SQLite statements
""")