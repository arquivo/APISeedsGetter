import requests
import urllib.request
import os
import click
import json
import pandas as pd  
import random
import string
import argparse
import time

#Input
parser = argparse.ArgumentParser(description='Description of your program')
parser.add_argument('-p','--path', help='Localization of the processed files', default= "./Process/")
parser.add_argument('-d','--destination', help='Destination of the patching files merged', default= "./Output/")
args = vars(parser.parse_args())


def generate_random_string_pdf():
    """
    Generate a random string for the name of the PDF
    """
    
    # Define the length of the random string
    length = 15

    # Generate the random string
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    return random_string+".pdf"


def extract_urls_pdf(file_name, output_filename):
    """
    Extract the URLs from the pdf
    """

    #Waiting Time for each request
    time.sleep(2)

    #TODO - Getting a mechanism to catch errors from tikalinkextract-linux64 script
    #Beware of the file's permissions (tikalinkextract-linux64)
    os.system("./tikalinkextract-linux64 -seeds -file "+ file_name +" >> ./Output/" + output_filename)

    # Open the file in read mode
    with open('./Output/'+ output_filename, 'r') as file:
        # Read all lines from the file into a list
        lines = file.readlines()
        
    # Strip the newline characters from each line
    return [line.strip() for line in lines]

def main():
    """
    Main function
    Don't forget: You must have the tika server running (java -mx1000m -jar tika-server-1.20.jar --port=9998)
    """
    
    #Init variables
    mypath = args['path']
    destination = args['destination']

    #Create the folders if they do not exist
    if not os.path.exists(mypath):
        os.makedirs(mypath)
    if not os.path.exists(destination):
        os.makedirs(destination)

    #Start the dataframe that will log the process
    df = pd.DataFrame(columns=['ENTITY', 'PDF_URL', 'NAME_PDF', 'NAME_GENERATED', 'PAGE', 'NOTE' , 'URLS'])

    #Get the first page of the publications
    response = requests.get('https://www.rcaap.pt/api/v2/search/results/publications') #?publishedDate=2023')
    response_json = response.json()

    #Get the total pages
    totalPages = response_json['results']['page']['totalPages']

    #Init variable to iterate between the pages
    page = 0
    
    #Print the progress bar
    with click.progressbar(length=totalPages, show_pos=True) as progress_bar:
        
        #Process the pages until the totalPages
        while page < totalPages:

            #Update progress bar
            progress_bar.update(1)

            #Waiting Time for each request
            time.sleep(2)

            #Get the publications from each page
            res = requests.get('https://www.rcaap.pt/api/v2/search/results/publications?page='+str(page)) # +"&publishedDate=2023") 
            response = res.json()

            #Check if there is the parameter _embedded
            if "_embedded" in response['results']:

                #Get the list of entities
                entities = response['results']['_embedded']['entities']

                #For each entity
                for elem in entities:

                    #Init a dictionary
                    data_pandas = {}
                    
                    #Log the error
                    data_pandas['NOTE'] = ""
                    
                    #Boolean to check if there is an error 
                    have_response = True

                    #Get the document for each entity
                    document = elem['_links']['self']['href']

                    #Log the entity
                    data_pandas['ENTITY'] = document
                    
                    try:
                    
                        #Get the response from the entity
                        res = requests.get(document)
                        response = res.json()
                    
                    except:
                    
                        #Regardless of whether it is a get or json error I ca not proceed (Both errors have already happened).
                        #Log the Error
                        data_pandas['NOTE'] = 'Error! Get the entity ' + document
                        have_response = False
                    
                    #Check if the document have the field with the URL to download the PDF and if the boolean "have_response" is true
                    if have_response and "MediaObject" in response['fields'] and "MediaObject.contentUrl" in response['fields']['MediaObject'][0]['content']:

                        #Get the link of the PDF
                        pdf_url = response['fields']['MediaObject'][0]['content']['MediaObject.contentUrl']
                        
                        #Log the link of the pdf
                        data_pandas['PDF_URL'] = pdf_url

                        #Get the name of the file using the URL from RCAAP API
                        parsed_url = urllib.parse.urlsplit(pdf_url)
                        filename = os.path.basename(parsed_url.path)
                        decoded_filename = urllib.parse.unquote(filename)

                        #Log the name of the file
                        data_pandas['NAME_PDF'] = decoded_filename
                        
                        #Check if the file is a PDF
                        if decoded_filename.lower().endswith(".pdf"):
                            
                            #Generate a random name for the file
                            random_string = generate_random_string_pdf()

                            #Log the random name
                            data_pandas['NAME_GENERATED'] = random_string

                            ###################################
                            #This next segment can be improved
                            #Something cleaner than the cascade of try except
                            ###################################
                            
                            try:
                                
                                #Waiting Time for each request
                                time.sleep(2)

                                #After some tests this method is better than a requests.get
                                urllib.request.urlretrieve(pdf_url, random_string)

                            except Exception as e:

                                try:
                                    
                                    #One more try to download the file
                                    time.sleep(60)
                                    urllib.request.urlretrieve(pdf_url, random_string)
                                    
                                except Exception as e:    
                                    
                                    #Log the Error
                                    data_pandas['NOTE'] = data_pandas['NOTE'] + " / "+ 'Error! With urlretrieve -> Error Message: ' + str(e)

                                    try:

                                        #Waiting Time for each request
                                        time.sleep(2)
                                        
                                        #Last alternative to download the pdf
                                        response = requests.get(pdf_url)
                                        output_pdf = open(random_string, "wb")
                                        output_pdf.write_bytes(response.content)

                                    except Exception as e:
                                        
                                        #Log the Error
                                        data_pandas['NOTE'] = data_pandas['NOTE'] + " / "+ 'Error! With get -> Error Message: ' + str(e)

                            #If the file exists
                            if os.path.exists(random_string):

                                #Create a name for the output file
                                output_filename = random_string.replace(".pdf", ".txt")

                                #Extract the URLs from the PDF and save the result in the output file
                                urls_extracted = extract_urls_pdf(random_string, output_filename)

                                #Log the URLs extracted
                                data_pandas['URLS'] = urls_extracted
                            
                                #Instead of removing the file, we will store the file to have a debug in the future.
                                os.system("mv " + random_string + " ./Process/")

                            else:
                                #Log the Error
                                data_pandas['NOTE'] = data_pandas['NOTE'] + " / "+ 'Error! No PDF Download.'
                        else:
                            #Log the Error
                            data_pandas['NOTE'] = data_pandas['NOTE'] + " / "+ 'Error! The file do not end with .pdf'
                    else:
                        #Log the Error
                        data_pandas['NOTE'] = data_pandas['NOTE'] + " / "+ 'Error! No PDF in the RCAAP API result'
                    
                    #Log the page and save the dataframe in a csv
                    data_pandas['PAGE'] = page
                    df = df.append(data_pandas, ignore_index=True)
                    df.to_csv('Log_RCAAP_API.csv', sep=';', encoding='utf-8')
            
            else:
                #Log the problem with RCAAP API result
                dic = {'ENTITY' : "", 'PDF_URL' : "", 'NAME_PDF' : "", 'NAME_GENERATED' : "", 'PAGE' : page, 'NOTE' : "The parameter _embedded does not appears"}
                df = df.append(dic, ignore_index=True)
                df.to_csv('Log_RCAAP_API.csv', sep=';', encoding='utf-8')

            #Next page
            page +=1

if __name__ == "__main__":
    main()