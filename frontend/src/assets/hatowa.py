import MeCab

def hatowa_str(target:str=""):
    tagger = MeCab.Tagger()
    target = target
    # target = '正直君が許せなかった今は笑えるけど'
    parsed = tagger.parse(target)
    parsed = parsed.split("\n")
    res = []
    for idx, item in enumerate(parsed):
        try:
            if item.split("\t")[0] == "は":
                if "助詞-係助詞" in item.split("\t"):
                    res.append("$は")
                else:
                    res.append("は")
            else:
                res.append(item.split("\t")[0])
        except:
            pass

    res = "".join(res)
    # print(res[0:-3])

    return res[0:-3]

def hatowa_list(target:list=[]):
    tagger = MeCab.Tagger()
    target = target
    # target = ['正直君が許せなかった今は笑えるけど',"君と初めて出かけたのはこんな秋の日だった",]

    final = []

    for line in target:
        parsed = tagger.parse(line)
        parsed = parsed.split("\n")
        print(parsed)
        res = []
        for idx, item in enumerate(parsed):
            try:
                if item.split("\t")[0] == "は":
                    if "助詞-係助詞" in item.split("\t"):
                        res.append("$は")
                    else:
                        res.append("は")
                else:
                    res.append(item.split("\t")[0])
            except:
                pass
        res = "".join(res)[0:-3]
        final.append(res)
    # print(final)

    return final

# hatowa_list()
