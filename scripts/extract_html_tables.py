# extracts the html tables from chronicle's UDM list documentation

import requests
from bs4 import BeautifulSoup

def extract_tables_with_headings(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        tables_with_headings = []

        for table in soup.find_all('table'):
            heading = table.find_previous('h3')
            heading_text = heading.text if heading else None

            tables_with_headings.append({
                'heading': heading_text,
                'table': table
            })

        return tables_with_headings
    else:
        print(f"Failed to fetch HTML. Status code: {response.status_code}")
        return None

url = 'https://cloud.google.com/chronicle/docs/reference/udm-field-list'
result = extract_tables_with_headings(url)

if result:
    for idx, item in enumerate(result, start=1):
        heading = item['heading']
        table = item['table']

        # Print Heading in valid HTML format
        if heading:
            print(f"<h3>{heading}</h3>")

        # Print Table in valid HTML format
        print(table.prettify())

        print("\n" + "=" * 50 + "\n")