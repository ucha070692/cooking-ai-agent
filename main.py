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

# Common ingredient constants (to reduce duplication warnings)
FLOUR_500G = "500g flour"
ONIONS_2 = "2 onions"
CORIANDER_FRESH = "Fresh coriander"

# Recipe database
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
            'ingredients': [FLOUR_500G, '300g sulguni cheese', '200ml milk', '50g butter', '1 egg', '1 tsp sugar', 'Salt to taste'],
            'instructions': 'Mix dough with flour, milk, egg, sugar, salt. Roll out, add cheese filling, fold and bake at 200°C for 20 minutes.',
            'cuisine': 'Georgian',
            'image': 'https://images.unsplash.com/photo-1579954115545-a95591f28bfc?w=400&h=300&fit=crop'
        },
        {
            'name': 'მეგრული ხაჭაპური (Megruli Khachapuri)',
            'ingredients': [FLOUR_500G, '400g sulguni cheese', '100g butter', '1 egg', '200ml milk', 'Salt to taste'],
            'instructions': 'Make dough, fill with cheese, fold into boat shape, add butter on top. Bake at 220°C for 15-20 minutes.',
            'cuisine': 'Georgian',
            'image': 'https://images.unsplash.com/photo-1579954115566-e66808b81b2e?w=400&h=300&fit=crop'
        }
    ],
    'ხინკალი': [  # Georgian dumplings
        {
            'name': 'ხინკალი (Khinkali)',
            'ingredients': ['500g ground meat (pork/beef mix)', ONIONS_2, FLOUR_500G, '200ml water', 'Salt, pepper, coriander'],
            'instructions': 'Make dough, fill with spiced meat mixture, twist dumplings, boil for 10-15 minutes. Eat by hand, drink juice first!',
            'cuisine': 'Georgian',
            'image': 'https://images.unsplash.com/photo-1551782450-17144efb5723?w=400&h=300&fit=crop'
        }
    ],
    'საჭმელი': [  # General Georgian food
        {
            'name': 'ჩურჩხელა (Churchkhela)',
            'ingredients': ['Grape juice', 'Walnuts', 'Flour', 'Sugar'],
            'instructions': 'String walnuts on thread, dip in thickened grape juice mixed with flour. Dry for several days.',
            'cuisine': 'Georgian',
            'image': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop'
        },
        {
            'name': 'ბადრიჯანი (Badrijan) - Eggplant Rolls',
            'ingredients': ['4 eggplants', '200g walnuts', '3 cloves garlic', CORIANDER_FRESH, 'Sunflower oil', 'Salt'],
            'instructions': 'Grill eggplants, roll with walnut-garlic paste, serve cold.',
            'cuisine': 'Georgian',
            'image': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400&h=300&fit=crop'
        },
        {
            'name': 'ლობიო (Lobio) - Bean Stew',
            'ingredients': ['500g red beans', ONIONS_2, '3 cloves garlic', CORIANDER_FRESH, 'Sunflower oil', 'Adjika (Georgian spice)', 'Salt'],
            'instructions': 'Soak beans overnight, cook with onions, garlic, spices. Mash slightly and serve hot.',
            'cuisine': 'Georgian',
            'image': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&h=300&fit=crop'
        }
    ],
    'ქართული': [  # Georgian cuisine
        {
            'name': 'ოჯახური ხარჩო (Ojakhuri Kharcho) - Beef Soup',
            'ingredients': ['500g beef', ONIONS_2, '3 potatoes', '2 tbsp tkemali (plum sauce)', CORIANDER_FRESH, 'Black pepper', 'Bay leaves'],
            'instructions': 'Cook beef, add onions, potatoes, spices. Simmer for 1.5 hours. Serve with fresh bread.',
            'cuisine': 'Georgian',
            'image': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400&h=300&fit=crop'
        }
    ]
}

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
    Search for recipes based on query with intelligent matching.
    """
    query_lower = query.lower()

    # Check for Georgian keywords first
    georgian_keywords = ['ხაჭაპური', 'ხინკალი', 'საჭმელი', 'ქართული', 'იმერული', 'georgian', 'georgia']
    if any(keyword in query_lower for keyword in georgian_keywords):
        results = _search_georgian_recipes(georgian_keywords)
    else:
        results = _search_intelligent(query_lower)

    return _format_recipe_response(results, query)

def _search_georgian_recipes(georgian_keywords):
    """Search for Georgian recipes."""
    results = []
    for key in recipes_db:
        if key in georgian_keywords or key in ['ხაჭაპური', 'ხინკალი', 'საჭმელი', 'ქართული']:
            results.extend(recipes_db[key])
    return results

def _search_intelligent(query_lower):
    """Intelligent search that understands various query types."""
    results = []

    # Direct category matches
    for category, recipes in recipes_db.items():
        if category in query_lower:
            results.extend(recipes)

    # Cuisine-based search
    cuisine_matches = _search_by_cuisine(query_lower)
    results.extend(cuisine_matches)

    # Ingredient-based search
    ingredient_matches = _search_by_ingredients(query_lower)
    results.extend(ingredient_matches)

    # Broad category search (meat, vegetarian, etc.)
    broad_matches = _search_broad_categories(query_lower)
    results.extend(broad_matches)

    # Remove duplicates while preserving order
    seen = set()
    unique_results = []
    for recipe in results:
        recipe_id = recipe['name']
        if recipe_id not in seen:
            seen.add(recipe_id)
            unique_results.append(recipe)

    return unique_results

def _search_by_cuisine(query_lower):
    """Search recipes by cuisine type."""
    results = []
    cuisine_map = {
        'american': 'American',
        'asian': 'Asian',
        'italian': 'Italian',
        'georgian': 'Georgian',
        'usa': 'American',
        'chinese': 'Asian',
        'japanese': 'Asian',
        'korean': 'Asian',
        'thai': 'Asian',
        'indian': 'Asian'
    }

    for cuisine_keyword, cuisine_name in cuisine_map.items():
        if cuisine_keyword in query_lower:
            for category, recipes in recipes_db.items():
                for recipe in recipes:
                    if recipe.get('cuisine', '').lower() == cuisine_name.lower():
                        results.append(recipe)

    return results

def _search_by_ingredients(query_lower):
    """Search recipes that contain specific ingredients."""
    results = []
    ingredient_keywords = {
        'chicken': ['chicken'],
        'beef': ['beef'],
        'pork': ['pork'],
        'fish': ['fish', 'salmon', 'tuna'],
        'pasta': ['pasta', 'spaghetti', 'penne'],
        'rice': ['rice'],
        'cheese': ['cheese', 'parmesan', 'mozzarella'],
        'tomato': ['tomato'],
        'onion': ['onion'],
        'garlic': ['garlic'],
        'egg': ['egg'],
        'milk': ['milk'],
        'butter': ['butter'],
        'flour': ['flour'],
        'bread': ['bread']
    }

    for ingredient_keyword, ingredient_list in ingredient_keywords.items():
        if ingredient_keyword in query_lower:
            for category, recipes in recipes_db.items():
                for recipe in recipes:
                    recipe_ingredients = ' '.join(recipe['ingredients']).lower()
                    if any(ing in recipe_ingredients for ing in ingredient_list):
                        results.append(recipe)

    return results

def _search_broad_categories(query_lower):
    """Search by broad categories like meat, vegetarian, etc."""
    results = []

    # Meat dishes
    if any(word in query_lower for word in ['meat', 'protein', 'chicken', 'beef', 'pork', 'lamb']):
        meat_ingredients = ['chicken', 'beef', 'pork', 'lamb', 'meat']
        for category, recipes in recipes_db.items():
            for recipe in recipes:
                recipe_text = ' '.join(recipe['ingredients'] + [recipe['name']]).lower()
                if any(ing in recipe_text for ing in meat_ingredients):
                    results.append(recipe)

    # Vegetarian dishes
    if any(word in query_lower for word in ['vegetarian', 'veggie', 'plant-based']):
        for category, recipes in recipes_db.items():
            for recipe in recipes:
                recipe_text = ' '.join(recipe['ingredients']).lower()
                meat_ingredients = ['chicken', 'beef', 'pork', 'lamb', 'fish', 'bacon', 'pancetta']
                if not any(meat in recipe_text for meat in meat_ingredients):
                    results.append(recipe)

    # Dairy-free dishes
    if any(word in query_lower for word in ['dairy-free', 'dairy free']):
        for category, recipes in recipes_db.items():
            for recipe in recipes:
                recipe_text = ' '.join(recipe['ingredients']).lower()
                dairy_ingredients = ['cheese', 'milk', 'butter', 'cream', 'yogurt']
                if not any(dairy in recipe_text for dairy in dairy_ingredients):
                    results.append(recipe)

    return results

def _format_recipe_response(results, query):
    """Format the recipe search response."""
    if results:
        response = f"Found {len(results)} recipe(s) for '{query}':\n\n"
        for i, recipe in enumerate(results, 1):
            emoji = recipe.get('image', '🍽️')
            response += f"{emoji} **Recipe {i}: {recipe['name']}** ({recipe['cuisine']})\n"
            response += "**Ingredients:**\n" + "\n".join(f"• {ing}" for ing in recipe['ingredients']) + "\n"
            response += f"**Instructions:** {recipe['instructions']}\n\n"
        return response
    else:
        return f"No recipes found for '{query}'. Try searching for:\n• Chicken, pasta, or cheese dishes\n• Italian, Asian, or Georgian cuisine\n• Vegetarian or meat-based recipes\n• Specific ingredients like 'garlic' or 'tomato'\n• Or ask me directly about cooking tips!"

# Initialize the agent (global for Streamlit)
@st.cache_resource
def get_agent():
    try:
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
            instructions="""You are a helpful cooking AI assistant with extensive recipe knowledge. Your main capabilities are:

