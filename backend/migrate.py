import glob, os, re
files = []
for root, dirs, f in os.walk('d:/standbharat/backend/app'):
    for file in f:
        if file.endswith('.py'):
            files.append(os.path.join(root, file))

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    if 'class Config:' in content:
        content = re.sub(r'class Config:\s+orm_mode = True', r'model_config = ConfigDict(from_attributes=True)', content)
        content = re.sub(r'class Config:\s+from_attributes = True', r'model_config = ConfigDict(from_attributes=True)', content)
        content = re.sub(r'class Config:\s+env_file = ".env"', r'model_config = ConfigDict(env_file=".env")', content)
        if 'ConfigDict' in content and 'ConfigDict' not in content[:content.find('\nclass ')]:
            if 'from pydantic import ' in content:
                content = content.replace('from pydantic import ', 'from pydantic import ConfigDict, ', 1)
            else:
                content = 'from pydantic import ConfigDict\n' + content
        
    if original != content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filepath}")
