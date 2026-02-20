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
            'ingredients': ['500g flour', '300g sulguni cheese', '200ml milk', '50g butter', '1 egg', '1 tsp sugar', 'Salt to taste'],
            'instructions': 'Mix dough with flour, milk, egg, sugar, salt. Roll out, add cheese filling, fold and bake at 200°C for 20 minutes.',
            'cuisine': 'Georgian',
            'image': 'https://images.unsplash.com/photo-1579954115545-a95591f28bfc?w=400&h=300&fit=crop'
        },
        {
            'name': 'მეგრული ხაჭაპური (Megruli Khachapuri)',
            'ingredients': ['500g flour', '400g sulguni cheese', '100g butter', '1 egg', '200ml milk', 'Salt to taste'],
            'instructions': 'Make dough, fill with cheese, fold into boat shape, add butter on top. Bake at 220°C for 15-20 minutes.',
            'cuisine': 'Georgian',
            'image': 'https://images.unsplash.com/photo-1579954115566-e66808b81b2e?w=400&h=300&fit=crop'
        }
    ],
    'ხინკალი': [  # Georgian dumplings
        {
            'name': 'ხინკალი (Khinkali)',
            'ingredients': ['500g ground meat (pork/beef mix)', '2 onions', '500g flour', '200ml water', 'Salt, pepper, coriander'],
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
            'ingredients': ['4 eggplants', '200g walnuts', '3 cloves garlic', 'Fresh coriander', 'Sunflower oil', 'Salt'],
            'instructions': 'Grill eggplants, roll with walnut-garlic paste, serve cold.',
            'cuisine': 'Georgian',
            'image': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400&h=300&fit=crop'
        },
        {
            'name': 'ლობიო (Lobio) - Bean Stew',
            'ingredients': ['500g red beans', '2 onions', '3 cloves garlic', 'Fresh coriander', 'Sunflower oil', 'Adjika (Georgian spice)', 'Salt'],
            'instructions': 'Soak beans overnight, cook with onions, garlic, spices. Mash slightly and serve hot.',
            'cuisine': 'Georgian',
            'image': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&h=300&fit=crop'
        }
    ],
    'ქართული': [  # Georgian cuisine
        {
            'name': 'ოჯახური ხარჩო (Ojakhuri Kharcho) - Beef Soup',
            'ingredients': ['500g beef', '2 onions', '3 potatoes', '2 tbsp tkemali (plum sauce)', 'Fresh coriander', 'Black pepper', 'Bay leaves'],
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
    Search for recipes based on query.
    """
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
                'cuisine': 'Georgian',
                'image': 'https://images.unsplash.com/photo-1579954115545-a95591f28bfc?w=400&h=300&fit=crop'
            },
            {
                'name': 'მეგრული ხაჭაპური (Megruli Khachapuri)',
                'ingredients': ['500g flour', '400g sulguni cheese', '100g butter', '1 egg', '200ml milk', 'Salt to taste'],
                'instructions': 'Make dough, fill with cheese, fold into boat shape, add butter on top. Bake at 220°C for 15-20 minutes.',
                'cuisine': 'Georgian',
                'image': 'https://images.unsplash.com/photo-1579954115566-e66808b81b2e?w=400&h=300&fit=crop'
            }
        ],
        'ხინკალი': [  # Georgian dumplings
            {
                'name': 'ხინკალი (Khinkali)',
                'ingredients': ['500g ground meat (pork/beef mix)', '2 onions', '500g flour', '200ml water', 'Salt, pepper, coriander'],
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
                'ingredients': ['4 eggplants', '200g walnuts', '3 cloves garlic', 'Fresh coriander', 'Sunflower oil', 'Salt'],
                'instructions': 'Grill eggplants, roll with walnut-garlic paste, serve cold.',
                'cuisine': 'Georgian',
                'image': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400&h=300&fit=crop'
            },
            {
                'name': 'ლობიო (Lobio) - Bean Stew',
                'ingredients': ['500g red beans', '2 onions', '3 cloves garlic', 'Fresh coriander', 'Sunflower oil', 'Adjika (Georgian spice)', 'Salt'],
                'instructions': 'Soak beans overnight, cook with onions, garlic, spices. Mash slightly and serve hot.',
                'cuisine': 'Georgian',
                'image': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&h=300&fit=crop'
            }
        ],
        'ქართული': [  # Georgian cuisine
            {
                'name': 'ოჯახური ხარჩო (Ojakhuri Kharcho) - Beef Soup',
                'ingredients': ['500g beef', '2 onions', '3 potatoes', '2 tbsp tkemali (plum sauce)', 'Fresh coriander', 'Black pepper', 'Bay leaves'],
                'instructions': 'Cook beef, add onions, potatoes, spices. Simmer for 1.5 hours. Serve with fresh bread.',
                'cuisine': 'Georgian',
                'image': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400&h=300&fit=crop'
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
            emoji = recipe.get('image', '🍽️')
            response += f"{emoji} **Recipe {i}: {recipe['name']}** ({recipe['cuisine']})\n"
            response += "**Ingredients:**\n" + "\n".join(f"• {ing}" for ing in recipe['ingredients']) + "\n"
            response += f"**Instructions:** {recipe['instructions']}\n\n"
        return response
    else:
        return f"No recipes found for '{query}'. Try searching for chicken, pasta, or Georgian dishes like 'ხაჭაპური', 'ხინკალი', 'საჭმელი', or 'ქართული'."

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
            instructions="""You are a helpful cooking AI assistant. Your main capabilities are:
- Searching for recipes based on ingredients, cuisine type, or keywords
- Extracting ingredients from recipe texts
- Providing cooking advice and tips
- Suggesting recipe modifications

When users ask to search for recipes, use the search_recipes tool.
When users provide recipe text and ask to extract ingredients, use the extract_ingredients tool.
For general cooking questions, answer directly using your knowledge.
Be friendly, informative, and encouraging.

Always respond in a helpful and engaging way, using emojis where appropriate.""",
            tools=[extract_ingredients, search_recipes],
        )
        return agent
    except Exception as e:
        st.error(f"Failed to initialize AI agent: {e}")
        st.stop()

def main():
    st.set_page_config(
        page_title="🍳 Cooking AI Agent",
        page_icon="🍳",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🍳 Cooking AI Agent")
    st.write("Chat with me about recipes, ingredients, or cooking tips!")

    # Initialize agent first
    agent = get_agent()

    # Sidebar with quick options
    with st.sidebar:
        st.header("🎯 Quick Recipe Ideas")
        st.write("Try these searches:")

        if st.button("🍗 Chicken Recipes"):
            st.session_state.quick_query = "chicken"
        if st.button("🍝 Pasta Recipes"):
            st.session_state.quick_query = "pasta"
        if st.button("🇬🇪 Georgian Food"):
            st.session_state.quick_query = "საჭმელი"
        if st.button("🧀 Khachapuri"):
            st.session_state.quick_query = "ხაჭაპური"
        if st.button("🥟 Khinkali"):
            st.session_state.quick_query = "ხინკალი"

        st.divider()
        st.write("💡 **Tips:**")
        st.write("- Ask for ingredient extraction")
        st.write("- Search by cuisine type")
        st.write("- Get cooking advice")

        # Clear chat history
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.thread = agent.get_new_thread()
            st.rerun()

    # Session state for conversation
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'thread' not in st.session_state:
        st.session_state.thread = agent.get_new_thread()

    # Chat interface
    st.subheader("💬 Chat with the Cooking Assistant")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

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

    # Process input
    if send_button and user_input.strip():
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

                    # Add assistant message to history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"😞 An error occurred: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()