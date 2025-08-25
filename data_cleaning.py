import json
import re

def filter_doctor_records_precise(input_file, output_file):
    """
    Filter JSON records:
    - Keep only those with URLs starting with 'https://www.doctorbangladesh.com/dr-'
    - Remove the 'content' field
    - Extract 'location' from the title (after 'in')
    - Extract 'specialty' from the title (between '-' and 'in')
    - Keep only the doctor's name in 'title'
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        filtered_data = []
        for record in data:
            url = record.get('url', '')
            title = record.get('title', '')

            if url.startswith('https://www.doctorbangladesh.com/dr-'):
                # Extract location from title (after ' in ')
                location_match = re.search(r'\s+in\s+(.+)$', title)
                location = location_match.group(1).strip() if location_match else ""

                # Extract specialty (between '-' and 'in')
                specialty_match = re.search(r'-\s*(.*?)\s+in\s+', title)
                specialty = specialty_match.group(1).strip() if specialty_match else ""

                # Extract only the doctor's name (before '-')
                name = title.split('-')[0].strip()

                # Build new record without 'content', and with new fields
                new_record = {
                    key: val for key, val in record.items() if key != 'content'
                }
                new_record['title'] = name
                new_record['specialty'] = specialty
                new_record['location'] = location

                filtered_data.append(new_record)

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, indent=2, ensure_ascii=False)

        print(f"Filtered {len(filtered_data)} records out of {len(data)}")
        print(f"Filtered data saved to: {output_file}")

        return filtered_data

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{input_file}'.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Usage
if __name__ == "__main__":
    input_filename = "dataset/raw_data.json"
    output_filename = "dataset/cleaned_data.json"

    filtered_records = filter_doctor_records_precise(input_filename, output_filename)

    if filtered_records:
        print("\nFiltered URLs with name, specialty, and location:")
        for record in filtered_records:
            print(f"{record['title']} | {record['specialty']} | {record['location']} -> {record['url']}")