RECIPE SEARCH: Use the search_recipes tool for various types of queries:
- By ingredients: "chicken recipes", "cheese dishes", "pasta recipes"
- By cuisine: "italian cuisine", "asian food", "georgian food"
- By dietary preferences: "vegetarian recipes", "meat dishes", "dairy-free"
- By specific dishes: "khachapuri", "khinkali", "carbonara"
- By cooking method: "grilled", "stir-fry", "baked"

INGREDIENT EXTRACTION: When users provide recipe text, use extract_ingredients to parse out the ingredients list.

Be intelligent about search queries:
- "Chicken" → find all chicken-based recipes
- "Italian" → find Italian cuisine recipes
- "Vegetarian" → find meat-free recipes
- "Cheese" → find recipes containing cheese
- "Georgian" → find traditional Georgian dishes

Always respond helpfully with cooking tips, recipe suggestions, and encouragement. Use emojis to make responses engaging!""",
            tools=[extract_ingredients, search_recipes],
        )
        return agent
    except Exception as e:
        st.error(f"Failed to initialize AI agent: {e}")
        st.stop()

def setup_page_config():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="🍳 Cooking AI Agent",
        page_icon="🍳",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def setup_sidebar(agent):
    """Set up the sidebar with quick recipe options and controls."""
    with st.sidebar:
        st.header("🎯 Quick Recipe Ideas")
        st.write("Try these searches:")

        # Quick search buttons with broader terms
        quick_searches = {
            "🍗 Chicken Dishes": "chicken recipes",
            "🍝 Pasta Dishes": "pasta recipes",
            "🇬🇪 Georgian Food": "georgian cuisine",
            "🧀 Khachapuri": "khachapuri",
            "🥟 Khinkali": "khinkali",
            "🥩 Meat Dishes": "meat dishes",
            "🥕 Vegetarian": "vegetarian recipes",
            "🧀 Cheese Dishes": "cheese recipes",
            "🍅 Italian Food": "italian cuisine",
            "🥢 Asian Food": "asian cuisine"
        }

        for button_text, search_query in quick_searches.items():
            if st.button(button_text):
                st.session_state.quick_query = search_query

        st.divider()
        st.write("💡 **Tips:**")
        st.write("- Ask for ingredient extraction")
        st.write("- Search by cuisine type")
        st.write("- Try 'vegetarian' or 'meat dishes'")
        st.write("- Search by ingredients like 'chicken' or 'cheese'")

        # Clear chat history
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.thread = agent.get_new_thread()
            st.rerun()

def initialize_session_state(agent):
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'thread' not in st.session_state:
        st.session_state.thread = agent.get_new_thread()

def display_chat_history():
    """Display the chat message history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def get_user_input():
    """Get user input from text field and send button."""
    # Handle quick queries from sidebar
    if 'quick_query' in st.session_state and st.session_state.quick_query:
        initial_value = st.session_state.quick_query
        st.session_state.quick_query = None  # Reset after use
        input_key = f"user_input_{len(st.session_state.messages)}"  # Unique key to clear
    else:
        initial_value = ""
        input_key = "user_input"

    # Chat input with text input and button
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input(
            "Type your cooking question:",
            value=initial_value,
            key=input_key,
            placeholder="Ask about recipes, ingredients, or cooking tips..."
        )
    with col2:
        send_button = st.button("Send 📤", use_container_width=True)

    return user_input, send_button

