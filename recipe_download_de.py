from bs4 import BeautifulSoup,NavigableString
from recipe_info import recipe_info
from categories_download import get_categories_de
from requests import get
import re
import time
import os
import argparse
import pandas as pd
import argparse
import urllib.request, urllib.error, urllib.parse
def load_arg():
    parser = argparse.ArgumentParser(description='To resume download, default will download from scratch')
    parser.add_argument('-c','--category', type=str,
                               help='start category name')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
        args =  load_arg()
        category_start = args.category

        print('Remainder ------ ')
        print('Recipe step icon name is rounded by # ')
        print('Recipe image url is rounded by $ ')
        home_url = "https://www.rezeptwelt.de"

        categories_info_file = get_categories_de()
        categories_data = pd.read_csv(categories_info_file, index_col=0)
        dataset_columns = ['link','img link','rating','number vote','number favorite',
        	           'difficulty','cooking time','portion','preparation time','tips',
        	           'author','if tested','accessories','steps','ingredients','recipe created for',
        	           'machine addtional info','addtional categories','variation link','variation name']
        
        categories_indices = categories_data.index

        if(category_start != None):
            start_flag = False
        else:

            category_start = categories_indices[0]
            start_flag = True
            print("Download from the first category")

        if (not category_start in categories_indices) and (category_start != None):
            print(category_start, " is not a valid category name")
            print("valid category names are :")
            print(categories_data.index)
            exit(1)




        for category_index in categories_indices:
            if(category_index == category_start) or (start_flag):
                start_flag = True
            else:
                continue


            print('/*******************************/')
            print('Start Download Category '+ str(category_index))
            print('/*******************************/')
            #get item url
            category_url = categories_data['link'][category_index]

            #creat folders and init file name
            category_index = category_index.replace('/',' ')
            if not os.path.isdir(str(category_index)):
                print("create directory for ", str(category_index))
                os.mkdir(str(category_index))
            category_recipe_outfile = str(category_index) + '/'+str(category_index)+'.csv' 
            items_data = pd.DataFrame(columns=dataset_columns)


            category_response = get(category_url)
            category_html_soup = BeautifulSoup(category_response.text, 'html.parser')
            
            pager_container = category_html_soup.find('div',class_= 'pager')
            lastpage_extend = pager_container.a['href']
            pager_number = re.findall('[0-9]+', lastpage_extend)[0]
            pager_number = int(pager_number)
        
            for current_page in range(1,pager_number+1): 
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
                        print("downloading "+ recipe_class.recipe_name)
                        
                        #download html
                        html_path = str(category_index)
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
            print('Category '+ str(category_index)+' saved')
            print('/*******************************/')
            items_data.to_csv(category_recipe_outfile, index = True,sep=",")
            #finish current pager crawler

