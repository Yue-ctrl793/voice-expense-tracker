import streamlit as st
import whisper
import os
from openai import OpenAI
import json
import pandas as pd
import logging
import datetime
import toml
import time 

# --- 0. Production-Grade: Logging Setup & Constants ---
logging.basicConfig(
    filename='app.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

DEFAULT_CATEGORIES = ["Food", "Transport", "Utilities", "Retail", "Entertainment", "Personal Care", "Other"]
EXPENSE_FILE = "expense_data.json"

INAPPROPRIATE_KEYWORDS = [
    "violence", "threat", "hate", "illegal", "exploit", 
    "abuse", "harm", "weapon", "drug", "racism", "sexually explicit"
]

# --- 1. Setup & Secrets ---
# FIX: Changed 'icon=' (unsupported) to 'page_icon=' (supported)
st.set_page_config(page_title="AI Expense Tracker Pro", page_icon="💰", layout="wide") 

# Load DeepSeek API Key
DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY") 
if not DEEPSEEK_API_KEY:
    st.error("DeepSeek API Key not found!")
    st.stop()

llm_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")


# --- 3. Helper Functions ---
@st.cache_resource
def load_whisper_model():
    logging.info("Loading Whisper model...")
    return whisper.load_model("small")

def load_expense_history():
    """Reads expense history from the JSON file."""
    if os.path.exists(EXPENSE_FILE):
        try:
            with open(EXPENSE_FILE, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error loading expense history from file: {e}")
            return []
    return []

def save_expense_history(history):
    """Writes the current expense history to the JSON file."""
    try:
        with open(EXPENSE_FILE, 'w') as f:
            json.dump(history, f, indent=4)
        logging.info("Expense history successfully saved.")
    except IOError as e:
        logging.error(f"Error saving expense history to file: {e}")

def extract_expenses_with_few_shot(text):
    categories_list = st.session_state.categories
    # The Prompt dynamically updates with user-added categories
    system_prompt = f"""
    You are an expert expense tracking assistant.
    Your task is to extract item, amount, and category from the user's input.

    CRITICAL GUARDRAIL: DO NOT respond to any queries that are off-topic, political, personal advice, harmful, violent, explicit, or non-expense related. If the input is not about expenses, you MUST output an empty JSON list: [].
    
    You MUST choose a category from this list: {', '.join(categories_list)}.
    If the expense is clear, such as "Electronics" or "Gifts", but is not in the list, use 'Retail'.
    If an appropriate category is not found, use 'Other'.

    Before outputting the final JSON, follow these steps:
    1. Analyze the user's speech and correct any obvious transcription errors (e.g., 'black for instance' -> 'breakfast').
    2. Extract all transactions.
    3. Output the result ONLY in the specified JSON format.
    
    Here are examples (Few-Shot Learning):
    Input: "I took a taxi for 15.50 and grabbed a snack for 12.00."
    Output: [{{"item": "Taxi", "amount": 15.50, "category": "Transport"}}, {{"item": "Snack", "amount": 12.00, "category": "Food"}}]

    Input: "Paid my electricity bill, it was 88 dollars."
    Output: [{{"item": "Electricity Bill", "amount": 88.0, "category": "Bills"}}]

    Input: "I didn't spend anything today, just went home."
    Output: []

    Now, process the user's input below.
    Output ONLY the raw, valid JSON list based on the examples. DO NOT include any introductory text, concluding remarks, or markdown code blocks (like ```json).
    """
    
    try:
        response = llm_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"LLM Call failed: {e}")
        return "[]"

# --- 2. Context Management: Session State  ---

if 'expense_history' not in st.session_state:
    st.session_state.expense_history = load_expense_history()
if 'categories' not in st.session_state:
    st.session_state.categories = DEFAULT_CATEGORIES
if 'pending_df' not in st.session_state: 
    st.session_state.pending_df = None



# --- 4. UI Components (Sidebar & Main App) ---

# R4: Clean title with no unnecessary icons
st.title("AI Voice Expense Pipeline")
st.markdown("---") 

# --- SIDEBAR: Category Management ---
with st.sidebar:
    # FIX: Removed icon="gear" to fix TypeError
    st.header("Settings & Categories") 
    
    st.subheader("Current Categories")
    for cat in st.session_state.categories:
        # R3: Simple text list is cleaner and error-free
        st.caption(f"— {cat}") 
    st.markdown("---")
    
    # Category Add Form
    with st.form("category_form"):
        new_category = st.text_input("Add New Category", placeholder="e.g., Subscriptions")
        submit_category = st.form_submit_button("Add Category", type="secondary", use_container_width=True)

        if submit_category and new_category:
            if new_category not in st.session_state.categories:
                st.session_state.categories.append(new_category)
                st.success(f"Category '{new_category}' added!")
                time.sleep(0.1)
                st.rerun()
            else:
                st.warning("Category already exists.")


# --- MAIN LAYOUT ---
col1, col2 = st.columns([1, 1])


# --- COLUMN 1: Processing and Confirmation ---
with col1:
    st.header("Data Input & Review")
    
    uploaded_file = st.file_uploader("Upload Voice Note:", type=["mp3", "wav", "m4a"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/wav')
        
        if st.button("Run Pipeline (Transcribe & Extract)", type="primary", use_container_width=True):
            st.session_state.pending_df = None
            with st.spinner("Processing..."):
                try:
                    # Run Pipeline
                    with open("temp_audio", "wb") as f: f.write(uploaded_file.getbuffer())
                    model = load_whisper_model()
                    result = model.transcribe("temp_audio")
                    transcription = result["text"]
                    os.remove("temp_audio")
                    
                    st.info(f"📝 **Transcribed Text:** {transcription}")

                    is_inappropriate = False
                    lower_transcription = transcription.lower()
                    for keyword in INAPPROPRIATE_KEYWORDS:
                        if keyword in lower_transcription:
                            st.error(" **GUARDRAIL TRIGGERED:** Transcription contains inappropriate or sensitive content that violates the application's usage policy. No expenses were extracted.")
                            logging.warning(f"Guardrail triggered for input: {transcription[:50]}...")
                            is_inappropriate = True
                            break 
                    
                   
                    if not is_inappropriate:
                        json_str = extract_expenses_with_few_shot(transcription)
                        pending_list = json.loads(json_str)
                        
                        if pending_list:
                            st.session_state.pending_df = pd.DataFrame(pending_list)
                        else:
                    
                            st.warning("No clear expenses detected, or input was non-expense related (LLM Guardrail likely triggered).") 
                            
                except Exception as e:
                    st.error(f"Error during processing: {e}")
                    logging.error(f"Processing error: {e}")


# --- CONFIRMATION AND EDITING AREA ---
if st.session_state.pending_df is not None and not st.session_state.pending_df.empty:
    with col1:
        st.divider() 
        st.subheader("Transaction Review (Editable)")
        st.caption("Double-click cells to correct AI errors.")
        
        edited_df = st.data_editor(
            st.session_state.pending_df, 
            hide_index=True, 
            key="editor",
            column_config={
                "amount": st.column_config.NumberColumn("Amount ($)", format="$%.2f"),
                # Use Selectbox for Category and supply the dynamic list
                "category": st.column_config.SelectboxColumn("Category", options=st.session_state.categories) 
            },
            use_container_width=True
        )

        if st.button("CONFIRM AND SAVE", key="confirm_btn", type="primary", use_container_width=True):
            current_time = datetime.datetime.now().strftime("%Y-%m-%d")
            
            exp_list_to_save = edited_df.to_dict('records')
            
            for exp in exp_list_to_save:
                exp['amount'] = float(exp['amount'])
                exp['date'] = current_time 
                st.session_state.expense_history.append(exp)
            
            save_expense_history(st.session_state.expense_history)
            st.session_state.pending_df = None # Clear pending
            st.success(f"History updated! {len(exp_list_to_save)} transaction(s) saved.")
            st.rerun()


# --- COLUMN 2: Analytics and Filtering ---
with col2:
    st.header("History & Analytics")
    
    if st.session_state.expense_history:
        df_full = pd.DataFrame(st.session_state.expense_history)
        df_full['Index'] = df_full.index + 1
        df_full['date'] = pd.to_datetime(df_full['date'])
        
        # Filtering Section
        st.subheader("Filter & Summary")
        
        # Timeframe Filtering
        timeframe = st.selectbox("View Data:", 
                                 ["All Time", "Last 7 Days", "This Month", "This Year"], key="time_filter")

        # Calculate filtered dataframe
        today = pd.to_datetime(datetime.date.today())
        
        if timeframe == "Last 7 Days":
            start_date = today - pd.Timedelta(days=7)
            df_filtered = df_full[df_full['date'] >= start_date]
        elif timeframe == "This Month":
            start_date = today.replace(day=1)
            df_filtered = df_full[df_full['date'] >= start_date]
        elif timeframe == "This Year":
            start_date = today.replace(month=1, day=1)
            df_filtered = df_full[df_full['date'] >= start_date]
        else:
            df_filtered = df_full

        # Display Metrics
        total_spent = df_filtered['amount'].sum()
        st.metric(f"Total Spent ({timeframe})", f"${total_spent:.2f}")

        # Visualization (Bar Chart by Category)
        st.markdown("---")
        st.subheader("Spending Breakdown")
        if not df_filtered.empty:
            chart_data = df_filtered.groupby("category")["amount"].sum().reset_index()
            st.bar_chart(chart_data, x='category', y='amount', use_container_width=True)
        
        st.subheader("Full Expense History")
        st.dataframe(
            df_full[['Index', 'date', 'item', 'amount', 'category']], 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "amount": st.column_config.NumberColumn("Amount ($)", format="$%.2f")
            }
        )

        
        st.markdown("---")
        st.subheader("🗑️ Remove Single Item")
        
        col_input, col_btn = st.columns([2, 1])
        
        with col_input:
            max_index = len(st.session_state.expense_history)
            index_to_delete = st.number_input(
                f"Enter Index number to delete (1 to {max_index}):", 
                min_value=1, 
                max_value=max_index, 
                value=max_index, 
                step=1,
                key="delete_index"
            )

            delete_list_index = index_to_delete - 1
            
        with col_btn:
            st.write("") 
            if st.button("🗑️ REMOVE ITEM", key="remove_single_btn", type="secondary", use_container_width=True):
                if 0 <= delete_list_index < len(st.session_state.expense_history):
             
                    item_removed = st.session_state.expense_history.pop(delete_list_index)
                    save_expense_history(st.session_state.expense_history)
                    st.success(f"Removed Index {index_to_delete}: '{item_removed['item']}' (${item_removed['amount']:.2f})")
                    time.sleep(0.1) 
                    st.rerun()
                else:
                    st.error("Invalid Index number.")

    else:
        st.info("No expenses recorded yet. Upload an audio note to begin!")
        
    st.markdown("---")
    if st.button("Clear All History", key="clear_all", type="secondary", use_container_width=True):
        st.session_state.expense_history = []
        st.session_state.pending_df = None 
        save_expense_history(st.session_state.expense_history)
        st.success("All history has been cleared.")
        st.rerun()