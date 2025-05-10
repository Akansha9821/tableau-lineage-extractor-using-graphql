import tableauserverclient as TSC

import requests

import re

import pandas as pd

 

# Tableau Server Configuration

server_url = ""

username = ""

password = ""

site_content_url = ""

 

# List of dashboard names to query

# dashboard_names = ["MEMBERSHIP_ALLTIME_MEMSCI_TIER3KPIS_GEO_PROD", "MGS DATA DICTIONARY", "MGS DATA DOWNLOAD", "MGS DATA DOWNLOAD BY GEO & STORE", "MGS DATA DOWNLOAD BY GEO & STORE", "MGS DATA DOWNLOAD BY GEO & STORE QA", "MGS GLOBAL SCORECARD_KOP", "MGSSCORECARD_PROD"]

dashboard_names = ["", ""]

# Function to normalize names by removing special characters and converting to uppercase

def normalize_name(name):

    return re.sub(r'[^A-Z0-9]', '', name.upper())

 

# Normalize dashboard names

normalized_dashboard_names = [normalize_name(name) for name in dashboard_names]

 

# Authenticate using TSC

tableau_auth = TSC.TableauAuth(username, password, site_content_url)

server = TSC.Server(server_url)

server.add_http_options({"verify": False})

 

with server.auth.sign_in(tableau_auth):

    print("Signed in successfully!")

 

    # Access token for GraphQL

    access_token = server.auth_token

    GRAPHQL_URL = f"{server_url}/relationship-service-war/graphql"

    headers = {

        "X-Tableau-Auth": access_token,

        "Content-Type": "application/json"

    }

 

    # GraphQL query to get all workbooks

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

 

    # Call Metadata API

    response = requests.post(GRAPHQL_URL, json=graphql_query, headers=headers, verify=False)

    metadata = response.json()

    # print("API Response:", metadata)  # Debugging statement to print the API response

 

    # Extract workbook IDs for matching dashboard names

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

 

    # Create a DataFrame from the matched workbooks

    df = pd.DataFrame(matched_workbooks).drop_duplicates(subset=['Workbook Name', 'Source Table Name'])

    print(df)

    # Save the DataFrame to a CSV file

    # df.to_csv('Consumer_Insights_matched_workbooks.csv', index=False)

 