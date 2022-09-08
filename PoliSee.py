
key = ""

def get_secrets(filename: str):
    with open(filename) as file:
        return file.readline()

if __name__ == "__main__":
    key = get_secrets("./secrets.txt")
    print(key)