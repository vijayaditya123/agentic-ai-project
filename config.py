import json
from dataclasses import dataclass
from pathlib import Path

def load_setting(file_path=Path(__file__).parent / "appsettings.json"):
    with open(file_path,"r") as file:
        setting = json.load(file)
    return  setting

Settings= load_setting()


@dataclass
class  Database: 
   db_host : str
   db_port : int
   db_name : str
   db_user  : str
   db_password : str
   db_read_user : str
   db_read_password : str

settings=  Database(db_host= Settings["Database"]["Host"],
    db_port=Settings["Database"]["Port"],
    db_name=Settings["Database"]["Name"],
    db_user=Settings["Database"]["User"],
    db_password=Settings["Database"]["Password"],
    db_read_user =Settings["Database"]["ReadOnlyUser"],
    db_read_password=Settings["Database"]["ReadOnlyPassword"]
    )

@dataclass
class aws_credential:
    model_id:str
    region: str

credential=aws_credential(model_id = Settings["aws"]["model_id"] ,
    region=  Settings["aws"]["region"])
