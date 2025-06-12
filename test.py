import csv
import os
import tempfile
import app

def test_export_and_read_csv():
    # Sample data
    data = [
        {'Name': 'Alice', 'Age': 30, 'Country': 'USA'},
        {'Name': 'Bob', 'Age': 25, 'Country': 'Canada'}
    ]

    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
        filepath = tmp.name

    try:
        # Export data
        app.export_to_csv(data, filepath)

        # Read data back
        headings, rows = app.read_csv(filepath)

        # Convert back to list of dicts for easy comparison
        read_data = [dict(zip(headings, row)) for row in rows]

        # Convert all values to strings (CSV stores them as strings)
        expected = [{k: str(v) for k, v in d.items()} for d in data]

        assert read_data == expected, f"Mismatch:\nExpected: {expected}\nGot: {read_data}"
        print("✅ test_export_and_read_csv passed!")

    finally:
        os.remove(filepath)


def test_append_csv():
    initial_data = [
        ['Name', 'Age', 'Country'],
        ['Alice', '30', 'USA']
    ]
    new_data = [
        ['Bob', '25', 'Canada'],
        ['Charlie', '40', 'UK']
    ]

    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
        filepath = tmp.name

    try:
        # Write initial data
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(initial_data)

        # Append new data
        app.append_csv(filepath, new_data)

        # Read and check full contents
        with open(filepath, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            all_rows = list(reader)

        expected = initial_data + new_data
        assert all_rows == expected, f"Mismatch after append:\nExpected: {expected}\nGot: {all_rows}"
        print("✅ test_append_csv passed!")

    finally:
        os.remove(filepath)


if __name__ == '__main__':
    test_export_and_read_csv()
    test_append_csv()
