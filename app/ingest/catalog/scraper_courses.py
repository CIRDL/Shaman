import requests
from bs4 import BeautifulSoup
import re
import pandas as pd


def fetch_html(url: str) -> BeautifulSoup:
    """Fetch HTML content from the given URL and return a BeautifulSoup object."""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        raise
    return BeautifulSoup(response.text, 'html.parser')


def extract_course_info(element) -> tuple:
    """
    Extract course information from a course block.

    Returns:
        A tuple of (class_code, class_name, credit_hours, prereq_codes)
        where prereq_codes is a list of prerequisite course codes.
    """
    # Extract header information
    header = element.find('strong')
    if not header:
        print("Warning: No header found in element.")
        return None

    header_text = header.text.strip()
    # Use regex to capture course code pattern allowing spaced letters
    match = re.search(r'([A-Z](?:\s*[A-Z])*\s*\d{3,4})', header_text)
    if not match:
        print(
            f"Warning: Failed to parse course code from header: '{header_text}'")
        return None
    raw_code = match.group(1)
    # Remove any spaces to standardize, e.g., "C S 5743" -> "CS5743"
    class_code = raw_code.replace(" ", "")

    # Remove the matched course code from header to extract the class name.
    # The header is expected to be in the form: "<course_code>.  <class_name>."
    class_name = header_text.replace(match.group(1), "")
    # Clean leading/trailing punctuation and whitespace; include period in removal
    class_name = class_name.lstrip(" .:-").rstrip(" .:-")
    if not class_name:
        print(f"Warning: No class name found in header: '{header_text}'")

    # Extract credit hours from the element with class 'credits'
    credits_elem = element.find(class_='credits')
    if credits_elem and credits_elem.text:
        credit_parts = credits_elem.text.strip().split()
        if credit_parts:
            credit_hours = credit_parts[0]
        else:
            print(
                f"Warning: Credits text found but empty tokens for {class_code}")
            credit_hours = None
    else:
        print(f"Warning: Missing credits element for course: {class_code}")
        credit_hours = None

    # Extract prerequisites from the course description (if present)
    prereq_codes = []
    desc_elem = element.find(class_='courseblockdesc')
    if desc_elem and desc_elem.text:
        # Extract text after "Prerequisite:" until the first period.
        match_prereq = re.search(r'Prerequisite:([^\.]*)\.', desc_elem.text)
        if match_prereq:
            prereq_text = match_prereq.group(1)
            # Use regex to capture course codes in the prereq text
            prereq_codes = re.findall(
                r'([A-Z](?:\s*[A-Z])*\s*\d{3,4})', prereq_text)
            # Standardize the codes by removing spaces
            prereq_codes = [code.replace(" ", "") for code in prereq_codes]
        else:
            print(f"Info: No prerequisites found for course: {class_code}")
    else:
        print(f"Info: No course description element for course: {class_code}")

    return class_code, class_name, credit_hours, prereq_codes


def scrape_department(url: str) -> tuple:
    """
    Scrape a department page to extract course and prerequisite data.

    Returns:
        - courses: A list of tuples (class_code, class_name, credit_hours)
        - prereqs: A list of tuples (class_code, parent_code)
    """
    soup = fetch_html(url)
    course_blocks = soup.find_all(class_='courseblock')

    courses = []
    prereqs = []

    for block in course_blocks:
        info = extract_course_info(block)
        if info is None:
            continue
        class_code, class_name, credit_hours, prereq_codes = info
        courses.append((class_code, class_name, credit_hours))
        # For each prerequisite, record the pair: (child course, prerequisite course)
        for parent in prereq_codes:
            prereqs.append((class_code, parent))

    return courses, prereqs


if __name__ == "__main__":
    # Define department URLs to scrape. You can expand this dictionary as needed.
    links = {
        'ise': 'https://ou-public.courseleaf.com/gallogly-engineering/industrial-systems-engineering/#coursestext',
        'cs': 'https://ou-public.courseleaf.com/gallogly-engineering/computer-science/#coursestext'
    }

    all_courses = []
    all_prereqs = []

    for dept, url in links.items():
        print(f"\nScraping department {dept} from {url} ...")
        courses, prereqs = scrape_department(url)
        all_courses.extend(courses)
        all_prereqs.extend(prereqs)

    # Build the two DataFrames:
    # classes_df holds (class_code, class_name, credit_hours)
    # prereqs_df holds (class_code, parent_code)
    classes_df = pd.DataFrame(all_courses, columns=[
                              'class_code', 'class_name', 'credit_hours'])
    prereqs_df = pd.DataFrame(all_prereqs, columns=[
                              'class_code', 'parent_code'])

    # Display the DataFrames for verification
    print("\nClasses DataFrame:")
    print(classes_df.tail(10))

    print("\nPrerequisites DataFrame:")
    print(prereqs_df.head(10))
