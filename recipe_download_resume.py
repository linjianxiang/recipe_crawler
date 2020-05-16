from bs4 import BeautifulSoup,NavigableString
from recipe_info import recipe_info
from categories_download import get_categories
from requests import get
import re
import time
import os
import argparse
import pandas as pd
import argparse
import urllib.request, urllib.error, urllib.parse

def load_arg():
    parser = argparse.ArgumentParser(description='To reume download files form a category')
    parser.add_argument('-c','--category', type=str,
                               help='category name')
    parser.add_argument('-p','--page', type=int,
                               help='page')

    args = parser.parse_args()
    return args



if __name__ == "__main__":
    
    #load arguments
    args = load_arg()
    category_resume = args.category
    page_resume = args.page

    print("category is ", args.category)
    print("page is ", str(args.page))

    print('Remainder ------ ')
    print('Recipe step icon name is rounded by # ')
    print('Recipe image url is rounded by $ ')
    home_url = "https://www.recipecommunity.com.au"
    
    categories_info_file = get_categories()
    categories_data = pd.read_csv(categories_info_file, index_col=0)
    dataset_columns = ['link','img link','rating','number vote','number favorite',
    	           'difficulty','cooking time','portion','preparation time',
    	           'author','if tested','accessories','steps','ingredients','recipe created for',
    	           'machine addtional info','addtional categories','variation link','variation name']
    
    
    categories_indices = categories_data.index
    if not category_resume in categories_indices:
        print(category_resume, " is not a valid category name")
        print("valid category names are :")
        print(categories_data.index)
        exit(1)

    print('/*******************************/')
    print('Resume Downloading Category '+ str(category_resume))
    print('/*******************************/')
    
    #creat folders and init file name
    if not os.path.isdir(str(category_resume)):
        print("create directory for ", str(category_resume))
        os.mkdir(str(category_resume))

    category_recipe_outfile = str(category_resume) + '/'+str(category_resume)+'.csv' 

    if os.path.isfile(category_recipe_outfile):
        recipe_index = pd.read_csv(category_recipe_outfile,index_col=0).index
    else:
        recipe_index = []


    items_data = pd.DataFrame(columns=dataset_columns)
    #get item url
    category_url = categories_data['link'][category_resume]
    category_response = get(category_url)
    category_html_soup = BeautifulSoup(category_response.text, 'html.parser')
    
    pager_container = category_html_soup.find('div',class_= 'pager')
    lastpage_extend = pager_container.a['href']
    pager_number = re.findall('[0-9]+', lastpage_extend)[0]
    pager_number = int(pager_number)
    
    for current_page in range(page_resume,pager_number+1): 
        page_url= category_url + '?page=' + str(current_page)
        print(page_url)
                        
        #download url contents and apply beautifulsoup
        item_response = get(page_url)
        item_html_soup = BeautifulSoup(item_response.text, 'html.parser')
        
        
        #find items on the first page
        items_container = item_html_soup.find_all('div', class_ = 'thumbnail result-recipe result-grid-display')
        
        for item in items_container:
    
            try:
                #init recipe class
                recipe_class = recipe_info(home_url)

                recipe_class.item_info_download(item)
                if recipe_class.recipe_name in recipe_index:
                    print(recipe_class.recipe_name, " exist")
                    continue

                print("downloading "+ recipe_class.recipe_name)
                
                #download html
                html_path = str(category_resume)
                recipe_class.download_html(html_path)
                
                  #process recipe url
                recipe_class.recipe_download_details()
                
                #create recipe data frame
                item_dic = recipe_class.create_data_frame()
                item_info = pd.DataFrame(item_dic,index=[recipe_class.recipe_name])
                items_data = items_data.append(item_info)
            except:
                log_file = open('error.log', 'a')
                log_file.write("Error occured!!! \n")
                log_file.write(recipe_class.recipe_url + '\n')
                log_file.close()
    
             
    print('/*******************************/')
    print('Category '+ str(category_resume)+' saved')
    print('/*******************************/')
    items_data.to_csv(category_recipe_outfile,mode='a', index = True,sep=",")
    #finish current pager crawler
    
