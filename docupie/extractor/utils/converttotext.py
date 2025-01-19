import re

def convert_to_text(markdown):
    if not markdown or not isinstance(markdown, str):
        raise ValueError("Valid markdown content is required.")
    
    # Strip markdown syntax and handle tables
    plain_text = markdown
    
    # Bold
    plain_text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', plain_text)
    
    # Italic
    plain_text = re.sub(r'(\*|_)(.*?)\1', r'\2', plain_text)
    
    # Headings
    plain_text = re.sub(r'(#+\s)', '', plain_text)
    
    # Links
    plain_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', plain_text)
    
    # Images
    plain_text = re.sub(r'!\[(.*?)\]\(.*?\)', r'\1', plain_text)
    
    # Code blocks/inline
    plain_text = re.sub(r'(```.*?\n[\s\S]*?\n```|`.*?`)', '', plain_text)
    
    # Blockquotes
    plain_text = re.sub(r'>+', '', plain_text)
    
    # Excess newlines
    plain_text = re.sub(r'\n{2,}', '\n', plain_text)
    
    # Table rows
    plain_text = re.sub(r'\|([^|]*)\|', lambda m: m.group(1).strip(), plain_text)
    
    # Table dividers
    plain_text = re.sub(r'-+', '', plain_text)
    
    return plain_text.strip()