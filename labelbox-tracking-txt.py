import os
import pandas as pd
from datetime import datetime

# Directory containing the CSV files organized by categories
base_directory = r'exports'

# Generate a date stamp
date_stamp = datetime.now().strftime("%Y-%m-%d")

# Output file with date stamp
output_file = os.path.join("tracking_data", f"tracking_report_{date_stamp}.txt")

# Initialize the report data structure
report_data = []

# Define a function to extract the grade level from the project name
def extract_grade_level(project_name):
    try:
        if "Grade" in project_name:
            grade_part = project_name.split(" ")[0]
            if grade_part.endswith(("th", "nd", "rd", "st")):
                return int(grade_part[:-2])  # Extract the numeric part of the grade
        return None
    except Exception:
        return None

# Process each category folder in the base directory
for category_folder in os.listdir(base_directory):
    category_path = os.path.join(base_directory, category_folder)
    if os.path.isdir(category_path):  # Ensure it's a folder
        # Use the folder name as the category
        category = category_folder

        # Process each CSV file in the category folder
        for file_name in os.listdir(category_path):
            if file_name.endswith('.csv'):
                file_path = os.path.join(category_path, file_name)

                # Load the CSV file
                data = pd.read_csv(file_path)

                # Extract project name
                project_name = data['dataset_name'].iloc[0]
                grade_level = extract_grade_level(project_name)

                # Validate if required columns exist
                required_columns = [f'labeller_{i}_items_labeled' for i in range(1, 11)]
                if not any(col in data.columns for col in required_columns):
                    print(f"Skipping file {file_name} in {category} due to missing columns.")
                    continue

                # Calculate total items in the dataset
                total_items = len(data)

                # Calculate fully labeled items (assume 3 labelers needed for full labeling)
                fully_labeled_items = sum(
                    (data[[col for col in required_columns if col in data]].notnull()).sum(axis=1) >= 3
                )

                # Add overall project summary
                report_data.append({
                    "Category": category,
                    "Grade Level": grade_level,
                    "Project Name": project_name,
                    "Progress": f"{fully_labeled_items}/{total_items} items fully labeled",
                    "Details": []
                })

                # Process each labeler
                aggregated_data = {}
                for i in range(1, 11):
                    email_col = f'labeller_{i}_email'
                    labeled_col = f'labeller_{i}_items_labeled'
                    time_col = f'labeller_{i}_time_minutes'

                    if all(col in data.columns for col in [email_col, labeled_col, time_col]):
                        labeler_data = data[[email_col, labeled_col, time_col]].dropna()
                        for _, row in labeler_data.iterrows():
                            labeler_email = row[email_col]
                            total_labels = row[labeled_col]
                            total_time = row[time_col]

                            if labeler_email not in aggregated_data:
                                aggregated_data[labeler_email] = {
                                    "total_labels": 0,
                                    "total_time": 0
                                }

                            aggregated_data[labeler_email]["total_labels"] += total_labels
                            aggregated_data[labeler_email]["total_time"] += total_time

                for email, stats in aggregated_data.items():
                    total_labels_percentage = (stats["total_labels"] / total_items) * 100 if total_items else 0
                    report_data[-1]["Details"].append(
                        f"  Labeler: {email}\n    Labels: {stats['total_labels']}/{total_items}\n    Labels Percentage: {total_labels_percentage:.2f}%\n    Time Spent: {stats['total_time']:.2f} minutes"
                    )

# Sort the report data by category and grade level
report_data.sort(key=lambda x: (x["Category"], x["Grade Level"] or float('inf')))

# Write the sorted report to a text file
with open(output_file, 'w', encoding='utf-8') as f:
    for entry in report_data:
        f.write(f"Category: {entry['Category']}\n")
        f.write(f"Project Name: {entry['Project Name']}\n")
        f.write(f"Progress: {entry['Progress']}\n")
        for detail in entry["Details"]:
            f.write(detail + "\n")
        f.write("\n")

print(f"Report generated and saved to {output_file}.")