# pywine

[Crawl](crawler.py) the wine catalogue from wine.com and ingest it in an elastic index. Any other storage tool would work as well but kibana is an awesome data visualization and exploration tool that is seamlessly integrated with elasticsearch.

# Exploring
The pictures below are kibana screenshots and display wine on sale at wine.com. The geo location is inferred using the [google geo decorator](decorator/google_geolocation_decorator.py). 

## Europe (excerpt)
![Wine regions in Europe](pictures/wine_regions_europe.PNG)
## Bordeaux region, France
![Wines from the Bordeaux region, France](pictures/wines_france_bordeaux.PNG)
## Germany
![Wines from Germany](pictures/wines_germany.PNG)
## Italy
![Wines from Italy](pictures/wines_italy.PNG)

# Requirements/Setup

## Data
The data is fetched from [wine.com](https://api.wine.com), so you will need an API key.

## Storage
The data is stored in an elastic index. This project uses [elasticsearch 5.5.0](https://www.elastic.co/de/downloads/elasticsearch), but any other (higher) version will do as well. 

## Visualization
For visualization and exploration, [kibana 5.5.0](https://www.elastic.co/de/downloads/kibana) is used. Again, any other (higher) version will do as well. 


# Other relevant data source
There are loads of other wine sellers. Unfortunately, not all do provide an API. 
One that does not seem to be too complicated to crawl is [Captain Cork](http://www.captaincork.com/entdecken).