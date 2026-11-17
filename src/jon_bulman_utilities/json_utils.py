import json

from typing import Any

def load_json(filepath: str, class_map: Any) -> list[Any]:
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return []

    # 1. If it's already a list, process each item
    if isinstance(data, list):
        processed_objects = []
        for item in data:
            class_str = item.pop("__type__", None)
            # Handle if class_map is a dict or a single class
            actual_class = class_map.get(class_str) if isinstance(class_map, dict) else class_map
            
            if actual_class:
                processed_objects.append(actual_class(**item))
            else:
                processed_objects.append(item)
        return processed_objects
    
    # 2. If it's a single dict, wrap the result in a list []
    else:
        class_str = data.pop("__type__", None)
        actual_class = class_map.get(class_str) if isinstance(class_map, dict) else class_map
        
        if actual_class:
            return [actual_class(**data)] # Wrapped in list
        return [data] # Wrapped in list

    
def Extract_values(obj, key):
	"""Pull all values of specified key from nested JSON."""
	arr = []
	def extract(obj, arr, key):        
		"""Recursively search for values of key in JSON tree."""
		if isinstance(obj, dict):
			v1 = 0 
			for k, v in obj.items():
				if isinstance(v, (dict, list)):
					extract(v, arr, key)
				elif k == key:
					v1 = v	
			arr.append(v1)
		elif isinstance(obj, list):
			for item in obj:
				extract(item, arr, key)
		return arr

	results = extract(obj, arr, key)
	return results
