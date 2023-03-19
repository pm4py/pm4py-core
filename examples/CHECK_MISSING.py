import os


if __name__ == "__main__":
    files = [x.split(".")[0] for x in os.listdir(".") if x.endswith(".py") and not "execute_everything" in x and not "CHECK_MISSING" in x]
    contents_ex_everything = open("execute_everything.py", "r").read()
    for f in files:
        if f not in contents_ex_everything:
            print(f)
