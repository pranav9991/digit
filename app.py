import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from io import BytesIO
import base64

# Configuration
API_KEY = "AIzaSyBAYQzDbnIIvHs_wostIIhWkuTERtARQLI" 
genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-1.5-flash"
TEMPERATURE = 0.3
MAX_OUTPUT_TOKENS = 1000

# Function to analyze car damage
def analyze_car_damage(image, user_description=None):
    try:
        # Initialize model
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config={
                "temperature": TEMPERATURE,
                "max_output_tokens": MAX_OUTPUT_TOKENS
            }
        )

        # Prompt for analysis
        if user_description and user_description.strip():
            prompt = """
            You are an AI claims adjuster for car insurance. Analyze the provided image and user description.

            Respond with a concise, human-readable text summary (no JSON or markdown) in the following format:
            Damaged Part: [e.g., front bumper, headlight, door]
            Damage Type: [e.g., scratches, dent, crack, broken]
            Severity: [e.g., minor, moderate, severe]
            Description Match: [Yes/No, indicates if the image matches the user's description]
            Estimated Repair Cost (INR): [range, e.g., 25000-100000]
            Recommendation: [e.g., Approve, Review Needed, Reject]
            Reason: [brief explanation]

            User Description: "{user_desc}"
            Ensure the response is plain text with no additional formatting or code blocks.
            """.format(user_desc=user_description)
        else:
            prompt = """
            You are an AI claims adjuster for car insurance. Analyze the provided image of a damaged car.

            Respond with a concise, human-readable text summary (no JSON or markdown) in the following format:
            Damaged Part: [e.g., front bumper, headlight, door]
            Damage Type: [e.g., scratches, dent, crack, broken]
            Severity: [e.g., minor, moderate, severe]
            Description Match: None (no user description provided)
            Estimated Repair Cost (INR): [range, e.g., 25000-100000]
            Recommendation: [e.g., Approve, Review Needed, Reject]
            Reason: [brief explanation based on image analysis]

            Ensure the response is plain text with no additional formatting or code blocks.
            """

        # Generate content
        response = model.generate_content([prompt, image])
        response.resolve()

        # Clean response
        cleaned_response = response.text.strip()
        if cleaned_response.startswith("```") and cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[3:-3].strip()

        return {"success": True, "analysis": cleaned_response}

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "raw_response": None
        }

# Function to create a download link for text
def get_text_download_link(data, filename, link_text):
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:text/plain;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

# Streamlit app
st.title("Car Damage Identifier")
st.write("Upload an image of the damaged car. Optionally, provide a description to aid analysis.")

# File uploader for image
uploaded_image = st.file_uploader("Upload Car Damage Image", type=["jpg", "jpeg", "png"])

# Text input for description (optional)
user_description = st.text_area("Enter the description of the damage (optional):", height=100)

# Button to trigger analysis
if st.button("Analyze Damage"):
    if uploaded_image is not None:
        # Load and display the uploaded image
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Analyze the damage
        st.write("Analyzing... Please wait.")
        result = analyze_car_damage(image, user_description)

        # Display results
        if result["success"]:
            st.subheader("Analysis Result")
            st.text(result["analysis"])  # Display as plain text

            # Provide download link for text
            download_link = get_text_download_link(
                result["analysis"],
                "car_damage_analysis.txt",
                "Download Analysis as Text"
            )
            st.markdown(download_link, unsafe_allow_html=True)
        else:
            st.error(f"Error: {result['error']}")
            st.markdown("**Raw Model Response (for debugging):**")
            st.code(result.get("raw_response", "No response available"), language="text")
    else:
        st.warning("Please upload an image to proceed.")

