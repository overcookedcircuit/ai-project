import json
import requests
from typing import List, Dict
from transformers import pipeline
import spacy

# Load the spaCy model for entity extraction
nlp = spacy.load("en_core_web_sm")

# Configuration
RELIEFWEB_API_URL = 'https://api.reliefweb.int/v1/reports'
DISASTER_REPORT_TEMPLATE = 'Disaster report '

def fetch_disaster_reports(query: str) -> List[Dict]:
    """
    Fetch disaster reports from the ReliefWeb API based on a query.
    
    Args:
        query (str): The search query for the reports.
        
    Returns:
        List[Dict]: A list of reports in JSON format.
    """
    response = requests.get(f"{RELIEFWEB_API_URL}?q={query}")
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"Error fetching data: {response.status_code}")
        return []

def summarize_reports(reports: List[Dict]) -> str:
    """
    Generate a summary for the provided disaster reports.
    
    Args:
        reports (List[Dict]): List of disaster reports.
        
    Returns:
        str: A summary of the reports.
    """
    # Use Hugging Face's transformers pipeline for summarization
    summarizer = pipeline("summarization")
    full_text = " ".join(report['content'] for report in reports)
    summary = summarizer(full_text, max_length=150, min_length=30, do_sample=False)
    return summary[0]['summary_text']

def extract_entities_from_text(text: str) -> List[Dict]:
    """
    Extract relevant entities from the provided text using spaCy.
    
    Args:
        text (str): The text from which to extract entities.
        
    Returns:
        List[Dict]: List of entities with their types.
    """
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append({
            'entity_type': ent.label_,
            'entity': ent.text
        })
    return entities

def main():
    # Example query
    query = 'earthquake 2024'
    
    # Fetch disaster reports
    reports = fetch_disaster_reports(query)
    
    if not reports:
        print("No reports found.")
        return
    
    # Summarize the reports
    summary = summarize_reports(reports)
    print("Summary of reports:")
    print(summary)
    
    # Extract entities from the summary
    entities = extract_entities_from_text(summary)
    print("\nExtracted Entities:")
    for entity in entities:
        print(f"Entity Type: {entity['entity_type']}, Entity: {entity['entity']}")
    
    # Example of how you might use the data
    print("\nGenerated Query for Additional Data:")
    print(f"Disaster information for {query}")

if __name__ == '__main__':
    main()
