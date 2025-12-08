ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS