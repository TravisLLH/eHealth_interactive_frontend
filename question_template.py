import streamlit as st
import base64
from translation import translations

# Helper function to convert local images to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def display_plain_text(content):
    html_content = f"""
    <div style="text-align: center; margin-top: 250px; margin-left: 100px">
        <h1>{content}</h1>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)


def display_yes_no_question(content, language='en'):
    """
    Displays a centered question with static Yes/No buttons.
    
    Parameters:
    - content (str): The question to display
    """
    html_content = f"""
    <style>
    .button {{
        display: inline-block;
        width: 200px; /* Makes the button much longer */
        padding: 12px 0; /* Vertical padding only since width is fixed */
        margin: 30px 40px 40px 0; /* Adds space between buttons (right margin) */
        border: none;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
        color: white;
        background-color: #007BFF;
        font-size: 16px;
        cursor: pointer;
    }}
    .yes {{
        background-color: #007BFF;  /* Blue for Yes */
    }}
    .no {{
        background-color: #6c757d;  /* Gray for No */
    }}
    </style>
    <div style="text-align: center; margin-top: 250px; margin-left: 100px">
        <h1>{content}</h1>
        <div>
            <span class="button yes">{translations['Yes'][language]}</span>
            <span class="button no">{translations['No'][language]}</span>
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

# Function to display the scale question with images
def display_scale_question(content, min_value, max_value, language='en'):
    # Start building the HTML content
    html_content = f"""
    <div style="text-align: center; margin-top: 250px; margin-left: 100px">
        <h1 style="margin-bottom: 30px;">{content}</h1>  <!-- Increased space below title -->
        <div style="display: flex; justify-content: center; flex-wrap: wrap;">
    """
    
    # Loop through the range from min_value to max_value
    for i in range(min_value, max_value + 1):
        image_path = f"images/scales/{i}.png"  # Assumes images are in the same directory
        base64_image = get_base64_image(image_path)
        # Add each image with button-like styling
        html_content += f'<img src="data:image/jpeg;base64,{base64_image}" style="width:80px; height:80px; margin:10px; border:none solid #ccc; border-radius:5px; object-fit:cover;">'
    
    # Close the HTML divs
    html_content += "</div></div>"
    
    # Render the HTML in Streamlit
    st.markdown(html_content, unsafe_allow_html=True)