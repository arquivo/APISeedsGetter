// Crawls scholar.tecnico.ulisboa.pt/api to get the list of units, researchers, records (aka publications) and/or files and saves them in CSV files.

import fetch from 'node-fetch';
import fs from 'fs';
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

// const requestTypes = ['units', 'researchers', 'records', 'files'];
const requestTypes = ['files'];
const baseApiUrl = 'https://scholar.tecnico.ulisboa.pt/api/'

const pageSize = 100; // Largest page size allowed by the API
const delayBetweenRequests = 5000 // Don't want to overload the API

const writeToFileErrorFunc = function (err) {
    if (err) {
        return console.error(err);
    }
}

const job = async function () {

    for (const requestType of requestTypes) {
        let currentPage = 0;
        let currentData = []
        let currentText='';
        let fileName = './'+requestType+'.csv'
    
        await fs.writeFile(fileName, "", writeToFileErrorFunc); // Makes sure that the file exists and that the file is empty

        let apiRequestType = requestType == 'files' ? 'records' : requestType;
        while (currentPage == 0 || currentData.length == pageSize) {
            const fetchUrl = baseApiUrl + apiRequestType + '?limit=' + pageSize + '&skip=' + (currentPage * pageSize)
            const response = await fetch(fetchUrl);
            currentData = await response.json();

            if(currentData.items === undefined){break;} // Makes sure this script doesn't break if totalItems is multiple of pageSize

            currentData = currentData.items;
			
			// Link para um PDF:
			// https://scholar.tecnico.ulisboa.pt/api/records/ RECORD-ID /file/ FILE-ID 
			//
			// A informação para construir o link vem dos pedidos com apiRequestType = "records" ( https://scholar.tecnico.ulisboa.pt/api/records )
			// Link só é válido se items[].files[].rights == "open-access"
			// RECORD-ID: items[].metadata.id
			// FILE-ID: items[].files[].id
			//
			// "items": [
			//   {
			//	   "metadata": { "id": "Record1" },
			//     "files": [
			//	     {
			//		   "id": "File1.pdf"
			//		   "rights": "open-access"
			//		 },{
			//		 {
			//		   "id": "File2.pdf"
			//		   "rights": "restricted-access"
			//		 }
			//	   ]
			//   },
			//   {
			//		...
			//   },
			//
			//	 ...
			//
			// ]

            let numberOfRetrievedDocs = currentData.length;
            switch (requestType) {
                case 'units':
                    currentText = currentData
                        .map(item => item.id) 
                        .map(i => 'https://scholar.tecnico.ulisboa.pt/units/'+i+'/records')
						.join('\n');
                    break;
                    
                case 'researchers':
                    currentText = currentData
                        .map(item => item.username)
                        .map(i => 'https://scholar.tecnico.ulisboa.pt/authors/'+i+'/records')
						.join('\n');
                    break;

                case 'records':
                    currentText = currentData
                        .map(item => item.metadata.id)
                        .map(i => 'https://scholar.tecnico.ulisboa.pt/records/'+i)
						.join('\n');
                        break;

                case 'files':
                    let files = [];
                    currentData.forEach(item => {
                        if (!!item.files && item.files.length > 0){
                            let recordid = item.metadata.id;
                            let currentFiles = item.files
                                .filter(file => file.rights == 'open-access')
                                .map(file => 'https://scholar.tecnico.ulisboa.pt/api/records/' + recordid + '/file/' + file.id);
                            files = [...files,...currentFiles];
                        }
                    })
                    currentText = files.join('\n');
                    numberOfRetrievedDocs = files.length;
                    break;
            
                default:
                    console.error('ERROR - Unknown request type "'+requestType+'"')
                    break;
            }
            if(currentText.length > 0){
                await fs.appendFile(fileName, (currentPage == 0 ? '' : '\n') + currentText, writeToFileErrorFunc);
            }
            console.log(fetchUrl + ' : ' + numberOfRetrievedDocs)
            await delay(delayBetweenRequests)
            currentPage += 1;
        }
    }
}

job();