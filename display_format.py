import streamlit as st
import base64
from translation import translations
from utils import get_base64_image


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
    text = text.replace("\\n", "<br>")
    # print(f"text_modify: {text}")

    # double check
    text = text.replace("\n", "<br>")
    return text


def get_image_html(content: str):
    if "intro_page" in content.lower():
        default_image_path = 'images/eHealth_12Domains.png'  # Default image for eHealth 12 Domains Intro
        base64_intro_img = get_base64_image(default_image_path)  
    
        # Start building the HTML content
        html_content = f"""
            <img src="data:image/png;base64,{base64_intro_img}" style="width:65vw; height:auto; border:none solid #ccc; border-radius:5px; object-fit:cover;">
        """

    else:    
        # Start building the HTML content
        html_content = f"""
            <img src="data:image/jpeg;base64,{content}" style="width:65vw; height:auto; border:none solid #ccc; border-radius:5px; object-fit:cover;">
        """
        
    return html_content


def get_plain_text_html(content: str, font_size: int = 100):

    content = text_modify(content)
    html_content = f"""
        <h1 style="font-size: {font_size}px; text-align: center;">{content}</h1>
    """
    return html_content


def get_yes_no_question_html(content: str, language='en'):
    content = text_modify(content)
    """
    Returns HTML for a centered question with static Yes/No buttons.
    
    Parameters:
    - content (str): The question to display
    """
    html_content = f"""
    <style>
    .button {{
        display: inline-block;
        width: 300px; /* Makes the button much longer */
        padding: 15px 0; /* Vertical padding only since width is fixed */
        margin: 30px 50px 40px 0; /* Adds space between buttons (right margin) */
        border: none;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
        color: white;
        background-color: #007BFF;
        font-size: 45px;
        cursor: pointer;
    }}
    .yes {{
        background-color: #007BFF;  /* Blue for Yes */
    }}
    .no {{
        background-color: #6c757d;  /* Gray for No */
    }}
    </style>
    <div style="display: flex; flex-direction: column; align-items: center;">
        <h1 style="font-size: 70px; text-align: center;">{content}</h1>
        <div style="display: flex; justify-content: center;">
            <span class="button yes;">{translations['Yes'][language]}</span>
            <span class="button no">{translations['No'][language]}</span>
        </div>
    </div>
    """
    return html_content


# Function to get the HTML for the scale question with images
def get_scale_question_html(content: str, order='ascending', min_value=0, max_value=5, language='en'):
    content = text_modify(content)
    
    if order == "descending":
        ord = "desc"
    elif order == "ascending": # Default to ascending if not specified (which means the color scale from Red to Green)
        ord = "asc"

    # Start building the HTML content
    html_content = f"""
    <div style="display: flex; flex-direction: column; align-items: center;">
        <h1 style="font-size: 70px; text-align: center;">{content}</h1>
        <div style="display: flex; justify-content: center; flex-wrap: wrap;">
    """
    
    # Loop through the range from min_value to max_value
    for i in range(min_value, max_value + 1):
        image_path = f"images/scales/{order}/{i}_{ord}.png"  # Assumes images are in the same directory
        base64_image = get_base64_image(image_path)
        # Add each image with button-like styling
        html_content += f'<img src="data:image/png;base64,{base64_image}" style="width:10vw; height:10vw; margin:1vw; border:none solid #ccc; border-radius:5px; object-fit:cover;">'
        
    # Close the HTML divs
    html_content += "</div></div>"
    
    return html_content


def get_gif_html(content: str):
    """
    Returns HTML for a centered GIF image. 
    ****** Currently supports a default "Please Wait" loading GIF. ******
    
    Parameters:
    - content (base64): The base64 encoded content of the GIF image.
    """

    # Secret Command: Please Wait Loading GIF
    if "please_wait" in content.lower():
        image_path = "images/gif/pleaseWait.gif"  
        base64_gif = get_base64_image(image_path)

    else:
        return ''

    html_content = f"""
        <img src="data:image/gif;base64,{base64_gif}" style="width:30vw; height:auto; border:none solid #ccc; border-radius:5px; object-fit:cover;"></img>
    """
    # <p style="text-align: center; margin: 10px 0 0 0; font-size: 15px; ">Please Wait</p>
     
    return html_content