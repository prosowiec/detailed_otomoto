import streamlit as st
import streamlit.components.v1 as components
import services
import pandas as pd
import os
st.set_page_config(layout="wide")



page =  st.sidebar.selectbox('Choose operation', ('Rate listings', 'Create new scraping file'))
filename_df = pd.read_csv('filenames.csv')
filename_df = filename_df['filename'].values.tolist()
index = 1

if page == 'Rate listings':
    cur_links =  st.sidebar.selectbox('Choose file name of links to be scraped', (filename_df))
    scraper = services.Scraper()
    scraper.filename = cur_links

    headers = ['link','saved']
    links_df = pd.read_csv(f'links/{cur_links}')

    if 'saved' not in links_df:
        links_df = links_df.assign(saved = 0)
        links_df.to_csv(f'links/{cur_links}', header=headers,index=None)

    links = links_df.iloc[:,0].values.tolist()
    saved = links_df.iloc[:,1].values.tolist()

    c1,c2 ,c3= st.columns([2,1,1])
    with c1:
        st.header('Rate listings from - '+ cur_links)
        
    with c3:
        index = st.number_input("Dataframe index",min_value=1,max_value=len(links),value=index)
        index -=1 

    if links_df.at[index,'saved'] == 1:
        new_title = '<p style="font-family:sans-serif; color:Green; font-size: 42px;">Data from this offer has been saved</p>'
        st.markdown(new_title, unsafe_allow_html=True)

    scraper.make_soup(links[index])
    scraper.make_parameters()
    st.image(scraper.get_imglist(),width=350)
    c1,c2,c3 = st.columns([2, 1,1])
    with c1:
        st.header('{} {}'.format(scraper.price , scraper.currency))
        components.html(html = scraper.param_table,width=770, height=700,scrolling = True)
    with c2:
        scraper.condition = st.number_input('Condition (0-2)',min_value=0, max_value=2, value=scraper.condition, step=1)
        scraper.equipment = st.number_input('Equipment (0-2)',min_value=0, max_value=2, value=scraper.equipment, step=1)
        scraper.make = st.text_input('Make',value=scraper.make)
        scraper.model = st.text_input('Model',value=scraper.model)
        scraper.year = st.number_input('Year',min_value=0, max_value = 2025, value=scraper.year, step=1)
        scraper.price = st.number_input('Price (PLN)',value=scraper.price, step=1)
        scraper.mileage = st.number_input('Mileage(km)',min_value=0, value=scraper.mileage, step=1000)
    with c3:
        scraper.eng_type = st.text_input('Engine type',value=scraper.eng_type)
        scraper.eng_cap = st.number_input('Engine capacity(cm3)',min_value=0,value=scraper.eng_cap, step=100)
        scraper.power = st.number_input('Power (hp)',min_value=0,value=scraper.power, step=1)
        scraper.gearbox = st.text_input('Gearbox',value=scraper.gearbox)
        scraper.body = st.text_input('Body type',value=scraper.body)
        scraper.origin = st.text_input('Origin',value=scraper.origin)
        scraper.transmission = st.text_input('Transmission',value=scraper.transmission)
        if st.button('Save'):
            links_df.at[index,'saved']= 1
            links_df.to_csv(f'links/{cur_links}', header=headers,index=None)
            scraper.load_df()

if page == 'Create new scraping file':
    st.header(page)
    link = services.Links()
    link.url =  st.text_input('Give Otomoto URL to scrape links from', )
    link.file_name = st.text_input('Set filename')
    if st.button('Submit'):
        with st.spinner('Wait for it...'):
            try:
                link.make_soup()
                link.scrape_links()
                st.header(f"Succes!! File has been {link.file_name} created in links folder.")
            except:
                st.header("Something went wrong :((")
            
