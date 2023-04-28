# APISeedsGetter
The repository consists of a set of scripts used to extract data from APIs.

## CienciaVitae API
The information we want to extract from CienciaVitae API:
- The CienciaVitae ID e.g. 851A-7C31-0327
- URLs from the each CienciaVitae ID

Basic steps to get the information that Arquivo.pt wants from CienciaVitae API:

1. Get all CienciaVitae IDs using the endpoint “persons all” (https://api.cienciavitae.pt/v1.1/searches/persons/all)
2. For each ID from 1, we need to get all the publications (https://api.cienciavitae.pt/v1.1/curriculum/CIENCIAVITAE_ID?lang=User%20defined)
3. Extract the information

### Parameters

<pre>
-u or --username     --> Username from CienciaVitae API
-p or --password     --> Password from CienciaVitae API
</pre>

### Run

```
python process_api_cienciaviate.py -u USERNAME - p PASSWORD
```

## RCAAP API
The information we want to extract from RCAAP API:
- Links to the PDFs
- All the citations from each PDF

Basic steps to get the information that Arquivo.pt wants from CienciaVitae API:
1. Get the publications (e.g. https://www.rcaap.pt/api/v2/search/results/publications)
2. For each publication we need to get the entity (e.g. https://www.rcaap.pt/api/v2/entity/a230c2cf-c84f-46e6-9ebc-cc722e9ef0fa)
3. For each entity we need to get the URL to the PDF
4. Extract the information

### Parameters

<pre>
-p or --path          --> Localization of the processed files
-d or --destination   --> Destination of the output files
</pre>

### Setup
Run in a different shell

```
java -mx1000m -jar tika-server-1.20.jar --port=9998
```

### Run

```
python rcaap_api.py
```
