from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def format_text_block(text, tag):
    """Format text based on HTML tag"""
    if not text.strip():
        return ""
        
    if tag.startswith('h'):
        level = int(tag[1])
        # Convert h1-h6 to corresponding number of #
        prefix = '#' * level
        return f"{prefix} {text}"
    elif tag == 'strong' or tag == 'b':
        return f"**{text}**"
    elif tag == 'em' or tag == 'i':
        return f"_{text}_"
    elif tag == 'code':
        return f"`{text}`"
    elif tag == 'pre':
        return f"```\n{text}\n```"
    else:
        return text

def get_clean_text(url):
    """Extract and clean text from webpage with improved formatting"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'img', 'nav', 'footer', 'header', 'aside', 'form', 'button', 'iframe']):
            element.decompose()
        
        # Improved text extraction with better formatting
        cleaned_text = []
        
        # Define the elements we want to process
        target_elements = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'code', 'strong', 'b', 'em', 'i']
        
        for element in soup.find_all(target_elements):
            # Get direct text from element
            text = element.get_text(strip=True)
            if text:
                # Format text based on tag
                formatted_text = format_text_block(text, element.name)
                if formatted_text:
                    cleaned_text.append(formatted_text)
        
        # Join text blocks with appropriate spacing
        final_text = '\n\n'.join(cleaned_text).strip()
        
        # Clean up any excessive newlines
        final_text = re.sub(r'\n{3,}', '\n\n', final_text)
        
        return final_text if final_text else "No readable text found"
    
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    url = None
    if request.method == 'POST':
        url = request.form['url']
        result = get_clean_text(url)
    return render_template('index.html', result=result, url=url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)