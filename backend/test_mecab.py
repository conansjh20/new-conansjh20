import MeCab
tagger = MeCab.Tagger()
parsed = tagger.parse("本当の心")
with open("backend/test_mecab_output.txt", "w", encoding="utf-8") as f:
    f.write(parsed)
