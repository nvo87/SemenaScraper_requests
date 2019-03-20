class ScraperConfig:
    INPUT_XLS_FILE = 'semena.xlsx'
    INPUT_SHEETNAME = 'ПРАЙС-ЛИСТ'
    COLS = {
        'sku': 'A',
        'name': 'B',
        'url': 'C',
        'amount': 'E'
    }

    IMG_DOWNLOAD_FOLDER = './result'
    OUTPUT_CSV_FILE = 'semena-scraped.csv'
    MISSED_URLS_TXT = 'missed_urls.txt'
    SCRAPED_URLS_TXT = 'scraped_urls.txt'

    PAUSE_TIME = 2  # sec
