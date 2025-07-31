# v0.2.3
import requests
import json
import os
from datetime import datetime
from openai import AzureOpenAI

def generate_event_content(event_params):
    """
    Generate content for an event using an LLM when web scraping fails to retrieve content.
    
    Args:
        event_params (dict): A dictionary containing event details like title, date, address, etc.
        
    Returns:
        str: Generated content for the event
    """
    current_year = datetime.now().year
    
    # Extract parameters from the event_params
    title = event_params.get('title', '')
    date = event_params.get('date', '')
    address = event_params.get('address', '')
    link = event_params.get('link', '')
    
    # Define the response schema to enforce structured output
    response_schema = {
        "type": "object",
        "properties": {
            "event_description": {
                "type": "string",
                "description": "A detailed description of the event"
            },
            "event_significance": {
                "type": "string",
                "description": "The significance of this event in the space industry"
            },
            "expected_attendees": {
                "type": "string",
                "description": "Who typically attends or participates in this event"
            },
            "topics": {
                "type": "string",
                "description": "Notable topics, sessions, or presentations that might be featured"
            }
        },
        "required": ["event_description", "event_significance", "expected_attendees", "topics"]
    }
    
    # Create a prompt for the LLM
    prompt = [{
        "role": "system",
        "content": f"""You are an expert in space industry events and conferences. 
Your task is to fetch detailed information about a space-related event based on the provided details.
The current year is {current_year}.
Please respond with structured information following this JSON schema:
{json.dumps(response_schema, indent=2)}"""
    }, {
        "role": "user",
        "content": f"""Please provide information about the following space industry event:

Title: {title}
Date: {date}
Location: {address}
Event URL: {link}

I need comprehensive information about this event that can be used in a news summary, 
but do not include the given information above or any links in your response. 
If the news content is less than 150 words, you can simply return the content as is. 
Otherwise, please summarize the event in a well-structured format."""
    }]
    
    try:
        # Set up Azure OpenAI client
        api_key = os.environ.get('AZURE_OPENAI_API_KEY')
        azure_endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
        api_version = os.environ.get('AZURE_OPENAI_API_VERSION')

        # Check if environment variables are correctly set
        if not api_key or not azure_endpoint:
            print("Azure OpenAI API Key or Endpoint is not set in the environment variables.")
            return f"The {title} is a space industry event scheduled for {date} in {address}. No additional details are available at this time."

        client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key, 
            api_version=api_version
        )

        # Get response from the LLM
        response = client.chat.completions.create(
            model="gpt-4o",  # The deployment model 
            messages=prompt,
            temperature=0.7
        )
        
        response_content = response.choices[0].message.content
        
        # Try to parse the JSON response
        try:
            json_response = json.loads(response_content)
            
            # Construct a well-formatted content string from the structured response
            content = f"{json_response.get('event_description', '')}\n\n"
            content += f"Significance: {json_response.get('event_significance', '')}\n\n"
            content += f"Expected Participants: {json_response.get('expected_attendees', '')}\n\n"
            content += f"Key Topics: {json_response.get('topics', '')}"
            
            # Clean up the content
            content = content.replace('\n\n', ' ').replace('\n', ' ').strip()
            
        except json.JSONDecodeError:
            # If JSON parsing fails, use the raw response
            content = response_content.strip()
        
        print(f"Successfully generated content for event: {title}")
        return content
    
    except Exception as e:
        print(f"Error generating content for event '{title}': {str(e)}")
        return f"The {title} is a space industry event scheduled for {date} in {address}. No additional details are available at this time."
