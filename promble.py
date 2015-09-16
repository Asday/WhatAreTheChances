from main import *
items = get_items([r"D:\bombs\8d954f7598e0e40221bc6c39c5396c5b"], range(65)).items

names = [item["name"] for item in items]

counts = [names.count(name) for name in names]

for _, count in enumerate(counts):
    items[_]["count"] = count

chances = [item for item in items if item["count"] == 2]
alchs = [item for item in items if item["count"] == 3]
chances.extend([item for item in items if item["count"] == 4])

chances.sort(key = lambda item: item["name"])
alchs.sort(key = lambda item: item["name"])

recipes = alchs + chances
#----------- subdivide
itemlist = recipes[:]
out = []
while itemlist:
    recipe = []
    item = itemlist.pop(0)
    recipe.append(item)
    while itemlist:
        if itemlist[0]["name"] == recipe[0]["name"]:
            item = itemlist.pop(0)
            recipe.append(item)
        else:
            break
    out.append(recipe)

for _ in out:
    assert len(set([item["name"] for item in _])) == 1

out.sort(key = key_sort_recipe_by_tab)

for _ in out:
    assert len(set([item["name"] for item in _])) == 1

#------------- fill_inventories

inventories = []
i = Inventory()
inventory = []
def tabname(item):
    try:
        i = str(int(item["_tab_label"])).zfill(3)
    except ValueError:
        i = item["_tab_label"]

    return i

for recipe in out:
    fits = True
    for item in recipe:
        if not i.place(item):
            fits = False
            break
    if not fits:
        inventory.sort(key = tabname)
        inventories.append(inventory)
        inventory = []
        i.clear()
    for item in recipe:
        if not fits:
            i.place(item)
        inventory.append(item)
if inventory:
    inventories.append(inventory)
