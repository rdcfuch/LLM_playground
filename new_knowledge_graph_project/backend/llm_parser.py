import json
import requests
import os

class LLMParser:
    def __init__(self, api_key=None):
        """Initialize the LLM Parser with an OpenAI API key"""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
    
    def _extract_jsonld_from_response(self, response):
        """Extract JSON-LD data from the API response"""
        result = response.json()
        jsonld_text = result["choices"][0]["message"]["content"].strip()
        
        # Try to parse the JSON-LD text
        try:
            return json.loads(jsonld_text)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON-LD: {e}")
            # Try to extract JSON from markdown code blocks if present
            if "```json" in jsonld_text:
                start = jsonld_text.find("```json") + 7
                end = jsonld_text.find("```", start)
                if end > start:
                    json_content = jsonld_text[start:end].strip()
                    return json.loads(json_content)
            
            # If we can't parse it, return the raw text
            return {"error": "Could not parse JSON-LD", "raw_text": jsonld_text}
    
    def parse_text_to_jsonld(self, text):
        """
        Parse unstructured text into JSON-LD format using LLM
        """
        print(f"\n=== LLMParser.parse_text_to_jsonld called ===")
        print(f"Text length: {len(text)}")
        print(f"First 100 chars: {text[:100]}...")
        print(f"API Key available: {'Yes' if self.api_key else 'No'}")
        
        try:
            # Call OpenAI API
            print("Calling OpenAI API...")
            # Define the system prompt for the LLM
            system_prompt = """
            You are an expert in knowledge graph extraction. Your task is to extract entities and relationships from unstructured text and format them as JSON-LD.
            
            Follow these guidelines:
            1. Identify key entities (people, organizations, locations, assets, etc.)
            2. Extract properties for each entity
            3. Identify relationships between entities
            4. Format the output as valid JSON-LD with @context, @type, and appropriate properties
            5. Use schema.org vocabulary where applicable
            6. Create URIs for entities using a consistent pattern
            
            The output should be a valid JSON-LD object that can be imported into a knowledge graph.
            """
            
            # Define the user prompt
            user_prompt = f"""
            Extract entities and relationships from the following text and format as JSON-LD:
            
            {text}
            
            Return ONLY the JSON-LD object, no explanations or other text.
            """
            
            # Call the OpenAI API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": "gpt-4o-mini", # You can change this to other models like "gpt-4" if needed
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.2,  # Lower temperature for more deterministic output
                "max_tokens": 2000   # Adjust based on expected output size
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
            
            print(f"Response received from OpenAI. Status: {response.status_code}")
            
            # Extract JSON-LD from response
            jsonld_data = self._extract_jsonld_from_response(response)
            print(f"Extracted JSON-LD data with {len(jsonld_data.keys()) if isinstance(jsonld_data, dict) else 'unknown'} keys")
            
            return jsonld_data
            
        except Exception as e:
            print(f"Error in parse_text_to_jsonld: {str(e)}")
            import traceback
            traceback.print_exc()
            raise  # Re-raise the exception