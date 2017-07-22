INDEX = "wine_geo"
DOC_TYPE = "wine_type"
mapping = '''
{  
  "mappings":{  
    "wine_type":{  
      "properties":{  
        "ProductAttributes":{  
          "type":"nested"
        },
        "Labels":{  
          "type":"nested"
        },
        "Vintages.List":{  
          "type":"nested"
        },
        "Ratings.List":{  
          "type":"nested"
        },
        "Vineyard.Id":{
          "type":"keyword"
        },
        "Appellation.Id":{
          "type":"keyword"
        },
        "Id":{
          "type":"keyword"
        }
        "location":{
           "type":"geo_point 
        }
      }
    }
  }
}'''