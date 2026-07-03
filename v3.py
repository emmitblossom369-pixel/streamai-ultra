import streamlit as str_web
from openai import OpenAI
import json
import os

# 1. Page configuration & setup
str_web.set_page_config(page_title="StreamAI Ultra", page_icon="⚡", layout="wide")

# Unique CSS: Sleek modern design tweaks for better scannability
str_web.markdown(
    """
    <style>
    [data-testid="stchatmessagecontainer"] { overflow-anchor: none !important; }
    html { scroll-behavior: auto !important; }
    .stDeployButton { display:none; } 
    </style>
    """,
    unsafe_allow_html=True
)

# 2. Secure connection setup - Update with your active Groq API Key
GROQ_API_KEY = "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"

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",  # Official OpenAI-compatible Groq URL
    api_key=GROQ_API_KEY
)

# 3. Active 2026 Engine Lookup
def get_live_groq_models():
    return [
        "openai/gpt-oss-20b",
        "qwen/qwen3-32b",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-safeguard-20b"
    ]

available_models = get_live_groq_models()

# INVISIBLE BACKGROUND STORAGE ENGINE: Saves chat rooms invisibly without login blockers
STORAGE_FILE = "user_storage.json"

def load_storage():
    if not os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "w") as f:
            json.dump({"Chat 1": []}, f)
    with open(STORAGE_FILE, "r") as f:
        return json.load(f)

def save_all_chats(chats):
    with open(STORAGE_FILE, "w") as f:
        json.dump(chats, f, indent=4)

# =====================================================================
# 4. Session memory initialize (LOADED DYNAMICALLY FROM PERSISTENT DATABASE)
# =====================================================================
user_db = load_storage()

if "all_chats" not in str_web.session_state:
    str_web.session_state.all_chats = user_db

# Strips the list layout to fetch a direct text string name to prevent crashes
if "active_chat_tab" not in str_web.session_state:
    first_room = list(str_web.session_state.all_chats.keys())[0]
    str_web.session_state.active_chat_tab = first_room

# Detailed guidelines (Google AI style)
GOOGLE_AI_STYLE = (
    " FORMATTING RULE: You must provide highly detailed, comprehensive, and thorough explanations. "
    "Break down complex ideas into simple, universally accessible language. Always structure your "
    "responses cleanly for quick reading by using bold terms, numbered lists for steps, and punchy "
    "bullet points for key details. Avoid large blocks of dense text."
)

# Your mandatory creator rule
CREATOR_GUARDRAIL = (
    " IMPORTANT RULE: If the user asks who created, built, or made StreamAI, you must state exactly "
    "that it was made by a 13-year-old boy who lives in the USA, who started this as a project to be "
    "used for other projects."
)

AI_BEHAVIOR = GOOGLE_AI_STYLE + CREATOR_GUARDRAIL

PERSONAS = {
    "🧠 General Assistant": "You are a helpful, direct, and elite AI assistant." + AI_BEHAVIOR,
    "💻 Senior Code Mentor": "You are an expert software engineer. Review code ruthlessly, prioritize efficiency, and provide clean refactors." + AI_BEHAVIOR,
    "✍️ Creative Storyteller": "You are a master novelist. Respond with vivid imagery, rich metaphors, and gripping narrative styles." + AI_BEHAVIOR,
    "📊 Data Scientist": "You are a meticulous statistician. Explain concepts mathematically and break down algorithms step-by-step." + AI_BEHAVIOR
}


