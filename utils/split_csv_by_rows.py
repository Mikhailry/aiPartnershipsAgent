import csv
import os

def split_csv_by_rows(input_path, output_prefix, max_rows=50):
    with open(input_path, 'r', newline='', encoding='utf-8') as infile:
        reader = list(csv.reader(infile))
        header = reader[0]
        rows = reader[1:]

    total_rows = len(rows)
    num_files = (total_rows + max_rows - 1) // max_rows

    for i in range(num_files):
        start = i * max_rows
        end = start + max_rows
        chunk = rows[start:end]
        output_path = f"{output_prefix}_{i+1:02d}.csv"
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(header)
            writer.writerows(chunk)
        print(f"Wrote {output_path} with {len(chunk)} rows.")

if __name__ == "__main__":
    input_file = "data/AI Partnerships.csv"
    output_prefix = "data/AI Partnerships"
    split_csv_by_rows(input_file, output_prefix, max_rows=50) 