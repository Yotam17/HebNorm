import yaml
from pathlib import Path

def load_lists(path="rules/lists"):
    """
    Load all YAML files from the lists directory and merge all lists.
    
    Args:
        path: Path to the lists directory containing YAML files
        
    Returns:
        Dictionary with merged lists from all YAML files
    """
    lists_dir = Path(path)
    merged_lists = {}
    
    if not lists_dir.exists():
        print(f"⚠️  Warning: Lists directory '{path}' not found")
        return {}
    
    if not lists_dir.is_dir():
        print(f"⚠️  Warning: '{path}' is not a directory")
        return {}
    
    # Find all YAML files in the directory
    yaml_files = list(lists_dir.glob("*.yaml")) + list(lists_dir.glob("*.yml"))
    
    if not yaml_files:
        print(f"⚠️  Warning: No YAML files found in '{path}'")
        return {}
    
    print(f"📁 Loading lists from {len(yaml_files)} YAML files in '{path}'")
    
    for yaml_file in yaml_files:
        try:
            print(f"   📄 Loading: {yaml_file.name}")
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
            
            if data and isinstance(data, dict):
                for key, value in data.items():
                    if key not in merged_lists:
                        merged_lists[key] = set()
                    
                    if isinstance(value, list):
                        merged_lists[key].update(value)
                    elif isinstance(value, str):
                        merged_lists[key].add(value)
                    else:
                        print(f"      ⚠️  Skipping non-list value for key '{key}' in {yaml_file.name}")
                        
        except Exception as e:
            print(f"      ❌ Error loading {yaml_file.name}: {e}")
    
    # Convert sets back to lists for the final result
    result = {k: list(v) for k, v in merged_lists.items()}
    
    print(f"✅ Loaded {len(result)} lists with total items:")
    for key, items in result.items():
        print(f"   {key}: {len(items)} items")
    
    return result

# בזמן אתחול
lists_registry = load_lists()
ctx = Context("בגן החיות יש את היחמור", cur_index=3, lists_registry=lists_registry)
