import chardet


def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    result = chardet.detect(raw_data)
    return result['encoding']

if __name__ == '__main__':
    file_path = 'book/CET4_1.json'
    encoding = detect_encoding(file_path)
    print("File encoding:", encoding)
