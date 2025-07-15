

from src.setup import load_gsheet, pre_process_surf_data


def main():
    """
    Main function to read, process, and visualize my surf data.
    """

    # (1) SETUP -------------------------------------------------------------------
  
    # Path to your service account JSON file (allows access to google sheet)
    SERVICE_ACCOUNT_FILE = 'keys/surf-data-analysis-b31fc887181f.json'

    # Spreadsheet ID (from the URL of the Google Sheet)
    SPREADSHEET_ID = '1DvfcN09E9cHPDe83N89AJtZhk-4DhxkxGLi8UsaR0Mw'

    # (1) LOAD & PREPROCESS  -----------------------------------------------------------

    surf_data_dict = load_gsheet(SPREADSHEET_ID, SERVICE_ACCOUNT_FILE)
    surf_data_df_raw = pre_process_surf_data(surf_data_dict)

    # (2) PROCESS ---------------------------------------------------------

    
    # (3) PLOT ----------------------------------------------------------



if __name__ == "__main__":
    main()