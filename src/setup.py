import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from requests import Request

# Authenticate and build the service
def auth_gsheet(sheet_access_key,
                scope = ['https://www.googleapis.com/auth/spreadsheets']):
    creds = Credentials.from_service_account_file(sheet_access_key, scopes=scope)
    service = build('sheets', 'v4', credentials=creds)
    return service


# Function to get all sheet names
def get_sheet_names(sheet_url, service):
    spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_url).execute()
    sheets = spreadsheet.get('sheets', [])
    return [sheet['properties']['title'] for sheet in sheets]


# Function to connect to a specific sheet and get data
def connect_to_sheet(sheet_name, sheet_url, service):
    range_name = f'{sheet_name}!A:Z'  # Adjust range as needed
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_url, range=range_name).execute()
    values = result.get('values', [])

    # if there are values and headers, create a DataFrame with the data
    if values and values[0]:
        headers = values[0]
        data = values[1:]
        if data:
            # Find the maximum number of columns across all data rows
            max_columns = max(len(row) for row in data) if data else len(headers)
            if max_columns > len(headers):
                # Extend headers with default names for extra columns
                extra_columns = max_columns - len(headers)
                default_headers = [f'column_{i + len(headers) + 1}' for i in range(extra_columns)]
                headers.extend(default_headers)
        df = pd.DataFrame(data, columns=headers)
        return df
    else:
        print(f'Skipping import of "{sheet_name}" sheet. Either invalid header or missing values.')
        return None

# Function to authenticate and load all sheets into a dictionary of DataFrames
def load_gsheet(sheet_url, sheet_access_key):
    service = auth_gsheet(sheet_access_key)
    sheet_names = get_sheet_names(sheet_url, service)
    data_dict = {}
    for sheet in sheet_names:
        df = connect_to_sheet(sheet, sheet_url, service)
        data_dict[sheet] = df
    return data_dict


def concatonate_entries(surf_data_dict):
    # Keep the sheets that have the data (i.e. labeled by the year)
    numeric_sheets = [sheet_name for sheet_name in surf_data_dict if sheet_name.isdigit()]

    # Create a list of dataframes from the dictionary, using only the numeric sheet names
    surf_data = [surf_data_dict[sheet_name] for sheet_name in numeric_sheets]

    # Concatenate the dataframes, even if they don't have the same columns
    df = pd.concat(surf_data, ignore_index=True)

    return df