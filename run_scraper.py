import os
import time

import requests
from bs4 import BeautifulSoup

from file_handlers import CSVHandler, ExcelHandler, TxtHandler, FileDownloader
import helpers_functions as helpers
from scraper_config import ScraperConfig as cfg
import scraper_meta as meta


class Scraper:
    def __init__(self):
        self.bs4 = BeautifulSoup
        self.file_downloader = FileDownloader
        self.csv = CSVHandler
        self.txt = TxtHandler
        self.excel = ExcelHandler

    def get_page_bs4_from_url(self, url):
        raw_html = self._get_page_source(url)
        return self.bs4(raw_html)

    def _get_page_source(self, url):
        try:
            req = requests.get(url)
        except Exception as e:
            print('unable to get {}. Reason - {}'.format(url, repr(e)))
            return False
        return req.text

    def _clear_bs4_from_attrs(self, bs4_soup):
        for tag in bs4_soup:
            for attribute in ["class", "id", "name", "style"]:
                try:
                    del tag[attribute]
                except:
                    continue
        return bs4_soup


class SemenaScraper(Scraper):
    def __init__(self):
        super().__init__()
        self.cfg = cfg()
        self.meta = meta
        self.product = Item
        self.products = []

    def fetch_products_from_excel_to_list_dicts(self, filename, columns_names_to_letters_dict):
        excel_file = self.excel(filename)
        excel_file.open_workbook()

        try:
            sheet = excel_file.wb[self.cfg.INPUT_SHEETNAME]
        except KeyError:
            print('there is no target sheet with name {}'.format(self.cfg.INPUT_SHEETNAME))
            return False

        cols_letters = columns_names_to_letters_dict
        urls_col = sheet[cols_letters['url']]
        for cell in urls_col:
            try:
                product = self.product()
                product['url'] = cell.hyperlink.target
            except AttributeError:
                continue

            row_num = cell.row
            product['full_name'] = sheet['{col}{row}'.format(col=cols_letters['name'], row=row_num)].value
            product['sku'] = sheet['{col}{row}'.format(col=cols_letters['sku'], row=row_num)].value
            product['amount'] = sheet['{col}{row}'.format(col=cols_letters['amount'], row=row_num)].value

            self.products.append(product.copy())
        return self.products

    def _parse_description_from_bs4(self, bs4_page):
        description = bs4_page.select_one(self.meta.CSS.description)
        description.select_one(self.meta.CSS.descr_first_line).replace_with('')
        description.select_one(self.meta.CSS.descr_last_line).replace_with('')
        description = self._clear_bs4_from_attrs(description)
        return description.text

    def enrich_product_data_from_bs4(self, product_item, page_bs4):
        product_item['description'] = self._parse_description_from_bs4(page_bs4)
        product_item['img_url'] = page_bs4.select_one(self.meta.CSS.img_url)['src']
        product_item['product_h1'] = page_bs4.select_one(self.meta.CSS.product_h1).text
        return product_item

    def _rename_file_to_product_name(self, raw_filename, product_name, dir='') -> str:
        """ rename files and return new file name. """
        raw_fname, ext = helpers.separate_name_extension(raw_filename)
        new_fname = helpers.translit(product_name.strip().replace(' ', '_'))
        new_filename = ''.join((new_fname, ext))

        old_filepath = os.path.join(dir, raw_filename)
        new_filepath = os.path.join(dir, new_filename)
        os.rename(old_filepath, new_filepath)
        return new_filename

    def rename_files_from_urls_to_products_names(self, urls_list, item_name, dir=''):
        new_img_names_list = []
        for ndx, img_url in enumerate(urls_list):
            raw_img_fname = helpers.split_filename_from_url(img_url)
            product_name = '{}-{}'.format(item_name, ndx)
            new_img_filename = self._rename_file_to_product_name(raw_img_fname, product_name, dir=dir)
            new_img_names_list.append(new_img_filename)
        return new_img_names_list


class Item(dict):
    def __init__(self):
        super().__init__()
        self['sku'] = ''
        self['full_name'] = ''
        self['url'] = ''
        self['category'] = ''
        self['description'] = ''
        self['amount'] = ''
        self['img_url'] = ''
        self['product_h1'] = ''
        self['new_img_filename'] = ''


def main():
    s = SemenaScraper()

    output_csv = s.csv(s.cfg.OUTPUT_CSV_FILE)
    output_csv.open_to_append_or_create()
    img_dir = s.cfg.IMG_DOWNLOAD_FOLDER
    img_saver = s.file_downloader()

    missed_urls_txt = s.txt(s.cfg.MISSED_URLS_TXT)
    missed_urls_txt.open_to_append_or_create()

    scraped_urls_txt = s.txt(s.cfg.SCRAPED_URLS_TXT)
    scraped_urls_txt.open_to_append_or_create()
    scraped_urls = scraped_urls_txt.read_data_to_list()

    products = s.fetch_products_from_excel_to_list_dicts(filename=s.cfg.INPUT_XLS_FILE,
                                                         columns_names_to_letters_dict=s.cfg.COLS)

    for product in products:
        if product['url'] in scraped_urls:
            continue
        page_bs4 = s.get_page_bs4_from_url(product['url'])
        try:
            product = s.enrich_product_data_from_bs4(product, page_bs4)
            img_urls_list = [product['img_url']]  # for this site it's only 1 img per product
            img_saver.download_files_from_urls_list(img_urls_list, img_dir)
        except Exception as e:
            print('{} missed. Reason - {}'.format(product['url'], repr(e)))
            missed_urls_txt.print_to_file(product['url'], mode='a')
            continue

        new_img_names_list = s.rename_files_from_urls_to_products_names(img_urls_list,
                                                                        product['product_h1'],
                                                                        dir=img_dir)
        product['new_img_filename'] = new_img_names_list[0]  # this project we need only the first img

        output_csv.add_row_from_dict(product)
        scraped_urls_txt.print_to_file(product['url'], mode='a')
        print('{} from {} scraped'.format(product['product_h1'], product['url']))

        time.sleep(s.cfg.PAUSE_TIME)


if __name__ == '__main__':
    main()
