import json
import requests
import time
from urlextract import URLExtract
import argparse

parser = argparse.ArgumentParser(description='Description of your program')
parser.add_argument('-u','--username', help='Username from CienciaVitae API', default= "USER")
parser.add_argument('-p','--password', help='Username from CienciaVitae API', default= "PASSWORD")
args = vars(parser.parse_args())

##Process input
username = args['username']
password = args['password']

headers = {'Accept': 'application/json'}

#import pdb;pdb.set_trace()

def extract_urls_method_1(data_json):
    """
    Extract the URLs from JSON (input)
    """
    urls = []
    
    if isinstance(data_json, dict):
        for key, value in data_json.items():
            #TODO check if we need the method startswith instead of ==
            if key == "url":
                urls.append(value)
            else:
                urls.extend(extract_urls_method_1(value))
    elif isinstance(data_json, list):
        for item in data_json:
            urls.extend(extract_urls_method_1(item))
    return urls

def extract_urls_method_2(text_json, list_urls):
    """
    Extract the URLs from JSON in TEXT (input)
    """     
    
    extractor = URLExtract()
    urls = extractor.find_urls(text_json)
    
    for url in urls:
        url = url.replace(",", "")
        if "http" in url:
            url = url[url.find('http'):]
        list_urls.append(url)
    
    return list_urls

def extract_urls(response_json, list_urls):    
    """
    Extract the URLs from diferent methods
    """ 

    #Extract URLs from JSON
    urls = extract_urls_method_1(response_json)

    #Merge two lists 
    list_urls = list_urls + urls

    #Remove the None from the list_urls
    list_urls = list(filter(lambda x: x is not None, list_urls))

    #Transform JSON in TEXT
    json_text = json.dumps(response_json)

    #Extract URLs from JSON in TEXT
    list_urls = extract_urls_method_2(json_text, list_urls)

    return list_urls

def get_urls_from_cienciavitaeCV(cienciavitaeID, list_urls):

    #Sleep to repect the limit of 2 request per second. It is 5 to be similar to the requests made by the crawlers
    time.sleep(5)

    try:
        #Get the information of the Curriculum from a given CienciaVitae ID
        url = "https://api.cienciavitae.pt/v1.1/curriculum/" + cienciavitaeID + "?lang=User%20defined"    
        response = requests.get(url, auth=(username, password), headers=headers)
        
        #Transform the response into JSON 
        response_json = response.json()

        #Call the extract_urls method
        list_urls = extract_urls(response_json, list_urls)
        
    except:
        print("Error get the Curriculum from the CienciaID: " + cienciavitaeID)

    return list_urls

def script():
    
    #Start the initial page
    page=1

    #Open file to store the output, i.e. the URLs extracted
    with open("output.txt", "w") as file:
        
        while True:

            #Sleep to repect the limit of 2 request per second. It is 5 to be similar to the requests made by the crawlers
            time.sleep(5)

            #It is just a list to put URLs and for every page the list is cleared
            list_urls = []

            #Sleep to repect the limit of 2 request per second
            url = "https://api.cienciavitae.pt/v1.1/searches/persons/all?order=Ascending&pagination=true&rows=20&page=" + str(page)
            response = requests.get(url, auth=(username, password), headers=headers)
            
            #Transform the response into JSON 
            response_json = response.json()

            #Call the extract_urls method
            list_urls = extract_urls(response_json, list_urls)
            
            try:
                
                #Get the list of persons
                list_persons = response_json['result']['person']
                
                for person in list_persons:
                    
                    #Get the list of all the author identifiers
                    list_author_identifier = person['author-identifiers']['author-identifier']
                    
                    for identifiers in list_author_identifier:
                        
                        #Get the ID from CienciaVitae
                        if identifiers['identifier-type']['code'] == "CIENCIAID":
                            
                            #ID from CienciaVitae
                            cienciavitaeID = identifiers['identifier']
                            
                            #Add CienciaVitae ID
                            list_urls.append("https://www.cienciavitae.pt/" + cienciavitaeID)

                            #Extract the URLs from the CienciaVitae Curriculum
                            list_urls = get_urls_from_cienciavitaeCV(cienciavitaeID, list_urls)

            except:
                print("Error get the CienciaID, page: " + page + " from the person " + person)

            #Stop condition
            if response_json['summary']['total'] == response_json['summary']['end']:
                break
            
            page += 1

            #Put all extracted URLS in a file
            for elem in list_urls:
                file.write(elem+"\n")

if __name__ == '__main__':
    script()