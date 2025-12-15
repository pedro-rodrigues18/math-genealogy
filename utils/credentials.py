def read_api_key():
    with open(".credentials.txt", "r") as file:
        return file.read().strip()
