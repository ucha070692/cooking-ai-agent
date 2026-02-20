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
    # Enhanced recipe database with Georgian options
    recipes_db = {
        'chicken': [
            {
                'name': 'Grilled Chicken Breast',
                'ingredients': ['4 boneless chicken breasts', '2 tbsp olive oil', 'Salt and pepper to taste', '1 tsp garlic powder'],
                'instructions': 'Marinate chicken in oil and spices, grill for 6-7 minutes per side.',
                'cuisine': 'American'
            },
            {
                'name': 'Chicken Stir-Fry',
                'ingredients': ['1 lb chicken breast, sliced', '2 cups mixed vegetables', '3 tbsp soy sauce', '1 tbsp sesame oil', '2 cloves garlic, minced'],
                'instructions': 'Stir-fry chicken and vegetables, add sauce, serve over rice.',
                'cuisine': 'Asian'
            }
        ],
        'pasta': [
            {
                'name': 'Spaghetti Carbonara',
                'ingredients': ['200g spaghetti', '100g pancetta', '2 eggs', '50g grated Parmesan', 'Black pepper'],
                'instructions': 'Cook pasta, fry pancetta, mix with eggs and cheese.',
                'cuisine': 'Italian'
            },
            {
                'name': 'Pesto Pasta',
                'ingredients': ['300g pasta', '2 cups fresh basil', '1/2 cup pine nuts', '1/2 cup olive oil', '2 cloves garlic', '1/2 cup Parmesan'],
                'instructions': 'Blend basil, nuts, garlic, oil; toss with cooked pasta and cheese.',
                'cuisine': 'Italian'
            }
        ],
        'ხაჭაპური': [  # Georgian cheese bread
            {
                'name': 'იმერული ხაჭაპური (Imeruli Khachapuri)',
                'ingredients': ['500g flour', '300g sulguni cheese', '200ml milk', '50g butter', '1 egg', '1 tsp sugar', 'Salt to taste'],
                'instructions': 'Mix dough with flour, milk, egg, sugar, salt. Roll out, add cheese filling, fold and bake at 200°C for 20 minutes.',
                'cuisine': 'Georgian'
            }
        ],
        'ხინკალი': [  # Georgian dumplings
            {
                'name': 'ხინკალი (Khinkali)',
                'ingredients': ['500g ground meat (pork/beef mix)', '2 onions', '500g flour', '200ml water', 'Salt, pepper, coriander'],
                'instructions': 'Make dough, fill with spiced meat mixture, twist dumplings, boil for 10-15 minutes.',
                'cuisine': 'Georgian'
            }
        ]
    }

    query_lower = query.lower()

    # Check for Georgian keywords
    georgian_keywords = ['ხაჭაპური', 'ხინკალი', 'საჭმელი', 'ქართული', 'იმერული']
    if any(keyword in query_lower for keyword in georgian_keywords):
        results = []
        for key in recipes_db:
            if key in georgian_keywords:
                for recipe in recipes_db[key]:
                    results.append(recipe)
    else:
        # Search by ingredients or keywords
        results = []
        for category, recipes in recipes_db.items():
            if category in query_lower:
                results.extend(recipes)

    if results:
        response = f"Found {len(results)} recipe(s) for '{query}':\n\n"
        for i, recipe in enumerate(results, 1):
            response += f"**Recipe {i}: {recipe['name']}** ({recipe['cuisine']})\n"
            response += "**Ingredients:**\n" + "\n".join(f"- {ing}" for ing in recipe['ingredients']) + "\n"
            response += f"**Instructions:** {recipe['instructions']}\n\n"
        return response
    else:
        return f"No recipes found for '{query}'. Try searching for chicken, pasta, or Georgian dishes like 'ხაჭაპური' or 'ხინკალი'."

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
        model_id="openai/gpt-4o"  # Using GPT-4o for good text generation
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