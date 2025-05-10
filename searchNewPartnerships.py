from utils.my_llm_utils import *
from utils.my_utils import *
from utils.tavily_search_utils import web_search
import pandas as pd
from datetime import datetime, timedelta
import time

def get_existing_partnerships(csv_path):
    """Read existing partnerships and create a set of normalized partner pairs"""
    df = pd.read_csv(csv_path)
    existing_pairs = set()
    
    for _, row in df.iterrows():
        partner1 = str(row['partner1']).lower().strip()
        partner2 = str(row['partner2']).lower().strip()
        # Store pairs in both orders to handle case-insensitive matching
        existing_pairs.add(frozenset([partner1, partner2]))
    
    return existing_pairs

def validate_partnership(partner1, partner2, content):
    """Validate if the content describes an AI partnership between the two companies using LLM"""
    from utils.my_llm_utils import get_llm
    
    # Initialize LLM
    #llm = get_llm(use_openai=False, model_name="gemma3:1b")
    llm = get_llm(use_openai=True)
    
    # Create validation prompt
    prompt = f"""
    You are a validation assistant. Answer these three questions about the text below:
    1. Does this text describe a partnership between {partner1} and {partner2}?
    2. Is this partnership related to AI or machine learning?
    3. Are {partner1} and {partner2} real companies?

    Answer with ONLY "yes" or "no" for each question, separated by commas.
    Example: yes,yes,yes
    Example: no,yes,no

    Text:
    {content}
    """
    
    try:
        # Get response from LLM
        response = llm.invoke(prompt)
        
        # Convert response to string and clean up
        response_str = response.content if hasattr(response, 'content') else str(response)
        response_str = response_str.strip().lower()
        
        print(f"Debug - Raw LLM response: {response_str}")  # Debug line
        
        # Parse the yes/no responses
        try:
            # Split by comma and clean up each answer
            answers = [ans.strip() for ans in response_str.split(',')]
            if len(answers) != 3:
                return False, f"Invalid response format. Expected 3 answers, got {len(answers)}"
            
            # Convert yes/no to boolean
            is_valid_partnership = answers[0] == 'yes'
            is_ai_related = answers[1] == 'yes'
            are_real_companies = answers[2] == 'yes'
            
            # Check all conditions
            is_valid = is_valid_partnership and is_ai_related and are_real_companies
            
            # Generate rejection reason
            if not is_valid:
                reasons = []
                if not is_valid_partnership:
                    reasons.append("not a valid partnership")
                if not is_ai_related:
                    reasons.append("not AI-related")
                if not are_real_companies:
                    reasons.append("companies not verified as real")
                rejection_reason = ", ".join(reasons)
            else:
                rejection_reason = "passed"
            
            return is_valid, rejection_reason
            
        except Exception as parse_error:
            return False, f"Failed to parse yes/no responses: {str(parse_error)}"
        
    except Exception as e:
        error_msg = f"Error in LLM validation: {str(e)}"
        print(error_msg)
        return False, error_msg

