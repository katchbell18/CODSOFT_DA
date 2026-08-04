# Task 1: Data Cleaning and Preprocessing

This task loads the raw retail dataset, finds missing values and duplicate records, standardizes inconsistent entries, corrects data types, and exports a clean dataset for later analysis.

## Run

```powershell
python scripts/generate_raw_dataset.py
python task_1_data_cleaning/clean_data.py
```

## Outputs

- `datasets/cleaned/retail_customer_orders_cleaned.csv`
- `outputs/task_1_data_cleaning/data_quality_summary.csv`
- `outputs/task_1_data_cleaning/cleaning_report.md`

