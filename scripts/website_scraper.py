import requests
from bs4 import BeautifulSoup
from xml.etree import ElementTree

from langchain_text_splitters import RecursiveCharacterTextSplitter

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from xml.etree import ElementTree

def get_urls():
    # URL of the sitemap
    sitemap_url = "https://abb-bank.az/sitemap.xml"

    # Create a session with retry logic
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        # Fetch the sitemap content with SSL verification disabled
        response = session.get(sitemap_url, verify=False)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the XML content
        sitemap_content = response.content
        root = ElementTree.fromstring(sitemap_content)

        # Extract the namespace from the root element
        namespace = {'ns': root.tag.split('}')[0].strip('{')}

        # Extract and filter URLs
        base_url = "https://abb-bank.az/az/ferdi/kreditler/"
        return [url.text for url in root.findall(".//ns:loc", namespaces=namespace) if url.text.startswith(base_url)]

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the sitemap: {e}")
        return []








def get_splitted_content():
    data = []
    urls  = get_urls()
    for url in urls:
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}
        response = requests.get(url , headers= headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            body_content = soup.find('body')
            
            # Remove the specific <header> with id "js-header" and the specified class because it contains unnecessary data 
            header = body_content.find('header', {'id': 'js-header'})
            if header:
                # Remove the <header> tag and its contents
                header.decompose()  

            # Extract all paragraphs and other elements from the body
            elements = body_content.find_all(['p', 'h1', 'h2', 'h3', 'ul', 'li'])
            
            page_content = ''
            
            # Concatenate all elements' text content, ensuring it is cleaned up
            for element in elements:
                text = element.get_text().strip() 
                page_content += text + ' '  # Add a space to separate text from different elements
            
            
            # Split the page content into chunks based on the defined text splitter. It will reduce number of tokens for API request to OPEN AI.
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, 
            chunk_overlap= 100, 
            separators=["\n\n","\n"," ", '\xa0']) 
            text_array =  text_splitter.split_text(text= page_content)
            for content in text_array :
                data.append(content)

        else:
           print(f"Failed to retrieve the page. Status code: {response.status_code}")
    
    
    return  data
    
