🤖 AI Partnerships Agent

Automatically validate, extract, and summarize AI partnerships from a large dataset using LLMs, web search, and experiment tracking tools.

🚀 Overview

Manually validating 800+ AI partnerships—from sourcing announcements to summarizing the details—was time-consuming and inefficient. This project automates the entire pipeline using an AI agent system and a modular workflow:

✅ Validates and cleans input list of partnerships
🔍 Searches the web for original announcement links (via Tavily API)
🧠 Uses LLMs (OpenAI, Ollama) for entity extraction and summarization
📊 Compares output from multiple models
📈 Tracks model performance and summary quality using Weights & Biases


📦 Tech Stack


| Component            | Purpose                                   |
| -------------------- | ----------------------------------------- |
| **Python**           | Core scripting and data manipulation      |
| **Pandas**           | Data wrangling                            |
| **Tavily API**       | Web search for announcement links         |
| **OpenAI API**       | Cloud-based LLMs (GPT-4, etc.)            |
| **Ollama**           | Local LLMs (Llama, Gemma, Phi)            |
| **Weights & Biases** | Track summary quality & model performance |


🧠 Workflow

Input Parsing: Load and clean a CSV of raw AI partnership entries
Web Search: Use Tavily API to find official announcements
Entity Extraction: Validate company names and extract partnership context with LLMs
Summarization: Run multiple models (OpenAI + Ollama) and compare results
Tracking: Log results to Weights & Biases for performance and tuning


✅ Features

🔁 End-to-end automation from input to summary
📄 Multi-model output comparison
🧪 Model performance tracking with experiment logs
🧩 Modular and extensible codebase


🔮 Future Improvements

 Add real-time discovery of new partnerships
 Smarter company/entity extraction (NER, external databases)
 UI/dashboard for non-technical users
 Real-time alerting for new high-impact partnerships

