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

# Custom CSS for styling
st.markdown("""
<style>
body {
    background-color: #f0f2f6;
    font-family: 'Arial', sans-serif;
}
.stApp {
    max-width: 1200px;
    margin: 0 auto;
}
h1 {
    color: #1a73e8;
    text-align: center;
    font-size: 2.5em;
    margin-bottom: 10px;
}
h3 {
    color: #333;
    font-size: 1.5em;
}
.stButton>button {
    background-color: #1a73e8;
    color: white;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 16px;
    border: none;
    transition: background-color 0.3s;
}
.stButton>button:hover {
    background-color: #1557b0;
}
.stTextArea textarea {
    border-radius: 8px;
    border: 1px solid #ccc;
    padding: 10px;
}
.result-container {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
.download-link {
    color: #1a73e8;
    font-weight: bold;
    text-decoration: none;
}
.download-link:hover {
    text-decoration: underline;
}
.tab-content {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# Function to analyze car damage and translate to Hindi
def analyze_car_damage(images, user_description=None):
    try:
        # Initialize model
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config={
                "temperature": TEMPERATURE,
                "max_output_tokens": MAX_OUTPUT_TOKENS
            }
        )

        # Prompt for analysis and translation
        if user_description and user_description.strip():
            prompt = """
            You are an AI claims adjuster for car insurance. Analyze the provided image(s) and user description.

            Respond with two sections in plain text (no JSON or markdown):
            1. English Analysis in the format:
               Damaged Part: [e.g., front bumper, headlight, door]
               Damage Type: [e.g., scratches, dent, crack, broken]
               Severity: [e.g., minor, moderate, severe]
               Description Match: [Yes/No, indicates if the image matches the user's description]
               Estimated Repair Cost (INR): [range, e.g., 25000-100000]
               Recommendation: [e.g., Approve, Review Needed, Reject]
               Reason: [brief explanation]
            2. Hindi Translation of the above analysis in the format:
               क्षतिग्रस्त हिस्सा: [e.g., सामने का बम्पर, हेडलाइट, दरवाजा]
               क्षति का प्रकार: [e.g., खरोंच, डेंट, दरार, टूटा हुआ]
               गंभीरता: [e.g., मामूली, मध्यम, गंभीर]
               विवरण मिलान: [हाँ/नहीं, indicates if the image matches the user's description]
               अनुमानित मरम्मत लागत (INR): [range, e.g., 25000-100000]
               सिफारिश: [e.g., स्वीकृत, समीक्षा आवश्यक, अस्वीकृत]
               कारण: [brief explanation]

            User Description: "{user_desc}"
            If multiple images are provided, combine findings into a single cohesive analysis, considering all perspectives. Ensure the response is plain text with no additional formatting or code blocks.
            """.format(user_desc=user_description)
        else:
            prompt = """
            You are an AI claims adjuster for car insurance. Analyze the provided image(s) of a damaged car.

            Respond with two sections in plain text (no JSON or markdown):
            1. English Analysis in the format:
               Damaged Part: [e.g., front bumper, headlight, door]
               Damage Type: [e.g., scratches, dent, crack, broken]
               Severity: [e.g., minor, moderate, severe]
               Description Match: None (no user description provided)
               Estimated Repair Cost (INR): [range, e.g., 25000-100000]
               Recommendation: [e.g., Approve, Review Needed, Reject]
               Reason: [brief explanation based on image analysis]
            2. Hindi Translation of the above analysis in the format:
               क्षतिग्रस्त हिस्सा: [e.g., सामने का बम्पर, हेडलाइट, दरवाजा]
               क्षति का प्रकार: [e.g., खरोंच, डेंट, दरार, टूटा हुआ]
               गंभीरता: [e.g., मामूली, मध्यम, गंभीर]
               विवरण मिलान: कोई नहीं (no user description provided)
               अनुमानित मरम्मत लागत (INR): [range, e.g., 25000-100000]
               सिफारिश: [e.g., स्वीकृत, समीक्षा आवश्यक, अस्वीकृत]
               कारण: [brief explanation]

            If multiple images are provided, combine findings into a single cohesive analysis, considering all perspectives. Ensure the response is plain text with no additional formatting or code blocks.
            """

        # Combine images for analysis
        content = [prompt] + images
        response = model.generate_content(content)
        response.resolve()

        # Clean response
        cleaned_response = response.text.strip()
        if cleaned_response.startswith("```") and cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[3:-3].strip()

        # Split response into English and Hindi sections
        sections = cleaned_response.split("\n\n")
        if len(sections) >= 2:
            english_analysis = sections[0].strip()
            hindi_analysis = sections[1].strip()
        else:
            english_analysis = cleaned_response
            hindi_analysis = "Hindi translation not available."

        return {
            "success": True,
            "english_analysis": english_analysis,
            "hindi_analysis": hindi_analysis
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "raw_response": None
        }

# Function to create a download link for text
def get_text_download_link(data, filename, link_text):
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:text/plain;base64,{b64}" download="{filename}" class="download-link">{link_text}</a>'
    return href

# Streamlit app
st.title("Car Damage Identifier")
st.write("Upload one or more images of the damaged car. Optionally, provide a description to aid analysis.")

# File uploader for multiple images
uploaded_images = st.file_uploader("Upload Car Damage Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

user_description = st.text_area("Enter the description of the damage (optional):", height=100)


if st.button("Analyze Damage"):
    if uploaded_images:
        images = []
        for idx, uploaded_image in enumerate(uploaded_images):
            image = Image.open(uploaded_image)
            images.append(image)
            st.image(image, caption=f"Uploaded Image {idx + 1}", use_column_width=True)

        
        with st.spinner("Analyzing images... Please wait."):
            result = analyze_car_damage(images, user_description)

        
        if result["success"]:
            st.subheader("Analysis Result")
            # Use tabs for English and Hindi outputs
            tab1, tab2 = st.tabs(["English", "Hindi"])
            with tab1:
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                st.text(result["english_analysis"])
                st.markdown('</div>', unsafe_allow_html=True)
                download_link_en = get_text_download_link(
                    result["english_analysis"],
                    "car_damage_analysis_en.txt",
                    "Download English Analysis"
                )
                st.markdown(download_link_en, unsafe_allow_html=True)
            with tab2:
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                st.text(result["hindi_analysis"])
                st.markdown('</div>', unsafe_allow_html=True)
                download_link_hi = get_text_download_link(
                    result["hindi_analysis"],
                    "car_damage_analysis_hi.txt",
                    "Download Hindi Analysis"
                )
                st.markdown(download_link_hi, unsafe_allow_html=True)
        else:
            st.error(f"Error: {result['error']}")
            st.markdown("**Raw Model Response (for debugging):**")
            st.code(result.get("raw_response", "No response available"), language="text")
            
    else:
        st.warning("Please upload at least one image to proceed.")
