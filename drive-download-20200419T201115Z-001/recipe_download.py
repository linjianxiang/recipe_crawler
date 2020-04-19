from categories_download import get_categories
from requests import get
from bs4 import BeautifulSoup,NavigableString
import pandas as pd
import os
import re
import pdfkit
import sys

class recipe_info:
    def __init__(self):
        self.recipe_name = None
        self.recipe_url = None
        self.recipe_img_link = None
        self.recipe_rating = None
        self.recipe_difficulty = None
        self.recipe_time = None
        self.recipe_author = None
        self.recipe_steps = None
        self.recipe_ingredients = None
        self.recipe_accessories = None
        self.number_vote = None
        self.number_favorites = None
        self.variation_link = None
        self.variation_name = None
        
    def item_info_download(self,item):
        #download author
        author_container = item.find_all('div',class_='item-author')[0]
        self.recipe_author = author_container.a.text
#         print(item_author)
        #download rating
        item_rating_container = item.find('div',class_ = 'item-rating clearfix')
        if (item_rating_container != None):
            self.recipe_rating = item_rating_container.div['data-average']
#             print(self.recipe_rating)
            #downloadd number of vote
            if (item_rating_container.span != None):
                vote_string = item_rating_container.span.text.strip()
                self.number_vote = re.findall('[0-9]+', vote_string)

        favourite_container = item.find('div',class_ = 'col-xs-2 favourite-inf')
        self.number_favorites = favourite_container.text.strip()
#         print(self.favorites)
        #download difficulty
        item_difficulty_container = item.find('div',class_ = 'col-xs-3 difficulty-inf')
        self.recipe_difficulty = item_difficulty_container.text.strip()
#         print(item_difficulty)
        #download cooking time
        item_time_container = item.find('div',class_ = 'col-xs-3 cooking-time-inf')
        self.recipe_time = item_time_container.text.strip()
#         print(item_time)
        #download name
        self.recipe_name = item.a['title']
#         print(item_name)
        #download image link
        self.recipe_img_link = item.img['src']
#         print(item_img_link)
        #download item url
        item_url_add = item.a['href']
        self.recipe_url = home_url+item_url_add
#         print(item_extend_url)
        

    def download_recipe_steps_ingredients(self, step_list,ingredient_list):
        self.recipe_steps = []
        if len(step_list) == 1:
            step_list_container = step_list[0].find_all('p')
            if (len(step_list_container) > 1):
                for step in step_list_container:
                    step_text = step.text.strip()
                    if step_text != '':
                        self.recipe_steps.append(step_text)
            elif(sum(1 for e in step_list[0].childGenerator())>4):
                for step in step_list[0].childGenerator():
                    if not (step and isinstance(step,NavigableString)):
                        continue
                    elif(str(step).strip() ==''):
                        continue
                    else:
                        self.recipe_steps.append(str(step).strip())
            else:
                self.recipe_steps.append(" ".join(step_list[0].text.split()))
        else:
#             try:
            for i in range(len(step_list)):
                self.recipe_steps.append(" ".join(step_list[i].text.split()))
#             except:
#                 for i in range(len(step_list)):
#                     self.recipe_steps.append(step_list[i].p.text)
        
        self.recipe_ingredients = []
        #append ingredients to dictionary
        for i in range(len(ingredient_list)):
             self.recipe_ingredients.append(" ".join(ingredient_list[i].text.split()))
        
    def recipe_download_details(self):
        recipe_response = get(self.recipe_url)
        recipe_html_soup = BeautifulSoup(recipe_response.text, 'html.parser')
        
        #download variations 
        variations_container = recipe_html_soup.find('div',class_= 'col-sm-12 sidebar-box variant-box')
        if (variations_container != None):
            self.variation_link = variations_container.a['href']
            self.variation_name = variations_container.a.text
        
        #find recipe steps list
        step_container = recipe_html_soup.find('ol', class_ = 'steps-list')
        step_list = step_container.find_all('li')

        #find ingredients list
        ingredients_container = recipe_html_soup.find('div', class_ = 'ingredients')
        ingredient_list = ingredients_container.find_all('li')
    
        #process recipe step and ingredient list
        self.download_recipe_steps_ingredients(step_list,ingredient_list)
        
        #accessories list download
        accessories_container = recipe_html_soup.find('div', class_ = 'accessories-list')
        if accessories_container == None:
            self.accessories = []
        else:
            tools_list = accessories_container.find_all("meta")
            accessories = []
            for tool in tools_list:
                accessories.append(tool.get("content"))
            self.recipe_accessories = [accessories]
            
    def create_data_frame(self):
        #create data frame
        item_dic = {}
        item_dic['link'] = self.recipe_url
        item_dic['img link']= self.recipe_img_link
        item_dic['rating'] = self.recipe_rating
        item_dic['number vote'] = self.number_vote
        item_dic['difficulty'] = self.recipe_difficulty
        item_dic['cooking time'] = self.recipe_time
        item_dic['author'] = self.recipe_author
        item_dic['steps'] = [self.recipe_steps]
        item_dic['ingredients'] = [self.recipe_ingredients]
        item_dic['accessories'] = self.recipe_accessories
        item_dic['number favorite'] = self.number_favorites
        item_dic['variation link'] = self.variation_link
        item_dic['variation name'] = self.variation_name
        
        return item_dic

if __name__ == "__main__":
	home_url = "https://www.recipecommunity.com.au"
	categories_info_file = get_categories()
	categories_data = pd.read_csv(categories_info_file, index_col=0)
	categories_indices = categories_data.index
	counter = 0
	for category_index in categories_indices:
		print('/*******************************/')
		print('Start Download Category '+ str(category_index))
		print('/*******************************/')
		#init 
		os.mkdir(str(category_index))
		category_recipe_outfile = str(category_index) + '/'+str(category_index)+'.csv' 
		items_data = pd.DataFrame(columns=['link','img link','rating','number vote',
					       'number favorite','variation link','variation name',
					       'difficulty','cooking time','author','accessories','steps','ingredients'])
		#get item url
		category_url = categories_data['link'][category_index]
		#     print(item_url)
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
		    #     print(len(items_container))

		    for item in items_container:
		        #init recipe class
		        recipe_class = recipe_info()
		        recipe_class.item_info_download(item)
		        print("downloading "+ recipe_class.recipe_name)

		    #         #process recipe url
		        recipe_class.recipe_download_details()

		        #create recipe data frame
		        item_dic = recipe_class.create_data_frame()
		        item_info = pd.DataFrame(item_dic,index=[recipe_class.recipe_name])
		        items_data = items_data.append(item_info)

		print('/*******************************/')
		print('Category '+ str(category_index)+' saved')
		print('/*******************************/')
		items_data.to_csv(category_recipe_outfile, index = True,sep=",")
		#finish current pager crawler
	#finish all pages








