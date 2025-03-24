import json
import subprocess
import platform
import os
import shutil
from PIL import Image
from utils import convert_datestr_to_tuple, convert_date_to_str

class Modele:
    def __init__(self):
        self.list = {}

    
    def update_list(self):
        pass

    def open_folder(self):
        path = os.path.abspath("archives")
        if platform.system() == "Windows":
            subprocess.Popen(["explorer", path])
        else:
            try:
                subprocess.Popen(["nautilus", path])
            except FileNotFoundError:
                try:
                    subprocess.Popen(["nemo", path])
                except FileNotFoundError:
                    try:
                        subprocess.Popen(["dolphin", path])
                    except FileNotFoundError:
                        subprocess.Popen(["xdg-open", path])

    def get_list(self):
        self.refresh_json()

        with open("data.json", "r", encoding="utf-8") as f :
            data = json.load(f)
        
        return data

    def refresh_json(self):
        archives = os.listdir("archives")
        
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        for archive in archives:
            if archive not in data:
                data[archive] = {"path": os.path.join("archives", archive),
                                "description": "",
                                "date": ""}
        
        keys_to_delete = [key for key in data.keys() if key not in archives]
        
        for key in keys_to_delete:
            del data[key]
            
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def edit_archive(self, modifications:dict):
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)


        if modifications["old_name"] != modifications["name"]:
            del data[modifications["old_name"]]
            data[modifications["name"]] = {"path": "archives/" + modifications["name"],
                            "description": modifications["description"],
                            "date": modifications["date"]}
            
            os.rename(os.path.join("archives", modifications["old_name"]), os.path.join("archives", modifications["name"]))
            
        else:
            data[modifications["name"]]["description"] = modifications["description"]
            data[modifications["name"]]["date"] = modifications["date"]


        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    
    def open_archive(self, path:str):
        if path.endswith(("png", "jpg", "jpeg")):
            image = Image.open(path)
            image.show()
        else:
            if platform.system() == "Windows":
                os.startfile(path)
            else:
                subprocess.Popen(["xdg-open", path])

    def get_searched_list(self, prompt:str):
        with open("data.json", "r", encoding="utf-8") as f :
            data = json.load(f)

        if prompt:
            keys_to_delete = [archive for archive, infos in data.items() if prompt.lower() not in archive.lower() and prompt.lower() not in infos["description"].lower()]
            for key in keys_to_delete:
                del data[key]

        return data
    
    def get_sorted_list(self, sort_key:str, liste:dict|None=None):
        if liste is not None:
            data = liste
        else:
            with open("data.json", "r", encoding="utf-8") as f :
                data = json.load(f)

        if sort_key == "Trier par":
            return data

        elif sort_key == "Nom (alphabétique)":
            sorted_dict = dict(sorted(data.items()))
        
        elif sort_key == "Nom (antialphabétique)":
            sorted_dict = dict(sorted(data.items(), reverse=True))

        elif sort_key == "Date (du plus ancien)":
            sorted_dict = dict(sorted(data.items(), key=lambda item: convert_datestr_to_tuple(item[1]['date'])))
            
        elif sort_key == "Date (du plus récent)":
            sorted_dict = dict(sorted(data.items(), key=lambda item: convert_datestr_to_tuple(item[1]['date']), reverse=True))

        return sorted_dict
    
    def get_filtered_list(self, filters:dict, liste:dict|None=None):
        if liste is not None:
            data = liste
        else:
            with open("data.json", "r", encoding="utf-8") as f :
                data = json.load(f)

        if filters["pdf"] or filters["img"] or filters["other"] or filters["after"] != filters["before"]:
            filtered_dict = data

            if filters["after"] != filters["before"]:
                filtered_dict = dict(filter(lambda item: convert_datestr_to_tuple(item[1]["date"]) > convert_datestr_to_tuple(convert_date_to_str(filters["after"]))
                                                         and convert_datestr_to_tuple(item[1]["date"]) < convert_datestr_to_tuple(convert_date_to_str(filters["before"])),
                                            filtered_dict.items()))

            if filters["pdf"] and not filters["img"] and not filters["other"]:
                filtered_dict = dict(filter(lambda item: item[0].endswith("pdf"), filtered_dict.items()))
            elif filters["img"] and not filters["pdf"] and not filters["other"]:
                filtered_dict = dict(filter(lambda item: item[0].endswith(("png", "jpg", "jpeg")), filtered_dict.items()))
            elif filters["other"] and not filters["pdf"] and not filters["img"]:
                filtered_dict = dict(filter(lambda item: not item[0].endswith(("png", "jpg", "jpeg", "pdf")), filtered_dict.items()))
            elif filters["pdf"] and filters["img"] and not filters["other"]:
                filtered_dict = dict(filter(lambda item: item[0].endswith(("png", "jpg", "jpeg", "pdf")), filtered_dict.items()))
            elif filters["pdf"] and filters["other"] and not filters["img"]:
                filtered_dict = dict(filter(lambda item: not item[0].endswith(("png", "jpg", "jpeg")), filtered_dict.items()))
            elif filters["img"] and filters["other"] and not filters["pdf"]:
                filtered_dict = dict(filter(lambda item: not item[0].endswith("pdf"), filtered_dict.items()))
            else:
                return filtered_dict
            
            return filtered_dict
        return data
    
    def add_archive(self, infos:dict):
        dest = os.path.join("archives", infos["name"])
        shutil.copy(infos["src"], dest)

        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        data[infos["name"]] = {"path": dest,
                               "description": infos["description"],
                               "date": infos["date"]}
        
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            

    
if __name__ == "__main__":
    modele = Modele()
    modele.refresh_json()