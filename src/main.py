from data_access.google_sheet_render import GoogleSheetsReader

def main():
    reader = GoogleSheetsReader()

    df = reader.get_dataframe()
    
    print(df)

if __name__ == "__main__":
    main()