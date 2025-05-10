## How to Extract Tableau Dashboard Lineage Across Multiple Sites Using GraphQL and Python

## Why I Wrote This Guide

##### If you manage multiple Tableau sites and dashboards, you know how difficult it is to ##### track lineage — upstream tables, downstream views, and ##### data sources.

##### In this guide, I’ll show you how to automate lineage extraction across multiple Tableau sites using:

- Tableau Server Client (TSC)
- Tableau Metadata API (GraphQL)
- Python (with pandas)

##### By the end, you’ll be able to generate a complete lineage CSV from all your dashboards in minutes!

### Prerequisites
- Access to Tableau Server or Tableau Online with Admin or Creator role

- Metadata API must be enabled on your Tableau instance

- Python 3.x installed on your machine

## Step 1: Install Required Python Libraries
### Let’s first install all the libraries you’ll need.

`
pip install tableauserverclient pandas requests

`

##### If you don’t have re (regular expressions), don’t worry — it’s part of Python’s standard library.

## Step 2: Understand the Goal
#### Here’s what we’re trying to extract for every dashboard:

- Site Name

- Workbook Name

- View Names (dashboards/sheets)

- Datasource Names

## Upstream Tables (schema & database details)

## Step 3: Set Up Tableau Server Authentication
#### We’ll authenticate with Tableau using the tableauserverclient (TSC) library.

`
import tableauserverclient as TSC
import requests
import re
import pandas as pd

# Tableau Server Configuration
server_url = ""  # Example: "https://your-server.com"
username = ""    # Your Tableau username
password = ""    # Your Tableau password
site_content_url = ""  # For default site use "", otherwise "yoursitename"

`

## Step 4: List the Dashboard Names You Care About
#### If you want lineage for all dashboards, skip filtering. But if you want specific dashboards, list them here:

`
# List of dashboards to query
dashboard_names = ["DASHBOARD_1", "DASHBOARD_2"]

`

# Step 5: Normalize Names to Avoid Case & Special Character Mismatches

`
def normalize_name(name):
    return re.sub(r'[^A-Z0-9]', '', name.upper())

normalized_dashboard_names = [normalize_name(name) for name in dashboard_names]
`


# Step 6: Authenticate & Call Tableau Metadata API (GraphQL)

`

# Authenticate using TSC
tableau_auth = TSC.TableauAuth(username, password, site_content_url)
server = TSC.Server(server_url)
server.add_http_options({"verify": False})  # Skip SSL check (optional)

with server.auth.sign_in(tableau_auth):
    print("Signed in successfully!")

    access_token = server.auth_token
    GRAPHQL_URL = f"{server_url}/relationship-service-war/graphql"

    headers = {
        "X-Tableau-Auth": access_token,
        "Content-Type": "application/json"
    }

    # GraphQL query
    graphql_query = {
        "query": """
        {
            workbooks {
                id
                name
                embeddedDatasources {
                    id
                    name
                    upstreamTables {
                        id
                        name
                        schema
                        database {
                            name
                        }
                    }
                }
                views {
                    id
                    name
                }
            }
        }
        """
    }

    response = requests.post(GRAPHQL_URL, json=graphql_query, headers=headers, verify=False)
    metadata = response.json()
`

## Step 7: Parse and Extract Lineage Info

`
matched_workbooks = []

for workbook in metadata['data']['workbooks']:
    if workbook['name'] is None:
        continue

    normalized_workbook_name = normalize_name(workbook['name'])

    if normalized_workbook_name in normalized_dashboard_names:
        for view in workbook['views']:
            for datasource in workbook['embeddedDatasources']:
                for table in datasource['upstreamTables']:
                    source_table_name = f"{workbook['name']}.{view['name']}.{datasource['name']}"
                    matched_workbooks.append({
                        'Site Name': site_content_url,
                        'View Name': view['name'],
                        'Datasource Name': datasource['name'],
                        'Workbook Name': workbook['name'],
                        'Source Table Name': source_table_name
                    })

# Convert to DataFrame
df = pd.DataFrame(matched_workbooks).drop_duplicates(subset=['Workbook Name', 'Source Table Name'])
print(df)

`


## Step 8: Save Lineage to CSV

`
df.to_csv('tableau_dashboard_lineage.csv', index=False)
print("Lineage data saved to tableau_dashboard_lineage.csv")
`

## Step 9: Run It Across Multiple Sites (Optional)
#### To extract lineage across 3–4 sites:
#### Wrap the whole logic in a for site in sites_list loop.
#### Change site_content_url dynamically.

#### Bonus: What You Can Do Next
#### Automate this script to run daily/weekly.

#### Push lineage data to Snowflake or BigQuery for self-serve access.

#### Visualize lineage using Tableau itself!

## Common Errors & Fixes
| Error	| Fix |
|--------------|
|403 Forbidden | Make sure Metadata API is enabled.|
|Invalid Credentials | Double-check username, password, site URL.|
|SSL Certificate Error	| Use verify=False in requests.post().|


## Final Thoughts
#### With just a few lines of Python and GraphQL, you now have a scalable way to trace lineage across multiple Tableau sites and dashboards.

#### Want to make this even better? In future articles, I’ll show you:

#### How to get downstream lineage (dashboards → views → users)

#### How to map Tableau → Database column lineage


