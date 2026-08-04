# CodSoft Data Analytics Internship Projects

This repository contains internship-ready solutions for the CodSoft Data Analytics task set. It includes a realistic retail analytics dataset, four fully runnable projects built on that dataset, and a fifth web-scraping project that is ready to run against a live public practice website.

## Included Tasks

1. Data Cleaning and Preprocessing
2. Exploratory Data Analysis (EDA)
3. Data Visualization Dashboard
4. Customer Data Analysis
5. Web Data Extraction and Analysis

## Project Highlights

- A synthetic but realistic retail and customer dataset is generated locally for portfolio use.
- Tasks 1 to 4 share the same dataset, which makes the repo feel like a complete analytics case study instead of disconnected mini-projects.
- Each task writes outputs to the `outputs/` folder and includes a short task-level README.
- Task 5 uses the public practice site `books.toscrape.com` and needs internet access when you run it.

## Quick Start

```powershell
python -m pip install -r requirements.txt
python scripts/generate_raw_dataset.py
python scripts/run_all_tasks.py
```

To include the web scraping task as well:

```powershell
python scripts/run_all_tasks.py --include-web-task
```

## Folder Structure

```text
datasets/
  raw/
  cleaned/
  scraped/
outputs/
  task_1_data_cleaning/
  task_2_eda/
  task_3_visualization_dashboard/
  task_4_customer_analysis/
  task_5_web_extraction_analysis/
scripts/
shared/
task_1_data_cleaning/
task_2_eda/
task_3_visualization_dashboard/
task_4_customer_analysis/
task_5_web_extraction_analysis/
```

## Suggested Submission Flow

1. Run the scripts and review the generated outputs.
2. Push the repository to GitHub with a name like `CODSOFT_TASKNO`.
3. Record a short LinkedIn video explaining the problem, process, and results for each completed task.
4. Use the markdown reports inside `outputs/` as speaking notes for your video.

