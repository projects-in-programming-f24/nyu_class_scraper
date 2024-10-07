import requests
import json
import os
from dotenv import load_dotenv
from pymongo import MongoClient

def get_courses(subject_grouping_value, term_value, courses_collection):
    url = f'https://bulletins.nyu.edu/class-search/api/?page=fose&route=search&subject_grouping={subject_grouping_value}'

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    payload = json.dumps({
        "other": {"srcdb": term_value},
        "criteria": [{"field": "subject_grouping", "value": subject_grouping_value}]
    })

    # starting to make the API request
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            print(f"API Error: {data['error']}")
            return

        courses_list = data.get('results', [])
        if courses_list:
            print(f"Found {len(courses_list)} courses. Inserting into MongoDB...")
            courses_collection.insert_many(courses_list)
            print("Insertion complete.")
        else:
            print("No courses found.")

    except requests.RequestException as e:
        print(f"Error fetching courses: {e}")
    except Exception as e:
        print(f"Error inserting into MongoDB: {e}")

def get_subject_groupings():
    return {
        'Data Science': 'A4',
        'Economics': 'A51',
    }

# helper function to get the term code
def get_term_code(term_input):
    term_mapping = {
        'Fall 2024': '1248',
        'Spring 2025': '1252',
    }
    return term_mapping.get(term_input.strip())

def main():
    load_dotenv()
    MONGODB_URI = os.getenv('MONGODB_URI')

    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()  
    courses_collection = db['course']

    subject_groupings = get_subject_groupings()

    if not subject_groupings:
        print("No subject groupings found. Exiting.")
        return

    print("Available subject groupings:")
    for i, subject in enumerate(subject_groupings.keys(), 1):
        print(f"{i}. {subject}")

    while True:
        try:
            choice = int(input("\nEnter the number of the subject grouping you want to search: ")) - 1
            if 0 <= choice < len(subject_groupings):
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

    selected_subject = list(subject_groupings.keys())[choice]
    subject_grouping_value = subject_groupings[selected_subject]

    term_input = input("Enter the term (e.g., Fall 2024): ")
    term_value = get_term_code(term_input)

    if not term_value:
        print("Invalid term. Exiting.")
        return

    get_courses(subject_grouping_value, term_value, courses_collection)

if __name__ == "__main__":
    main()
