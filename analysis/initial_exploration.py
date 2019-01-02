from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time


def main():
    page_url = 'https://www.pollbludger.net/bludgertrack2019/polldata.htm?'
    driver = webdriver.Safari()
    driver.get(page_url)
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    table = soup.find('div', attrs={'class':'google-visualization-table'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    data = []
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele if ele else np.nan for ele in cols ]) # Get rid of empty values

    df = pd.DataFrame(data)
    df.columns = ['start_date', 'end_date', 'pollster', 'scope', 'sample', 'lnp', 'alp', 'grn', 'phon',
                     'nxt', 'lnp2pp', 'alp2pp', 'lnpra', 'alpra']
    df.to_csv('/Users/clinton/Documents/dev/elections/emma-chisit-2019/poll_bludger_national.csv', index=False)
    time.sleep(2)
    elem = driver.find_element_by_id('//*[@id="btvic"]')
    elem.click()
    time.sleep(2)
    elem.click()
    #
    #
    # soup = BeautifulSoup(driver.page_source, features="html.parser")
    # print soup
    driver.quit()


if __name__ == '__main__':
    main()
