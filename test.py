str = "https://exhentai.org/g/1054581/243749340c/"
begin = len("https://exhentai.org/g/")
end = len(str)
param = str[begin:end].split('/')
print(param[0])
print(param[1])
