# load libraries
from utils.my_llm_utils import *
from utils.my_utils import *
from utils.tavily_search_utils import web_search
#from utils.crawler_utils import crawl_url

import pandas as pd
import time
import os

#-------------------------------------------------------------

# for ollama llm - [gemma3:1b, llama3.2:latest, deepseek-r1:8b, phi4:latest]
llm = get_llm(use_openai=False, model_name="gemma3:1b")


# Check which llm has been loaded
if hasattr(llm, 'model'):
	print(llm.model)  # check loaded model
else:
	print(llm)
	
#-------------------------------------------------------------
# load data
csv_path = "data/input/AI Partnerships_03.csv"

# read the csv file
df, output_path = read_csv_with_output_path(csv_path)

#-------------------------------------------------------------
 # Update the partnerships data
success = update_partnerships(df, output_path)
#-------------------------------------------------------------
#-------------------------------------------------------------
#-------------------------------------------------------------

