# Text2SQL Project

This project implements a lightweight Text-to-SQL pipeline combining schema linking and structured prompting for zero-shot SQL generation.

## 1. Clone the repository

```bash
git clone https://github.com/llllleeeewwwiis/text2sql-project.git
cd text2sql-project
```

## 2. Download the dataset

Download and unzip the Spider subset:

[Download link](https://drive.google.com/file/d/1403EGqzIDoHMdQF4c9Bkyl7dZLZ5Wt6J/view)

Make sure the unzipped folder structure is:

```
text2sql-project/
├── spider_data/
│   └── test_database/
│       └── concert_singer/
│           ├── concert_singer.sqlite
│           └── dev.json
```

## 3. Install dependencies

### 3.1 Install Ollama

Follow instructions to install Ollama and pull the Qwen 2.5-3B model:

```bash
# Install Ollama (Mac)
brew install ollama

# Pull the Qwen2.5-3B model
ollama pull qwen-2.5-3b

# Start Ollama service
ollama start
```

### 3.2 Install Python packages

We recommend using a Conda environment:

```bash
conda create -n text2sql python=3.10
conda activate text2sql
```

Install required Python packages:

```bash
pip install -r requirements.txt
```

## 4. Run the test script

```bash
python3 spider_test.py
```

This will execute the pipeline on the `concert_singer` subset (first 45 questions in `dev.json`) and print the execution accuracy.
