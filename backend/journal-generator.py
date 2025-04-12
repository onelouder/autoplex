import os
import re
from datetime import datetime
import logging
from jinja2 import Environment, FileSystemLoader
import html
import markdown

logger = logging.getLogger(__name__)

def generate_journal_entry(topic, api_response):
    """Generate an HTML journal entry from Perplexity API response
    
    Args:
        topic: Topic database model instance
        api_response: Processed response from Perplexity API
        
    Returns:
        str: Filename of the generated HTML file
    """
    logger.info(f"Generating journal entry for topic: {topic.name}")
    
    # Create journal directory if it doesn't exist
    journal_dir = os.path.join('frontend', 'journal_html')
    os.makedirs(journal_dir, exist_ok=True)
    
    # Create a filename from the topic name
    filename = f"{topic.name.lower().replace(' ', '-')}.html"
    filepath = os.path.join(journal_dir, filename)
    
    # Load template environment
    template_dir = os.path.join('frontend', 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('journal_entry.html')
    
    # Process content from API response
    content = api_response.get('content', '')
    citations = api_response.get('citations', [])
    
    # Convert markdown to HTML if content appears to be markdown
    if '##' in content or '*' in content:
        content = markdown.markdown(content)
    
    # Extract potential tags from content
    tags = extract_tags(content, topic.name)
    
    # Get current time for the update timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare data for template
    template_data = {
        'title': topic.name,
        'content': content,
        'citations': citations,
        'timestamp': timestamp,
        'tags': tags,
        'query': topic.query
    }
    
    # Render the template
    html_content = template.render(**template_data)
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"Journal entry generated: {filepath}")
    return filename

def extract_tags(content, topic_name):
    """Extract potential tags from content based on keyword frequency
    
    Args:
        content (str): The content text
        topic_name (str): The name of the topic
        
    Returns:
        list: Extracted tags
    """
    # Simple tag extraction based on capitalized words and phrases
    words = re.findall(r'\b[A-Z][a-zA-Z]*\b', content)
    phrases = re.findall(r'\b[A-Z][a-zA-Z]* [A-Z][a-zA-Z]*\b', content)
    
    # Count occurrences
    word_counts = {}
    for word in words:
        if len(word) > 3:  # Ignore short words
            word_counts[word] = word_counts.get(word, 0) + 1
    
    for phrase in phrases:
        word_counts[phrase] = word_counts.get(phrase, 0) + 1
    
    # Get the most frequent words/phrases
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Extract top tags (excluding the topic name itself)
    tags = []
    for word, count in sorted_words[:10]:  # Get top 10 candidates
        if count >= 2 and word.lower() not in topic_name.lower():
            tags.append(word)
    
    # Add default categories
    topic_lower = topic_name.lower()
    
    if 'quantum' in topic_lower or 'physics' in topic_lower:
        tags.extend(['Physics', 'Technology'])
    
    if 'ai' in topic_lower or 'artificial intelligence' in topic_lower:
        tags.extend(['AI', 'Technology'])
    
    if 'urban' in topic_lower or 'city' in topic_lower:
        tags.extend(['Urban', 'Planning'])
    
    # Deduplicate and limit to 5 tags
    unique_tags = []
    for tag in tags:
        if tag not in unique_tags:
            unique_tags.append(tag)
    
    return unique_tags[:5]

def format_content(content):
    """Format content with proper HTML and highlighting
    
    Args:
        content (str): Raw content from API
        
    Returns:
        str: Formatted HTML content
    """
    # Escape HTML to prevent injection
    content = html.escape(content)
    
    # Format citations [1] -> <sup>[1]</sup>
    content = re.sub(r'\[(\d+)\]', r'<sup>[1]</sup>', content)
    
    # Format headings (assuming markdown-like syntax)
    content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    
    # Format paragraphs
    paragraphs = content.split('\n\n')
    formatted_paragraphs = []
    
    for p in paragraphs:
        if not p.startswith('<h') and p.strip():
            formatted_paragraphs.append(f'<p>{p}</p>')
        else:
            formatted_paragraphs.append(p)
    
    return '\n'.join(formatted_paragraphs)