def process_user_message(user_input, agent):
    """Process user input and generate AI response."""
    prompt = user_input.strip()

    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("👨‍🍳 Cooking up an answer..."):
            try:
                result = asyncio.run(agent.run(prompt, thread=st.session_state.thread))
                response = result.text
                st.markdown(response)

                # Check if response contains recipes and display images
                if "Found" in response and "recipe" in response.lower():
                    display_recipe_gallery(response)

                # Add assistant message to history
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"😞 An error occurred: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

def display_recipe_gallery(response):
    """Display recipe gallery with images when recipes are found."""
    st.markdown("---")
    st.subheader("📸 Recipe Gallery")

    # Extract recipe names from response (simple parsing)
    recipe_names = []
    for line in response.split('\n'):
        if '**Recipe' in line and ':' in line:
            name = line.split(':')[1].split('**')[0].strip()
            recipe_names.append(name)

    # Display recipe cards with images
    if recipe_names:
        cols = st.columns(min(len(recipe_names), 3))
        for i, name in enumerate(recipe_names):
            with cols[i % 3]:
                # Find the recipe data
                for category, recipes in recipes_db.items():
                    for recipe in recipes:
                        if recipe['name'] in name or name in recipe['name']:
                            if 'image' in recipe and recipe['image'].startswith('http'):
                                st.image(recipe['image'], caption=recipe['name'], use_column_width=True)
                                break
                            break
                    else:
                        continue
                    break

def main():
    setup_page_config()

    st.title("🍳 Cooking AI Agent")
    st.write("Chat with me about recipes, ingredients, or cooking tips!")

    # Initialize agent first
    agent = get_agent()

    setup_sidebar(agent)
    initialize_session_state(agent)

    # Chat interface
    st.subheader("💬 Chat with the Cooking Assistant")

    display_chat_history()

    # Get user input
    user_input, send_button = get_user_input()

    # Process input
    if send_button and user_input.strip():
        process_user_message(user_input, agent)

if __name__ == "__main__":
    main()