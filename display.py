import streamlit as st
import requests

st.title("Mistral AI Quickstart App")

with st.sidebar:
    mistral_api_key = st.text_input("Mistral AI API Key", type="password")
    "[Get a Mistral API key](#)"  # Replace with the actual link to get an API key


def generate_response(input_text):
    if not mistral_api_key:
        st.info("Please add your Mistral AI API key to continue.")
        return
    
    # Mistral API URL
    mistral_api_url = "https://api.mistral.ai/generate"  # Placeholder URL

    # Payload to send to Mistral API
    payload = {
        "prompt": input_text,
        "temperature": 0.7,
        # Add other parameters required by Mistral API
    }

    headers = {
        "Authorization": f"Bearer {mistral_api_key}",
        "Content-Type": "application/json"
    }

    # Sending request to Mistral AI
    response = requests.post(mistral_api_url, json=payload, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        st.info(response_data.get("generated_text", "No response text found"))
    else:
        st.error(f"Error: {response.status_code} - {response.text}")


with st.form("my_form"):
    text = st.text_area("Enter text:", "What are 3 key advice for learning how to code?")
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        generate_response(text)