# =====================================================================
# 5. Sidebar hub management (PLACE THIS DIRECTLY BELOW SECTION 4)
# =====================================================================
with str_web.sidebar:
    str_web.title("⚡ StreamAI Hub")
    
    str_web.caption("⚙️ SYSTEM METRICS")
    live_model_id = str_web.selectbox("Active Engine", available_models)
    str_web.success(f"Total Rooms: {len(str_web.session_state.all_chats)}")
    
    str_web.divider()

    # DYNAMIC UI STYLE SLIDERS
    str_web.caption("🎨 UI STYLE CUSTOMIZER")
    ui_height = str_web.slider("Chat Window Vertical Height", min_value=300, max_value=800, value=520, step=50)
    ui_border = str_web.checkbox("Enable Workspace Border Frame", value=False)
    
    str_web.divider()
    
    # Unique Feature 1: Persona Engine Selection
    str_web.caption("🤖 SELECT AI AGENT PERSONA")
    chosen_persona = str_web.selectbox("Active Persona", list(PERSONAS.keys()), label_visibility="collapsed")
    system_instruction = PERSONAS[chosen_persona]
    
    str_web.divider()
    
    # Unique Feature 2: Multi-Room Navigation Grid
    str_web.caption("💬 ACTIVE CHAT ROOMS")
    for room_name in list(str_web.session_state.all_chats.keys()):
        is_active = (room_name == str_web.session_state.active_chat_tab)
        type_style = "primary" if is_active else "secondary"
        
        if str_web.button(f"▪️ {room_name}", key=f"nav_{room_name}", type=type_style, use_container_width=True):
            str_web.session_state.active_chat_tab = room_name
            str_web.rerun()

    str_web.divider()
    
    if str_web.button("➕ Start New Chat Room", type="primary", use_container_width=True):
        new_chat_num = len(str_web.session_state.all_chats) + 1
        new_chat_name = f"Chat {new_chat_num}"
        str_web.session_state.all_chats[new_chat_name] = []
        str_web.session_state.active_chat_tab = new_chat_name
        save_all_chats(str_web.session_state.all_chats)  # Auto-save layout mapping
        str_web.rerun()

# 6. Main App Window UI
current_room = str_web.session_state.active_chat_tab

# Fallback validation check
if current_room not in str_web.session_state.all_chats:
    current_room = list(str_web.session_state.all_chats.keys())[0]
    str_web.session_state.active_chat_tab = current_room

str_web.subheader(f"Workspace: {current_room}")
str_web.caption(f"Currently fueled by **{chosen_persona}** using the updated Groq network.")

# Dynamic Viewport Box Container (Linked to your style sliders)
chat_viewport = str_web.container(height=ui_height, border=ui_border)

# Render existing messages for this unique room inside the locked container
with chat_viewport:
    for msg in str_web.session_state.all_chats[current_room]:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            with str_web.chat_message(msg["role"]):
                str_web.write(msg["content"])

# 7. Live processing & response stream
if user_input := str_web.chat_input("Ask anything..."):
    with chat_viewport:
        with str_web.chat_message("user"):
            str_web.write(user_input)
    
    str_web.session_state.all_chats[current_room].append({"role": "user", "content": user_input})
    
    # ADDED FEATURE: Smart Automated Room Renaming 
    # Automatically triggers if this entry is the very first query to name the generic layout button
    if len(str_web.session_state.all_chats[current_room]) == 1 and current_room.startswith("Chat "):
        clean_summary = user_input.strip()[:18]
        if len(user_input) > 18:
            clean_summary += "..."
        new_room_name = f"💬 {clean_summary}"
        
        str_web.session_state.all_chats[new_room_name] = str_web.session_state.all_chats.pop(current_room)
        str_web.session_state.active_chat_tab = new_room_name
        current_room = new_room_name

    save_all_chats(str_web.session_state.all_chats)  # Auto-save user entry
    
    # Pack your system rules and conversation history together
    full_prompt = f"System Instruction: {system_instruction}\n\n"
    for msg in str_web.session_state.all_chats[current_room]:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            prefix = "User: " if msg["role"] == "user" else "Assistant: "
            full_prompt += f"{prefix}{msg['content']}\n"
        
    with chat_viewport:
        with str_web.chat_message("assistant"):
            response_placeholder = str_web.empty()
            response_placeholder.markdown("*Thinking...*")
            
            try:
                # Contact the Groq Server using your working endpoint logic
                response = client.responses.create(
                    model=str(live_model_id),
                    input=str(full_prompt)
                )
                
                # Safe list validation parsing check
                if isinstance(response, list) and len(response) > 0:
                    # Extracts content safely out of the list container index
                    item = response[0]
                    if hasattr(item, "output_text"):
                        full_ai_response = item.output_text
                    elif isinstance(item, dict):
                        full_ai_response = item.get("output_text", str(item))
                    else:
                        full_ai_response = str(item)
                elif hasattr(response, 'output_text') and response.output_text:
                    full_ai_response = response.output_text
                else:
                    full_ai_response = str(response)
                
                response_placeholder.markdown(full_ai_response)
                str_web.session_state.all_chats[current_room].append({"role": "assistant", "content": full_ai_response})
                save_all_chats(str_web.session_state.all_chats)
                str_web.rerun()
                
            except Exception as err:
                str_web.error(f"Network processing hitch: {err}")
