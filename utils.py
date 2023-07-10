import hashlib

def generate_unique_identifier(uploaded_file):
    """
    Generate unique identifier for a file based on its hash to check for duplicates
    """
    # Make sure the pointer of the file is on te beginning 
    uploaded_file.seek(0)
    content = uploaded_file.read()
    return hashlib.md5(content).hexdigest()
