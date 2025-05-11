import re
from datetime import datetime
import pandas as pd
import os

from utils.tavily_search_utils import web_search
from utils.my_llm_utils import summarize_text_partnership

import time
from urllib.parse import urlparse

def clean_date(date_str):
    """Convert dates like 'Sep-24' to a standardized format 'yyyy-mm'"""
    if not isinstance(date_str, str) or not date_str:
        return None
    
    try:
        # Map month abbreviations to numbers
        month_map = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        
        # Split the date string into month and year
        parts = date_str.strip().split('-')
        if len(parts) != 2:
            return None
            
        month_abbr, year = parts
        
        # Convert year to 4-digits (assuming 20xx for brevity)
        if len(year) == 2:
            year = f"20{year}"
            
        # Get month number
        month_num = month_map.get(month_abbr, None)
        if not month_num:
            return None
            
        return f"{year}-{month_num}"
    except:
        return None



def extract_date_from_text(text):
    """Try to extract a date from text using patterns"""
    # Look for common date patterns
    patterns = [
        r'(\w+\s+\d{1,2},\s*20\d{2})',  # e.g., "October 23, 2024"
        r'(\d{1,2}\s+\w+\s+20\d{2})',    # e.g., "23 October 2024"
        r'(20\d{2}-\d{1,2}-\d{1,2})'     # e.g., "2024-10-23"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            try:
                date_str = matches[0]
                # Try to parse the date
                date_obj = None
                
                # Try different formats
                formats = [
                    '%B %d, %Y',      # "October 23, 2024"
                    '%b %d, %Y',      # "Oct 23, 2024"
                    '%d %B %Y',       # "23 October 2024"
                    '%d %b %Y',       # "23 Oct 2024"
                    '%Y-%m-%d'        # "2024-10-23"
                ]
                
                for fmt in formats:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        if date_obj:
                            # Return in month-year format
                            return f"{date_obj.strftime('%b')}-{date_obj.strftime('%y')}"
                    except:
                        continue
            except:
                pass
    return None

# Validate Link (basic check)
def validate_link(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def read_csv_with_output_path(csv_path: str, output_path: str = None) -> tuple[pd.DataFrame, str]:
    """
    Read a CSV file and generate an output path if not provided.
    
    Args:
        csv_path (str): Path to input CSV file
        output_path (str, optional): Path to save updated CSV. If None, creates a new filename
    
    Returns:
        tuple[pd.DataFrame, str]: DataFrame containing the CSV data and the output path
    """
    # If no output path is provided, create one based on the input filename
    if not output_path:
        dirname, filename = os.path.split(csv_path)
        base, ext = os.path.splitext(filename)
        output_path = os.path.join(dirname, f"{base}_updated{ext}")
    
    # Read the CSV file
    try:
        df = pd.read_csv(csv_path)
        return df, output_path
    except Exception as e:
        print(f"Error reading CSV: {e}")
        raise

def find_partnership_info(partner1, partner2, partner3=None, return_raw_content=True):
    """Search for partnership information using Tavily
    partner1, partner2, partner3 are the names of the companies to search for
    partner3 is optional, it is the name of the third partner in the partnership
    returns a tuple of the link, date, and summary of the partnership

    returns None, None, None if no partnership info is found
    returns the link, date, and summary of the partnership if found
    """

    # Remove None values and ensure all partners are strings
    partners = [p for p in [partner1, partner2, partner3] if p and isinstance(p, str)]
    
    if len(partners) < 2:
        return None, None, None, None if return_raw_content else None
    
    # Construct search query
    query = f"{partner1} {partner2} AI partnership announcement"
    if partner3 and isinstance(partner3, str) and partner3.strip():
        query += f" {partner3}"
        
    print(f"Searching for: {query}")
    
    # Search for the partnership info
    try:
        search_results = web_search(query, max_results=3)
        
        if not search_results or not search_results.get('results'):
            return None, None, None, None if return_raw_content else None
            
        # Filter results to find relevant information
        relevant_results = []
        for result in search_results['results']:
            # Check if both company names are in the title or content
            title = result.get('title', '').lower()
            content = result.get('content', '').lower()
            full_text = title + ' ' + content
            
            # Check if both main partners are mentioned
            if partner1.lower() in full_text and partner2.lower() in full_text:
                # Check for words indicating partnership
                partnership_keywords = ['partner', 'collaboration', 'agreement', 'alliance', 'join']
                if any(keyword in full_text for keyword in partnership_keywords):
                    relevant_results.append(result)
        
        # Use the most relevant result or fall back to the first one
        result = relevant_results[0] if relevant_results else search_results['results'][0]
        
        link = result.get('url')
        content = result.get('content', '')
        
        # Try to extract date from content
        date = extract_date_from_text(content)
        
        # Generate summary if we have content
        summary = None
        if content and len(content.strip()) > 10:
            summary = summarize_text_partnership(content, partner1, partner2)
        else:
            print(f"Warning: No valid content found for link: {link}")
            summary = "No content available from link"
        
        raw_content = content if return_raw_content else None
        
        return link, date, summary, raw_content
        
    except Exception as e:
        print(f"Error searching for partnership info: {str(e)}")
        return None, None, None, None if return_raw_content else None
    

def update_partnerships(df, output_path=None):
    """Update the AI partnerships CSV with missing information"""
    
    # Add summary and raw_content columns if they don't exist
    if 'summary' not in df.columns:
        df['summary'] = None
    if 'raw_content' not in df.columns:
        df['raw_content'] = None
    
    # Process each row
    for idx, row in df.iterrows():
        partner1 = row.get('partner1')
        partner2 = row.get('partner2')
        partner3 = row.get('partner3')
        
        # Skip if we don't have at least two partners
        if not isinstance(partner1, str) or not isinstance(partner2, str):
            continue
            
        print(f"\nProcessing partnership: {partner1} and {partner2}")
        
        # Check if we have a valid link
        link1 = row.get('Link')
        link2 = row.get('link 2')
        
        valid_link = None
        content = None
        
        # Validate existing links
        if isinstance(link1, str) and validate_link(link1):
            valid_link = link1
        elif isinstance(link2, str) and validate_link(link2):
            valid_link = link2
        
        # If no valid link or missing date, search for information
        if not valid_link or pd.isna(row.get('When announced')):
            new_link, new_date, summary, raw_content = find_partnership_info(partner1, partner2, partner3, return_raw_content=True)
            
            # Update link if we found one
            if new_link and validate_link(new_link):
                df.at[idx, 'Link'] = new_link
                valid_link = new_link
                print(f"Found new link: {new_link}")
                
            # Update date if we found one
            if new_date and (pd.isna(row.get('When announced')) or not row.get('When announced')):
                df.at[idx, 'When announced'] = new_date
                print(f"Found new date: {new_date}")
                
            # Update summary and raw content if we found them
            if summary:
                df.at[idx, 'summary'] = summary
                print(f"Generated summary: {summary}")
            if raw_content:
                df.at[idx, 'raw_content'] = raw_content
                print("Stored raw content")
            
        # If we have a valid link but no summary, try to generate one
        elif valid_link and (pd.isna(row.get('summary')) or not row.get('summary')):
            print(f"Generating summary based on existing link...")
            search_results = web_search(valid_link, max_results=1)
            
            if search_results and search_results.get('results'):
                content = search_results['results'][0].get('content', '')
                if content and len(content.strip()) > 10:
                    summary = summarize_text_partnership(content, partner1, partner2)
                    df.at[idx, 'summary'] = summary
                    df.at[idx, 'raw_content'] = content
                    print(f"Generated summary: {summary}")
                    print("Stored raw content")
                else:
                    # If no content from the link, fall back to searching for partnership info
                    print(f"No content found from link, searching for partnership info...")
                    new_link, new_date, summary, raw_content = find_partnership_info(partner1, partner2, partner3, return_raw_content=True)
                    
                    # Update link if we found a better one
                    if new_link and validate_link(new_link):
                        df.at[idx, 'Link'] = new_link
                        print(f"Found better link: {new_link}")
                    
                    # Update date if we found one
                    if new_date and (pd.isna(row.get('When announced')) or not row.get('When announced')):
                        df.at[idx, 'When announced'] = new_date
                        print(f"Found new date: {new_date}")
                    
                    # Update summary and raw content if we found them
                    if summary:
                        df.at[idx, 'summary'] = summary
                        print(f"Generated summary from new search: {summary}")
                    if raw_content:
                        df.at[idx, 'raw_content'] = raw_content
                        print("Stored raw content")
                    else:
                        df.at[idx, 'summary'] = "No content available from any source"
                        print("No content available from any source")
            else:
                # If no search results from the link, fall back to searching for partnership info
                print(f"No search results from link, searching for partnership info...")
                new_link, new_date, summary, raw_content = find_partnership_info(partner1, partner2, partner3, return_raw_content=True)
                
                # Update link if we found a better one
                if new_link and validate_link(new_link):
                    df.at[idx, 'Link'] = new_link
                    print(f"Found better link: {new_link}")
                
                # Update date if we found one
                if new_date and (pd.isna(row.get('When announced')) or not row.get('When announced')):
                    df.at[idx, 'When announced'] = new_date
                    print(f"Found new date: {new_date}")
                
                # Update summary and raw content if we found them
                if summary:
                    df.at[idx, 'summary'] = summary
                    print(f"Generated summary from new search: {summary}")
                if raw_content:
                    df.at[idx, 'raw_content'] = raw_content
                    print("Stored raw content")
                else:
                    df.at[idx, 'summary'] = "No content available from any source"
                    print("No content available from any source")
                    
        # Add a small delay to avoid rate limits
        time.sleep(1)
        
    # Save the updated data
    try:
        df.to_csv(output_path, index=False)
        print(f"\nUpdated data saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False