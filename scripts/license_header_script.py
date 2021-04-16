import glob

if __name__ == '__main__':
    LICENSE_HEADER_FILE_PATH = 'C:/Users/zelst/ownCloud/Process_Mining_FIT_shared/pm4py/scripts/LICENSE_HEADER_GITHUB.txt'
    with open(LICENSE_HEADER_FILE_PATH, 'r') as license_file:
        license = license_file.read()
        for filename in glob.iglob('../pm4py/' + '**/*.py', recursive=True):
            with open(filename, 'r') as original:
                data = original.read()
                if (data.find(license) == -1):
                    with open(filename, 'w') as modified:
                        print('adding license to: ' + filename)
                        modified.write(license + '\n' + data)
                else:
                    print('skipping: ' + filename)