def search_new_partnerships(existing_pairs, days_back=30):
    """Search for new AI partnerships using Tavily"""
    new_partnerships = []
    
    # Multiple search queries to increase coverage
    search_queries = [
        f"company announces AI partnership with company"
        # f"company expands partnership with company AI",
        # f"company and company announce AI partnership",
        # f"company partners with company AI",
        # f"company collaborates with company artificial intelligence",
        # f"company teams up with company AI",
        # f"company joins forces with company AI",
        # f"company strategic partnership with company AI",
        # f"company new partnership with company artificial intelligence",
        # f"company alliance with company AI"
    ]
    
    # Process each search query
    for query in search_queries:
        print(f"\nSearching with query: {query}")
        search_results = web_search(query, max_results=5)
        
        if not search_results or not search_results.get('results'):
            continue
        
        # Process each result
        for result in search_results['results']:
            content = result.get('content', '').lower()
            title = result.get('title', '').lower()
            url = result.get('url')
            
            # Skip if content is too short
            if len(content) < 50:
                continue
                
            # Look for company names in the content
            companies = extract_companies_from_text(content + " " + title)
            
            # Skip if we don't find at least 2 companies
            if len(companies) < 2:
                continue
            
            # Check each pair of companies
            for i in range(len(companies)):
                for j in range(i + 1, len(companies)):
                    partner1 = companies[i]
                    partner2 = companies[j]
                    
                    # Skip if either company name is too short
                    if len(partner1) < 3 or len(partner2) < 3:
                        continue
                    
                    # Check if this partnership is new
                    pair = frozenset([partner1.lower().strip(), partner2.lower().strip()])
                    if pair not in existing_pairs:
                        # Validate the partnership using LLM
                        is_valid, rejection_reason = validate_partnership(partner1, partner2, content)
                        if is_valid:
                            # Extract date
                            date = extract_date_from_text(content)
                            
                            # Add to new partnerships
                            new_partnerships.append({
                                'partner1': partner1,
                                'partner2': partner2,
                                'When announced': date,
                                'Link': url,
                                'raw_content': content
                            })
                            
                            # Add to existing pairs to avoid duplicates
                            existing_pairs.add(pair)
                            
                            print(f"Found new partnership: {partner1} and {partner2}")
                        else:
                            print(f"Skipped partnership: {partner1} and {partner2}")
                            print(f"Reason: {rejection_reason}")
        
        # Add a small delay between queries to avoid rate limits
        time.sleep(1)
    
    return new_partnerships

def extract_companies_from_text(text):
    """Extract potential company names from text using LLM"""
    from utils.my_llm_utils import get_llm
    
    # Initialize LLM
    llm = get_llm(use_openai=False, model_name="gemma3:1b")
    
    # Create prompt for company extraction
    prompt = f"""
    Extract the names of companies involved in a partnership or collaboration from the following text.
    Return ONLY a JSON array of company names, with no additional text or explanation.
    If there are no companies mentioned, return an empty array.
    Clean up company names by removing common suffixes like 'Inc', 'Ltd', 'LLC', 'Corp', 'Corporation'.
    Remove any common prefixes like 'The', 'A', 'An'.
    
    Text:
    {text}
    
    Example format:
    ["Company1", "Company2"]
    """
    
    try:
        # Get response from LLM
        response = llm.invoke(prompt)
        
        # Convert response to string and clean up
        response_str = response.content if hasattr(response, 'content') else str(response)
        
        # Extract JSON array from response
        import json
        import re
        
        # Find JSON array in the response
        json_match = re.search(r'\[.*\]', response_str)
        if json_match:
            companies = json.loads(json_match.group())
        else:
            # If no JSON array found, try to extract company names directly
            companies = [name.strip() for name in response_str.split(',') if name.strip()]
        
        # Clean up company names
        cleaned_companies = []
        for company in companies:
            # Remove common suffixes
            company = re.sub(r'\s+(Inc\.?|Ltd\.?|LLC|Corp\.?|Corporation)$', '', company, flags=re.IGNORECASE)
            # Remove common prefixes
            company = re.sub(r'^(The|A|An)\s+', '', company, flags=re.IGNORECASE)
            # Remove quotes if present
            company = company.strip('"\'')
            if company:
                cleaned_companies.append(company)
        
        return list(set(cleaned_companies))  # Remove duplicates
        
    except Exception as e:
        print(f"Error extracting companies: {str(e)}")
        return []

def main():
    # Configuration
    input_csv = "data/AI Partnerships.csv"
    output_csv = "data/new_partnerships.csv"
    days_back = 30  # Search for partnerships from the last 30 days
    
    # Get existing partnerships
    existing_pairs = get_existing_partnerships(input_csv)
    print(f"Found {len(existing_pairs)} existing partnerships")
    
    # Search for new partnerships
    new_partnerships = search_new_partnerships(existing_pairs, days_back)
    print(f"Found {len(new_partnerships)} new partnerships")
    
    if new_partnerships:
        # Create DataFrame for new partnerships
        df_new = pd.DataFrame(new_partnerships)
        
        # Process new partnerships to get summaries
        df_new = update_partnerships(df_new, output_csv)
        
        print(f"\nNew partnerships saved to {output_csv}")
    else:
        print("No new partnerships found")

if __name__ == "__main__":
    main() 