#!/usr/bin/env python
# coding: utf-8

# In[2]:


#bibliotecas que usaremos requests y bs4


# In[3]:


import requests


# In[4]:


#Guardamos nuestra url en una variable 
url = 'https://www.ellitoral.com/'


# In[5]:


#Ejecutamos un request inicial
litoral = requests.get(url)


# In[6]:


#Verificamos nuestro status_code
litoral.status_code


# In[7]:


#En este punto pudieramos ejecutar algunos comandos para ver el contenido de nuestra consulta
# .text / .content / .headers / .request.headers / .request.method / .request.url


# In[8]:


#Parseamos nuestro html con BeautifulSoup
from bs4 import BeautifulSoup


# In[9]:


lit = BeautifulSoup(litoral.text,'lxml')


# In[10]:


#Realizamos una primera impresion de nuestra consulta prettify
print(lit.prettify())


# In[11]:


lit.find('a')


# In[12]:


#Ubicamos las secciones principales que agrupan a las noticias
lit.find('div', attrs={'class':'styles_horizontal-scroll-wrapper__WkQo5'}).find_all('a')


# In[13]:


secciones = lit.find('div', attrs={'class':'styles_horizontal-scroll-wrapper__WkQo5'}).find_all('a')


# In[14]:


seccion= secciones[0]


# In[15]:


seccion


# In[16]:


secciones


# In[17]:


print(seccion['href'])


# In[18]:


links_secciones = [seccion.get('href') for seccion in secciones]


# In[19]:


links_secciones


# In[20]:


links_secciones = [seccion.get('href') if seccion.get('href').startswith('http') else 'https://www.ellitoral.com'+seccion.get('href') for seccion in secciones]


# In[21]:


links_secciones


# In[22]:


sec = requests.get(links_secciones[0])


# In[23]:


sec.status_code


# In[24]:


s_seccion = BeautifulSoup(sec.text, 'lxml')


# In[25]:


print(s_seccion.prettify())


# In[26]:


#Para acceder a los link lo hacemos de la siguiente forma: declaramos variable y ejecutamos find + atributos
featured_article = s_seccion.find('div', attrs={'class':'styles_temas-container__2moeC'})
featured_article


# In[27]:


featured_article.a.get('href')


# In[28]:


def obtener_notas(soup):
    lista_notas=[]
    featured_article = soup.find('div', attrs={'class':'styles_temas-container__2moeC'})
    if featured_article:
        for a in featured_article.find_all('a'):
            href = a.get('href')
            href_with_prefix = "https://www.ellitoral.com/" + href.replace('/', '', 1)
            lista_notas.append(href_with_prefix)

    # Agregar el prefijo en caso de que no se haya agregado en el bucle anterior
    for i in range(len(lista_notas)):
        if not lista_notas[i].startswith('https://www.ellitoral.com/'):
            lista_notas[i] = 'https://www.ellitoral.com/' + lista_notas[i]

    return lista_notas


# In[29]:


lista_notas = obtener_notas(s_seccion)
lista_notas


# In[30]:


url_nota = lista_notas[0]


# In[31]:


url_nota


# In[32]:


# Escritura del Scrapper
# Encapsulamos el codigo en un bloque Try - Except
# El .get('datetime') nos permite acceder al elemento que nos interesa del span

try:
    nota = requests.get(url_nota)
    if nota.status_code == 200:
        s_nota = BeautifulSoup(nota.text, 'lxml')
    #Extraemos el título
    titulo = s_nota.find('h1', attrs={'class':'headline-text'})
    print(titulo.text)
    #Extraemos la volanta
    volanta = s_nota.find('div', attrs ={'class':'styles_volanta-text__rE4Lf'})
    print(volanta.get_text())
    #Extraemos la cuerpo de la nota
    cuerpos = s_nota.find_all('div', attrs={'class':'custom-text text-content styles_paragraph-detail__iq2ji styles_lila-links__fmg8W styles_note-styles__iXm81'})
    for cuerpo in cuerpos:
        print(cuerpo.get_text())

except Exception as e: 
    print('Error:')
    print(e)
    print('\n')

# como reto de la clase extraer el copete, la volanta y el autor de la noticia


# In[33]:


# Codigo para automatizar mediante un bloque de codigo la ejecucion del scrapper

def obtener_info(s_nota):
    #Creamos un diccionario vacio para poblarlo con la información
    ret_dict ={}


    #Extraemos el título
    titulo = s_nota.find('h1', attrs={'class':'headline-text'})
    if titulo:
        ret_dict['titulo'] = titulo.text
    else:
        ret_dict['titulo'] = None 

    #Extraemos la volanta
    volanta = s_nota.find('div', attrs ={'class':'styles_volanta-text__rE4Lf'})
    if volanta:
        ret_dict['volanta'] = volanta.get_text()
    else:
        ret_dict['volanta'] = None
             
    #Extraemos el cuerpo de la nota
    cuerpos = s_nota.find_all('div', attrs={'class':'custom-text text-content styles_paragraph-detail__iq2ji styles_lila-links__fmg8W styles_note-styles__iXm81'})
    for cuerpo in cuerpos:
        if cuerpo:
            ret_dict['texto'] = cuerpo.get_text()
        else:
            ret_dict['texto'] = None
    
    return ret_dict            


# In[34]:


#Encapsular el Scrapper en un función

def scrape_nota(url):
    try:
        nota = requests.get(url)
    except Exception as e:
        print('Error scrapeando URL', url)
        print(e)
        return None
    
    if nota.status_code !=200:
        print(f'Error obteniendo nota{url}')
        print(f'status Code ={nota.status_code}')
        return None
    
    s_nota = BeautifulSoup(nota.text, 'lxml')
    
    ret_dict = obtener_info(s_nota)
    ret_dict['url'] = url
    
    return ret_dict


# In[35]:


scrape_nota(url_nota)


# In[36]:


links_secciones


# In[37]:


notas = []
for link in links_secciones:
    try:
        r = requests.get(link)
        if r.status_code ==200:
            soup = BeautifulSoup(r.text, 'lxml')
            notas.extend(obtener_notas(soup))
        else:
            print('No se pudo obtener la seccion', link)
    except:
        print('No se pudo obtener la seccion', link)


# In[38]:


notas


# In[39]:


data =[]
for i, nota in enumerate(notas):
    print(f'Scrapeando nota{i}/{len(notas)}')
    data.append(scrape_nota(nota))


# In[40]:


len(data)


# In[41]:


#importamos la libreria de pandas para enviar toda la info que sacamos a un DataFrame

import pandas as pd


# In[42]:


df = pd.DataFrame(data)


# In[43]:


df.head()


# In[ ]:


import csv


# In[47]:


df.to_excel('archivo_excel.xlsx', index=False)


# In[46]:


data = df

with open('archivo.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    
    for row in data:
        writer.writerow(row)


# In[45]:





# In[ ]:




