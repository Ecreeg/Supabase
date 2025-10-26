import streamlit as st
from supabase import create_client, Client
import requests
import json

# -------------------- CONFIG --------------------
st.set_page_config(page_title="😂 Cross-Culture Humor Mapper", page_icon="🌍")

# --- Supabase Setup ---
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------- SESSION STATE --------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

# -------------------- AUTH FUNCTIONS --------------------
def signup(email, password):
    try:
        supabase.auth.sign_up({"email": email, "password": password})
        st.success("✅ Account created! Please log in now.")
    except Exception as e:
        st.error(f"❌ Signup failed: {e}")

def login(email, password):
    try:
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if user and user.user:
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = email
            st.toast(f"Welcome, {email}! 🎉", icon="✅")
        else:
            st.error("Invalid credentials.")
    except Exception as e:
        st.error(f"❌ Login failed: {e}")

def logout():
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.info("👋 Logged out!")

# -------------------- LOGIN PAGE --------------------
if not st.session_state["logged_in"]:
    st.markdown(
        """
        <h1 style='text-align:center; color:#ff66b2;'>😂 Cross-Culture Humor Mapper 🌍</h1>
        <p style='text-align:center; color:gray;'>Translate jokes across cultures and languages!</p>
        """,
        unsafe_allow_html=True
    )

    choice = st.radio("Choose an option:", ["Login", "Sign Up"], horizontal=True)

    email = st.text_input("📧 Email")
    password = st.text_input("🔑 Password", type="password")

    if choice == "Sign Up":
        if st.button("📝 Create Account"):
            signup(email, password)
    else:
        if st.button("🚪 Log In"):
            login(email, password)

    st.stop()  # Don’t render the main app for non-logged users

# -------------------- MAIN APP --------------------
st.markdown(
    f"<h3 style='color:#ff3399;'>Welcome, {st.session_state['user_email']}!</h3>",
    unsafe_allow_html=True
)

if st.button("🔓 Logout"):
    logout()
    st.stop()

st.subheader("🎭 Cross-Culture Humor Translator")

source_culture = st.selectbox("🌎 Source Culture", ["American", "British", "Indian", "Japanese", "Other"])
target_culture = st.selectbox("🎯 Target Culture", ["Indian", "American", "British", "Japanese", "Other"])
target_language = st.selectbox("🗣️ Output Language", ["English", "Hindi", "Spanish", "French", "German", "Japanese"])
joke = st.text_area("💬 Enter your joke or meme text", placeholder="Type your joke here...")

if st.button("✨ Translate Joke"):
    if not joke:
        st.warning("Please enter a joke first!")
    else:
        with st.spinner("Translating with Mistral AI... ⏳"):
            try:
                headers = {
                    "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
                    "Content-Type": "application/json"
                }

                prompt = (
                    f"You are a humor translator. Adapt this {source_culture} joke for a {target_culture} audience, "
                    f"and rewrite it naturally in {target_language}. "
                    f"Keep it funny, culturally relevant, and easy to understand.\n\nJoke: {joke}"
                )

                data = {
                    "model": "mistralai/mistral-small-3.2-24b-instruct:free",
                    "messages": [
                        {"role": "system", "content": "You are a multilingual humor and cultural adaptation assistant."},
                        {"role": "user", "content": prompt}
                    ]
                }

                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    data=json.dumps(data)
                )

                if response.status_code == 200:
                    result = response.json()
                    output = result["choices"][0]["message"]["content"]
                    st.success(f"✅ Translated Joke ({target_language}):")
                    st.markdown(output)
                elif response.status_code == 429:
                    st.error("⚠️ Rate limit reached. Try again later or add your own OpenRouter key.")
                else:
                    st.error(f"❌ Error: {response.status_code}")
                    st.text(response.text)
            except Exception as e:
                st.error(f"Unexpected error: {e}")
