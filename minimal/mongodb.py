from pymongo import MongoClient

client = MongoClient("mongodb+srv://brayo:EasyPass@brayos.gmypf.mongodb.net/spotify?retryWrites=true&w=majority")
db = client.spotify
spotify_db = db.urlpairs

def query_for_link(id:str)->str:
    result = spotify_db.find_one({"spotify_id":id})
    if result != None:
        link = result["yt_url"]
        if link != None:
            return link
    else:
        return ""

def insert_link_entry(id:str, yt_url:str):
    yt_url = yt_url[32:]
    spotify_db.find_one_and_update({"spotify_id":f"{id}"},{"$set":{"yt_url":yt_url}},upsert=True)


def unset_link_entry(id:str) -> bool:
    result = spotify_db.find_one_and_update({"spotify_id":f"{id}"}, {"$set":{"yt_url":""}})
    if result != None:
        return True
    return False

def insert_genius_link(id:str,genius_url:str) -> bool:
    if spotify_db.find_one({"spotify_id":f"{id}"}) != None:
        result = spotify_db.find_one_and_update({"spotify_id":f"{id}"},{"$set":{"genius_url":f"{genius_url}"}})
        # print(genius_url)
        if result != None:
            return True
    return False

def query_for_genius_link(id:str)->str:
    result = spotify_db.find_one({"spotify_id":id})
    if result != None:
        try:
            if result["genius_url"] != "None":
                return result["genius_url"]
        except:
            return "None"
    return "None"
def wrapper_for_findAny():
    result = spotify_db.find_one()
    return result

def drop_collection():
    spotify_db.drop()