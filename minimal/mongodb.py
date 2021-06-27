import pymongo

client = pymongo.MongoClient("mongodb+srv://brayo:EasyPass@brayos.gmypf.mongodb.net/spotify?retryWrites=true&w=majority")
db = client.spotify
spotify_db = db.urlpairs

def query_for_link(id:str)->str:
    result = spotify_db.find_one({"spotify_id":id})
    if result != None:
        return result["yt_url"]
    else:
        return ""

def insert_link_entry(id:str, yt_url:str):
    yt_url = yt_url[32:]
    if spotify_db.find_one({"spotify_id":f"{id}"}) != None:
        # print("already exists")
        return
    # print(f"inserted {yt_url}")
    json_document ={"spotify_id":f"{id}","yt_url": f"{yt_url}"}
    try:
        spotify_db.insert_one(json_document)
    except:
        pass

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