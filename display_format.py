import streamlit as st
import base64
from translation import translations
from utils import get_base64_image

# # Helper function to convert local images to base64
# def get_base64_image(image_path):
#     with open(image_path, "rb") as f:
#         data = f.read()
#     return base64.b64encode(data).decode()

def text_modify(text: str):
    """
    Function to modify text with some conditions before display.
    
    Parameters:
    - text (str): The input text to be modified.
    
    Returns:
    - str: The modified text with single quotes removed and newlines replaced by spaces.
    """
    # Remove single quotes from the beginning and end of the string
    text = text.strip("'")

    # Replace newline characters with spaces
    text = text.replace("\n", "<br>")
    return text

def display_image(content: base64):
    # Start building the HTML content
    html_content = f"""
    <div style="display: flex; justify-content: center; align-items: center; height: 100%; width: 100%;">
        <img src="data:image/jpeg;base64,{content}" style="width:65%; height:auto; margin:10px; border:none solid #ccc; border-radius:5px; object-fit:cover;">
    </div>
    """
    # Render the HTML in Streamlit
    st.markdown(html_content, unsafe_allow_html=True)


def display_plain_text(content: str):
    content = text_modify(content)
    html_content = f"""
    <div style="text-align: center; margin-top: 250px; margin-left: 100px">
        <h1>{content}</h1>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)


def display_yes_no_question(content: str, language='en'):
    content = text_modify(content)
    """
    Displays a centered question with static Yes/No buttons.
    
    Parameters:
    - content (str): The question to display
    """
    html_content = f"""
    <style>
    .button {{
        display: inline-block;
        width: 230px; /* Makes the button much longer */
        padding: 12px 0; /* Vertical padding only since width is fixed */
        margin: 30px 50px 40px 0; /* Adds space between buttons (right margin) */
        border: none;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
        color: white;
        background-color: #007BFF;
        font-size: 30px;
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
            <span class="button yes;">{translations['Yes'][language]}</span>
            <span class="button no">{translations['No'][language]}</span>
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

# Function to display the scale question with images
def display_scale_question(content: str, order='ascending', min_value=0, max_value=5, language='en'):
    content = text_modify(content)
    
    if order == "descending":
        ord = "desc"
    elif order == "ascending": # Default to ascending if not specified (which means the color scale from Red to Green)
        ord = "asc"

    # Start building the HTML content
    html_content = f"""
    <div style="text-align: center; margin-top: 250px; margin-left: 100px">
        <h1 style="margin-bottom: 30px;">{content}</h1>  <!-- Increased space below title -->
        <div style="display: flex; justify-content: center; flex-wrap: wrap;">
    """
    
    # Loop through the range from min_value to max_value
    for i in range(min_value, max_value + 1):
        image_path = f"images/scales/{order}/{i}_{ord}.png"  # Assumes images are in the same directory
        base64_image = get_base64_image(image_path)
        # Add each image with button-like styling
        html_content += f'<img src="data:image/jpeg;base64,{base64_image}" style="width:80px; height:80px; margin:10px; border:none solid #ccc; border-radius:5px; object-fit:cover;">'
        
    # Close the HTML divs
    html_content += "</div></div>"
    
    # Render the HTML in Streamlit
    st.markdown(html_content, unsafe_allow_html=True)


def display_gif(content: str):
    """
    Displays a centered GIF image. 
    ****** Currently supports a default "Please Wait" loading GIF. ******
    
    Parameters:
    - content (base64): The base64 encoded content of the GIF image.
    """

    # Default Please Wait Loading GIF
    if "please wait" in content.lower():
        image_path = "images/gif/pleaseWait.gif"  
        base64_gif = get_base64_image(image_path)

    else:
        return

    html_content = f"""
    <div style="display: flex; justify-content: center; align-items: center; height: 100%; width: 100%;">
        <img src="data:image/gif;base64,{base64_gif}" style="width:20%; height:auto; margin-top:230px; border:none solid #ccc; border-radius:5px; object-fit:cover;"></img>
    </div>
    """
    # <p style="text-align: center; margin: 10px 0 0 0; font-size: 15px; ">Please Wait</p>
     
    st.markdown(html_content, unsafe_allow_html=True)
