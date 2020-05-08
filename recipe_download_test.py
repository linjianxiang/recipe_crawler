from categories_download import get_categories
from requests import get
from bs4 import BeautifulSoup,NavigableString
import pandas as pd
import os
import re
import sys
import urllib.request, urllib.error, urllib.parse

class recipe_info:
    def __init__(self):
        self.recipe_name = None
        self.recipe_url = None
        self.recipe_img_link = None
        self.recipe_rating = None
        self.recipe_difficulty = None
        self.recipe_time = None
        self.preparation_time = None
        self.recipe_author = None
        self.recipe_steps = None
        self.recipe_ingredients = None
        self.recipe_portion = None
        self.recipe_accessories = None
        self.number_vote = None
        self.number_favorites = None
        self.variation_link = None
        self.variation_name = None
        self.machine_name = None
        self.machine_addtional_info = None
        self.addtional_categories_dic = None
        self.addtional_categories_name = None
        
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
        self.recipe_name = item.a['title'].replace('/','').replace(' ','')
#         print(item_name)
        #download image link
        self.recipe_img_link = item.img['src']
#         print(item_img_link)
        #download item url
        item_url_add = item.a['href']
        self.recipe_url = home_url+item_url_add
#         print(item_extend_url)
        
    def insert_icon_text(self, step):
        try:
            img_string = step.img
            operation = '#' + img_string['title'] + '#'
            step_icon = str(step).replace(str(img_string),operation)
            step_icon_soup = BeautifulSoup(step_icon,'html.parser')
            return step_icon_soup.text.strip().replace('\xa0',' ')
        except:
            step_image_url = step.img['src']
            return " ".join(step.text.split()) + "$" + step_image_url +"$"

    def download_recipe_steps_ingredients(self, step_list,ingredient_list):
        self.recipe_steps = []
        if len(step_list) == 1:
            try:
                self.recipe_steps.append(self.insert_icon_text(step_list[0]))
            except:
                step_list_container = step_list[0].find_all('p')
                if (len(step_list_container) > 1):
                    for step in step_list_container:
                        step_text = step.text.strip()
                        if step_text != '':
                            self.recipe_steps.append(step_text.replace('\xa0',' '))
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
            for i in range(len(step_list)):
                if (step_list[i].img != None):
                    self.recipe_steps.append(self.insert_icon_text(step_list[i]))
                else:
                    self.recipe_steps.append(" ".join(step_list[i].text.split()))
        
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
            self.variation_link = home_url+variations_container.a['href']
            self.variation_name = variations_container.a.text
        
        #find recipe steps list
        step_container = recipe_html_soup.find('ol', class_ = 'steps-list')
        step_list = step_container.find_all('li')

        #find ingredients list and portion
        ingredients_container = recipe_html_soup.find('div', class_ = 'ingredients')
        ingredient_list = ingredients_container.find_all('li')
        if (ingredients_container.find('p',class_='padding-bottom-10')):
            self.recipe_portion = ingredients_container.find('p',class_='padding-bottom-10').text.strip()

        #download if tested
        iftested_container = recipe_html_soup.find('span','recipe-testing-status-text')
        self.iftested = re.findall('\w+\stested', iftested_container.text)[0]

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
        
        #download addtional info
        self.download_addtional_info(recipe_html_soup)
      
    def download_addtional_info(self,recipe_html_soup):
        addtional_info_container = recipe_html_soup.find('div',class_= 'additional-info')
        addtion_info_list = addtional_info_container.find_all('li')
        #preparation time dowload
        time_container = addtion_info_list[0]
        preparation_time_container = time_container.find_all('div',class_='smallText')
        if (preparation_time_container):
            self.preparation_time = preparation_time_container[0].find("span", id="preparation-time-final").text.strip()
            #cooking method
            cooking_method = preparation_time_container[1].text.strip()
        #machine and machine addtional info
        machine_contianer = addtion_info_list[2]
        if (machine_contianer.h5 != None):
            self.machine_name = machine_contianer.h5.text
        self.machine_addtional_info = machine_contianer.find('div',class_="margin-top-10")
        if(self.machine_addtional_info!=None):
            self.machine_addtional_info = self.machine_addtional_info.text.strip()
        #addtional categroies
        if(len(addtion_info_list) >4):
            addtional_categories_container = addtion_info_list[4]
            addtional_categories_list =addtional_categories_container.find_all('a',class_='catText preventDefault')
            self.addtional_categories_dic ={}
            self.addtional_categories_name = []
            for category in addtional_categories_list:
                self.addtional_categories_name.append(category.text)
                self.addtional_categories_dic[category.text] = category['href']
        
    def create_data_frame(self):
        #create data frame
        item_dic = {}
        item_dic['link'] = self.recipe_url
        item_dic['img link']= self.recipe_img_link
        item_dic['rating'] = self.recipe_rating
        item_dic['number vote'] = self.number_vote
        item_dic['difficulty'] = self.recipe_difficulty
        item_dic['cooking time'] = self.recipe_time
        item_dic['preparation time'] = self.preparation_time
        item_dic['author'] = self.recipe_author
        item_dic['steps'] = [self.recipe_steps]
        item_dic['ingredients'] = [self.recipe_ingredients]
        item_dic['accessories'] = self.recipe_accessories
        item_dic['number favorite'] = self.number_favorites
        item_dic['variation link'] = self.variation_link
        item_dic['variation name'] = self.variation_name
        item_dic['portion'] = self.recipe_portion
        item_dic['recipe created for'] = self.machine_name
        item_dic['machine addtional info'] = self.machine_addtional_info
#         item_dic['addtional categories'] = self.addtional_categories_dic
        item_dic['addtional categories'] = [self.addtional_categories_name]
        item_dic['if tested'] = self.iftested
        
        return item_dic

    def download_html(self,path):   
        #save html to file
        response = urllib.request.urlopen(self.recipe_url)
        webContent = response.read()
        f = open(path+'/'+self.recipe_name+'.html', 'wb')
        f.write(webContent)
        f.close


if __name__ == "__main__":
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

        items_data = pd.DataFrame(columns=dataset_columns)
        page_url= "https://www.recipecommunity.com.au/categories/baking-sweet?page=18"
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










