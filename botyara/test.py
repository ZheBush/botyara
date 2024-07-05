import codecs
import json

file = codecs.open('./docs/areas.json', 'r', 'utf_8_sig')
data = json.loads(file.read())
print(data[2])