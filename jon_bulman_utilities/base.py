import json
from datetime import datetime

class Jon_Bulman_Base:
    def to_dict(self):
        """Converts any child class instance into a JSON-serializable dict."""
        data = self.__dict__.copy()
        
        # Add the class name so we know how to "cast" it back later
        data["__type__"] = self.__class__.__name__
        
        # Handle datetime objects (JSON can't save them natively)
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

    def to_json(self):
        """Returns a JSON string of the object."""
        return json.dumps(self.to_dict(), indent=3)