import pandas as pd
import json

with open('data/unique_values.json','r', encoding='utf-8') as f:
    unique_values_dict = json.load(f)

text_cols_to_export = list(unique_values_dict.keys())

# URL of the CSV file
csv_url = f'https://www.datos.gov.co/resource/jbjy-vk9h.csv?$select={",".join(text_cols_to_export)}&$limit=10000000'

# Load the CSV data from the URL into a DataFrame
complete_df = pd.read_csv(csv_url,low_memory=False).fillna("")

# Initialize an empty dictionary to store unique values
unique_values_dict = {}

# Loop through each column in the DataFrame and extract unique values
for column_name in complete_df.columns:
    unique_values = complete_df[column_name].unique().tolist()
    unique_values = sorted(unique_values)
    unique_values_dict[column_name] = unique_values

# Export the unique values dictionary to a JSON file
output_json_file = 'data/unique_values.json'
with open(output_json_file,'w',encoding='utf-8') as json_file:
    json.dump(unique_values_dict, json_file, ensure_ascii=False)

print(f"Unique values extracted and saved to {output_json_file}")