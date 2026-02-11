from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from openai import AsyncOpenAI
import asyncio
import os
from dotenv import load_dotenv
from typing import Annotated
import streamlit as st

# Load environment variables
load_dotenv()

# Define tools
def extract_ingredients(recipe_text: Annotated[str, "The recipe text to extract ingredients from."]) -> str:
    """
    Extract ingredients from a recipe text.
    """
    lines = recipe_text.split('\n')
    ingredients = []
    for line in lines:
        line = line.strip()
        # Simple heuristic: lines that start with - or contain quantities
        if line.startswith('-') or (any(char.isdigit() for char in line[:10]) and ('cup' in line.lower() or 'tbsp' in line.lower() or 'tsp' in line.lower() or 'oz' in line.lower() or 'lb' in line.lower() or 'g' in line.lower())):
            ingredients.append(line)
    if ingredients:
        return "Extracted Ingredients:\n" + '\n'.join(ingredients)
    else:
        return "No ingredients found in the provided text."

def search_recipes(query: Annotated[str, "Keywords or ingredients to search for recipes."]) -> str:
    """
    Search for recipes based on query.
    """
    # Dummy implementation - in a real app, this would query a database or API
    query_lower = query.lower()
    if 'chicken' in query_lower:
        return """
Found recipes for chicken:

Recipe 1: Grilled Chicken Breast
Ingredients:
- 4 boneless chicken breasts
- 2 tbsp olive oil
- Salt and pepper to taste
- 1 tsp garlic powder
Instructions: Marinate chicken in oil and spices, grill for 6-7 minutes per side.

Recipe 2: Chicken Stir-Fry
Ingredients:
- 1 lb chicken breast, sliced
- 2 cups mixed vegetables
- 3 tbsp soy sauce
- 1 tbsp sesame oil
- 2 cloves garlic, minced
Instructions: Stir-fry chicken and vegetables, add sauce, serve over rice.
"""
    elif 'pasta' in query_lower:
        return """
Found recipes for pasta:

Recipe 1: Spaghetti Carbonara
Ingredients:
- 200g spaghetti
- 100g pancetta
- 2 eggs
- 50g grated Parmesan
- Black pepper
Instructions: Cook pasta, fry pancetta, mix with eggs and cheese.

Recipe 2: Pesto Pasta
Ingredients:
- 300g pasta
- 2 cups fresh basil
- 1/2 cup pine nuts
- 1/2 cup olive oil
- 2 cloves garlic
- 1/2 cup Parmesan
Instructions: Blend basil, nuts, garlic, oil; toss with cooked pasta and cheese.
"""
    else:
        return f"""
Sample Recipe based on '{query}':

Recipe: Simple {query.title()} Dish
Ingredients:
- Main ingredient: {query}
- Seasonings: salt, pepper
- Oil for cooking
Instructions: Season and cook the main ingredient to taste.
"""

# Initialize the agent (global for Streamlit)
@st.cache_resource
def get_agent():
    # Initialize OpenAI client for GitHub models
    openai_client = AsyncOpenAI(
        base_url="https://models.github.ai/inference",
        api_key=st.secrets["GITHUB_TOKEN"],
    )

    # Create chat client
    chat_client = OpenAIChatClient(
        async_client=openai_client,
        model_id="cohere/cohere-command-a"  # Using GPT-4o for good text generation
    )

    # Create the cooking assistant agent
    agent = ChatAgent(
        chat_client=chat_client,
        name="CookingAssistant",
        instructions="""You are a helpful cooking AI assistant. Your main capabilities are:
- Searching for recipes based on ingredients, cuisine type, or keywords
- Extracting ingredients from recipe texts
- Providing cooking advice and tips
- Suggesting recipe modifications

When users ask to search for recipes, use the search_recipes tool.
When users provide recipe text and ask to extract ingredients, use the extract_ingredients tool.
For general cooking questions, answer directly using your knowledge.
Be friendly, informative, and encouraging.""",
        tools=[extract_ingredients, search_recipes],
    )
    return agent

def main():
    st.title("🍳 Cooking AI Agent")
    st.write("Chat with me about recipes, ingredients, or cooking tips!")

    agent = get_agent()

    # Session state for conversation
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'thread' not in st.session_state:
        st.session_state.thread = agent.get_new_thread()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me about cooking..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = asyncio.run(agent.run(prompt, thread=st.session_state.thread))
                    response = result.text
                    st.markdown(response)
                    # Add assistant message to history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"An error occurred: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()