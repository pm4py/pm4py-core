import os
import networkx as nx
import requests as r
import time
import requests

def get_version(package):
	url = "https://pypi.org/project/"+package
	r = requests.get(url)
	res = r.text
	version = res.split("<p class=\"release__version\">")[1].split("</p>")[0].strip().split(" ")[0].strip()
	license = res.split("<p><strong>License:</strong>")[1].split("</p>")[0].strip()
	time.sleep(0.1)
	return package, url, version, license

os.system("pipdeptree -p pm4py >deps.txt")
F = open("deps.txt", "r")
content = F.readlines()
F.close()
G = nx.DiGraph()
i = 1
dep_level = {}
blocked = False
blocked_level = -1
while i < len(content):
    row = content[i].split("- ")
    level = round(len(row[0])/2)
    dep = row[1].split(" ")[0]
    if blocked and blocked_level == level:
        blocked = False
    if dep == "pm4pycvxopt":
        blocked = True
        blocked_level = level
    if not blocked:
        dep_level[level] = dep
        if level > 1:
            G.add_edge(dep_level[level-1], dep_level[level])
        else:
            G.add_node(dep_level[level])
    i = i + 1
edges = list(G.edges)
deps = []
while len(edges) > 0:
    left = set(x[0] for x in edges)
    right = set(x[1] for x in edges)
    diff = sorted([x for x in right if x not in left])
    for x in diff:
        if not x in deps:
            deps.append(x)
        G.remove_node(x)
    edges = list(G.edges)
nodes = sorted(list(G.nodes))
for x in nodes:
    if not x in deps:
        deps.append(x)
deps = sorted(deps, key=lambda x: x.lower())
packages = []
for x in deps:
	packages.append(get_version(x))
F = open("../dependencies_sheet.csv", "w")
F.write("package\turl\tversion\tlicense\n")
for x in packages:
	F.write("%s\t%s\t%s\t%s\n" % (x[0], x[1], x[2], x[3]))
F.close()
F = open("../requirements.txt", "w")
for x in packages:
	F.write("%s\n" % (x[0]))
F.close()
F = open("../requirements_stable.txt", "w")
for x in packages:
	F.write("%s==%s\n" % (x[0], x[2]))
F.close()
F = open("../README.THIRD_PARTY.md", "w")
F.write("""# PM4Py Third Party Dependencies

PM4Py depends on third party libraries to implement some
functionality. This document describes which libraries are depended
upon, and how. It is maintained by and for humans, and so while it is a
best effort attempt to describe the library's dependencies, it is subject
to change as libraries are added or removed.

| Name | URL | License | Version |
| --------------------------- | ------------------------------------------------------------ | --------------------------- | ------------------- |
""")
for x in packages:
	F.write("| %s | %s | %s | %s |\n" % (x[0], x[1], x[3], x[2]))
F.close()
os.remove("deps.txt")
