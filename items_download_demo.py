#!/usr/bin/env python
# coding: utf-8

# In[1]:


from categories_download import get_categories
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import os


# In[2]:


class recipe_info:
    def __init__(self):
        self.recipe_url = None
        self.recipe_img_link = None
        self.recipe_rating = None
        self.recipe_difficulty = None
        self.recipe_time = None
        self.recipe_author = None
        self.recipe_steps = None
        self.recipe_ingredients = None
    def item_info_download(self):
        return 'hello world'


# In[3]:


def item_info_download(item):
        #download author
        author_container = item.find_all('div',class_='item-author')[0]
        item_author = author_container.a.text
#         print(item_author)
        #download rating
        item_rating_container = item.find('div',class_ = 'item-rating clearfix')
        item_rating = item_rating_container.div['data-average']
#         print(item_rating)
        #download difficulty
        item_difficulty_container = item.find('div',class_ = 'col-xs-3 difficulty-inf')
        item_difficulty = item_difficulty_container.text.strip()
#         print(item_difficulty)
        #download cooking time
        item_time_container = item.find('div',class_ = 'col-xs-3 cooking-time-inf')
        item_time = item_time_container.text.strip()
#         print(item_time)
        #download name
        item_name = item.a['title']
#         print(item_name)
        #download image link
        item_img_link = item.img['src']
#         print(item_img_link)
        #download item url
        item_url_add = item.a['href']
        item_extend_url = home_url+item_url_add
#         print(item_extend_url)
        #create data frame
        item_dic = {}
        item_dic['link'] = item_extend_url
        item_dic['img link']= item_img_link
        item_dic['rating'] = item_rating
        item_dic['difficulty'] = item_difficulty
        item_dic['cooking time'] = item_time
        item_dic['author'] = item_author

        item_info = pd.DataFrame(item_dic,index=[item_name])
#         print(item_info)
        return item_name,item_extend_url,item_dic;


# In[4]:


home_url = "https://www.recipecommunity.com.au"
categories_info_file = get_categories()
categories_data = pd.read_csv(categories_info_file, index_col=0)


# In[6]:


categories_indices = categories_data.index
for category_index in categories_indices:
    #get item url
    item_url = categories_data['link'][category_index]
#     print(item_url)
    #download url contents and apply beautifulsoup
    item_response = get(item_url)
    item_html_soup = BeautifulSoup(item_response.text, 'html.parser')
    #find items on the first page
    items_container = item_html_soup.find_all('div', class_ = 'thumbnail result-recipe result-grid-display')
#     print(len(items_container))
    items_data = pd.DataFrame(columns=['link','img link','rating','difficulty','cooking time','author','steps','ingredients'])
    category_recipe_outfile = str(category_index)+'.csv'
    for item in items_container:
        item_name,recipe_url,item_dic = item_info_download(item)
        print("downloading "+ item_name)
        #process recipe url
        recipe_response = get(recipe_url)
        recipe_html_soup = BeautifulSoup(recipe_response.text, 'html.parser')
        #find recipe steps
        recipe_container = recipe_html_soup.find('ol', class_ = 'steps-list')
        step_list = recipe_container.find_all('li')
        #append steps to item dictionary
        steps = []
        for i in range(len(step_list)):
            steps.append(step_list[i].p.text)
        item_dic['steps'] = [steps]
#             item_dic['Step '+str(i)] = step_list[i].p.text
        #find ingredients
        ingredients_container = recipe_html_soup.find('div', class_ = 'ingredients')
#         print(type(ingredients_container))
        ingredient_list = ingredients_container.find_all('li')
        ingredients = []
        #append ingredients to dictionary
        for i in range(len(ingredient_list)):
             ingredients.append(" ".join(ingredient_list[i].text.split()))
        item_dic['ingredients'] = [ingredients]
        item_info = pd.DataFrame(item_dic,index=[item_name])
        items_data = items_data.append(item_info)

    items_data.to_csv(category_recipe_outfile, index = True,sep=",")
    # break


# In[7]:


# items_data

