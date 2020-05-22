from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import os

def get_categories():
    home_url = "https://www.recipecommunity.com.au"
    category_url = "https://www.recipecommunity.com.au/categories/"
    response = get(category_url)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    outfile = 'crawler_categories.csv'
    
    if os.path.isfile(outfile):
        return outfile

    #find all categories
    categories_container = html_soup.find_all('div', class_ = 'col-sm-6 col-md-4 sectionbox')
    categories_data = pd.DataFrame(columns=['link','img_link'])
    counter = 0
    for category in categories_container:
        #get the link of category image
        category_img_link = category.img['src']
        #get the name of the category
        category_name = category.h4.a.text
        #get the url for category
        category_link_add = category.a['href']
        category_extend_url = home_url+category_link_add
        #dictionary category
        category_dic = {'link': [category_extend_url],
           'img_link': [category_img_link]}
        category_info = pd.DataFrame(category_dic,index=[category_name])
        categories_data = categories_data.append(category_info)
        #save to csv
        categories_data.to_csv(r'crawler_categories.csv', index = True,sep=",")    
    print("/******************************/")
    print("finish categories info download")
    print("/******************************/")
    return (outfile)

def get_categories_de():
    home_url = "https://rezeptwelt.de"
    category_url = "https://rezeptwelt.de/kategorien"
    response = get(category_url)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    outfile = 'crawler_categories_de.csv'
    
    if os.path.isfile(outfile):
        return outfile

    #find all categories
    categories_container = html_soup.find_all('div', class_ = 'col-sm-6 col-md-4 sectionbox')
    categories_data = pd.DataFrame(columns=['link','img_link'])
    counter = 0
    for category in categories_container:
        #get the link of category image
        category_img_link = category.img['src']
        #get the name of the category
        category_name = category.h4.a.text
        #get the url for category
        category_link_add = category.a['href']
        category_extend_url = home_url+category_link_add
        #dictionary category
        category_dic = {'link': [category_extend_url],
           'img_link': [category_img_link]}
        category_info = pd.DataFrame(category_dic,index=[category_name])
        categories_data = categories_data.append(category_info)
        #save to csv
        categories_data.to_csv(outfile, index = True,sep=",")    
    print("/******************************/")
    print("finish de categories info download")
    print("/******************************/")
    return (outfile)

if __name__ == "__main__":
    #get_categories()
    get_categories_de()
