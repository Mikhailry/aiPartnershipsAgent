from utils.my_llm_utils import *
from utils.my_utils import *
from utils.tavily_search_utils import web_search

import time
import numpy as np
from datetime import datetime

csv_path = "data/AI Partnerships sample_updated.csv"

# read the csv file
df, output_path = read_csv_with_output_path(csv_path)


import wandb
wandb.init(project="AI-Partnerships-agent")

ollamaModels = ["gemma3:1b", "llama3.2:latest", "phi4:latest"]
openAiModels = ["gpt-4o"]

prompt = f"""
    Summarize the following AI partnership announcement in one sentence:
    """

# Initialize statistics dictionary
model_stats = {}

def process_model_summaries(models, use_openai=False):
    for model in models:
        print(f"\nProcessing {model}...")
        llm = get_llm(use_openai=use_openai, model_name=model)
        
        # Initialize statistics for this model
        model_stats[model] = {
            'summary_lengths': [],
            'processing_times': [],
            'start_time': datetime.now()
        }
        
        # iterate over the rows of the dataframe
        for index, row in df.iterrows():
            # get the raw content
            raw_content = row['raw_content']
            
            # Time the summarization
            start_time = time.time()
            # summarize the raw content
            summary = llm.invoke(prompt + "\n" + raw_content)
            end_time = time.time()
            
            # Convert summary to string
            summary_str = summary.content if hasattr(summary, 'content') else str(summary)
            
            # Store statistics
            model_stats[model]['summary_lengths'].append(len(summary_str))
            model_stats[model]['processing_times'].append(end_time - start_time)
            
            # add the summary to the dataframe
            df.at[index, model + '_summary'] = summary_str
            
        # Calculate final statistics
        model_stats[model]['end_time'] = datetime.now()
        model_stats[model]['total_time'] = (model_stats[model]['end_time'] - model_stats[model]['start_time']).total_seconds()
        model_stats[model]['avg_time'] = np.mean(model_stats[model]['processing_times'])
        model_stats[model]['min_time'] = np.min(model_stats[model]['processing_times'])
        model_stats[model]['max_time'] = np.max(model_stats[model]['processing_times'])
        model_stats[model]['median_time'] = np.median(model_stats[model]['processing_times'])
        model_stats[model]['avg_length'] = np.mean(model_stats[model]['summary_lengths'])
        model_stats[model]['min_length'] = np.min(model_stats[model]['summary_lengths'])
        model_stats[model]['max_length'] = np.max(model_stats[model]['summary_lengths'])
        model_stats[model]['median_length'] = np.median(model_stats[model]['summary_lengths'])

# Process Ollama models
process_model_summaries(ollamaModels, use_openai=False)

# Process OpenAI models
process_model_summaries(openAiModels, use_openai=True)

# Create summary DataFrame
summary_stats = pd.DataFrame({
    'Model': list(model_stats.keys()),
    'Total Time (s)': [stats['total_time'] for stats in model_stats.values()],
    'Avg Time (s)': [stats['avg_time'] for stats in model_stats.values()],
    'Min Time (s)': [stats['min_time'] for stats in model_stats.values()],
    'Max Time (s)': [stats['max_time'] for stats in model_stats.values()],
    'Median Time (s)': [stats['median_time'] for stats in model_stats.values()],
    'Avg Length': [stats['avg_length'] for stats in model_stats.values()],
    'Min Length': [stats['min_length'] for stats in model_stats.values()],
    'Max Length': [stats['max_length'] for stats in model_stats.values()],
    'Median Length': [stats['median_length'] for stats in model_stats.values()]
})

# Create modelComparison DataFrame
modelComparison = df[['partner1', 'partner2', 'raw_content'] + [f'{model}_summary' for model in ollamaModels + openAiModels]].copy()

# Convert AIMessage objects to strings
for col in modelComparison.columns:
    if col.endswith('_summary'):
        modelComparison[col] = modelComparison[col].apply(lambda x: x.content if hasattr(x, 'content') else str(x))


# Log both tables to wandb
wandb.log({
    "summaries": wandb.Table(dataframe=modelComparison),
    "model_stats": wandb.Table(dataframe=summary_stats)
})

# Display the summary statistics
print("\nModel Performance Statistics:")
print(summary_stats.to_string(index=False))
