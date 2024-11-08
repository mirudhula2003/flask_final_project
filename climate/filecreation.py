import os
import pandas as pd
import json
import xml.etree.ElementTree as ET

# Create output directory if it doesn't exist
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

def convert_to_json(data, part):
    with open(f"{output_dir}/part_{part}.json", 'w') as json_file:
        json.dump(data.to_dict(orient='records'), json_file)

def convert_to_csv(data, part):
    data.to_csv(f"{output_dir}/part_{part}.csv", index=False)

def convert_to_excel(data, part):
    data.to_excel(f"{output_dir}/part_{part}.xlsx", index=False)

def convert_to_html(data, part):
    html = data.to_html(index=False)
    with open(f"{output_dir}/part_{part}.html", 'w') as html_file:
        html_file.write(html)

def convert_to_xml(data, part):
    root = ET.Element('data')
    for _, row in data.iterrows():
        item = ET.SubElement(root, 'item')
        for col in data.columns:
            child = ET.SubElement(item, col)
            child.text = str(row[col])
    
    tree = ET.ElementTree(root)
    tree.write(f"{output_dir}/part_{part}.xml")

def process_csv(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Divide into 5 parts
    n = len(df) // 5
    for i in range(5):
        start_index = i * n
        end_index = (i + 1) * n if i < 4 else len(df)  # Ensure the last part takes any remaining rows
        part_data = df.iloc[start_index:end_index]

        # Save each part in the specified format
        if i == 0:
            convert_to_json(part_data, i + 1)  # part1 as JSON
        elif i == 1:
            convert_to_csv(part_data, i + 1)   # part2 as CSV
        elif i == 2:
            convert_to_excel(part_data, i + 1) # part3 as Excel
        elif i == 3:
            convert_to_html(part_data, i + 1)  # part4 as HTML
        elif i == 4:
            convert_to_xml(part_data, i + 1)   # part5 as XML

if __name__ == '__main__':
    process_csv('/Users/mirudhulaloganath/Desktop/GUVI/python/assignment3/climate/studentperf.csv')
