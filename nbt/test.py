from nbt import tag

path = "/Users/3074018/Desktop/template.nbt"
path2 = "/Users/3074018/Desktop/template.snbt"

tag.load(path).savesnbt(path2)

