import re
import MeCab
import jaconv
from deep_translator import GoogleTranslator
import eng_to_ipa as ipa
from phonetic_learning import phonetic
jap_one_syl = ["あ", "か", "さ", "た", "な", "は", "ま", "や", "ら", "わ", "が", "ざ", "だ", "ば", "ぱ",
               "い", "き", "し", "ち", "に", "ひ", "み", "り", "ぎ", "じ", "ぢ", "び", "ぴ",
               "う", "く", "す", "つ", "ぬ", "ふ", "む", "ゆ", "る", "ぐ", "ず", "づ", "ぶ", "ぷ",
               "え", "け", "せ", "て", "ね", "へ", "め", "れ", "げ", "ぜ", "で", "べ", "ぺ",
               "お", "こ", "そ", "と", "の", "ほ", "も", "よ", "ろ", "ご", "ぞ", "ど", "ぼ", "ぽ", "を", " ", "ゔ", "っ", "ー"]
jap_two_syl = ["きゃ", "しゃ", "ちゃ", "にゃ", "ひゃ", "みゃ", "りゃ", "ぎゃ", "じゃ", "びゃ", "ぴゃ",
               "きゅ", "しゅ", "ちゅ", "にゅ", "ひゅ", "みゅ", "りゅ", "ぎゅ", "じゅ", "びゅ", "ぴゅ",
               "きょ", "しょ", "ちょ", "にょ", "ひょ", "みょ", "りょ", "ぎょ", "じょ", "びょ", "ぴょ",
               "あっ", "かっ", "さっ", "たっ", "なっ", "はっ", "まっ", "やっ", "らっ", "わっ", "がっ", "ざっ", "だっ", "ばっ", "ぱっ",
               "いっ", "きっ", "しっ", "ちっ", "にっ", "ひっ", "みっ", "りっ", "ぎっ", "じっ", "ぢっ", "びっ", "ぴっ",
               "うっ", "くっ", "すっ", "つっ", "ぬっ", "ふっ", "むっ", "ゆっ", "るっ", "ぐっ", "ずっ", "づっ", "ぶっ", "ぷっ",
               "えっ", "けっ", "せっ", "てっ", "ねっ", "へっ", "めっ", "れっ", "げっ", "ぜっ", "でっ", "べっ", "ぺっ",
               "おっ", "こっ", "そっ", "とっ", "のっ", "ほっ", "もっ", "よっ", "ろっ", "ごっ", "ぞっ", "どっ", "ぼっ", "ぽっ",
               "あん", "かん", "さん", "たん", "なん", "はん", "まん", "やん", "らん", "わん", "がん", "ざん", "だん", "ばん", "ぱん",
               "いん", "きん", "しん", "ちん", "にん", "ひん", "みん", "りん", "ぎん", "じん", "ぢん", "びん", "ぴん",
               "うん", "くん", "すん", "つん", "ぬん", "ふん", "むん", "ゆん", "るん", "ぐん", "ずん", "づん", "ぶん", "ぷん",
               "えん", "けん", "せん", "てん", "ねん", "へん", "めん", "れん", "げん", "ぜん", "でん", "べん", "ぺん",
               "おん", "こん", "そん", "とん", "のん", "ほん", "もん", "よん", "ろん", "ごん", "ぞん", "どん", "ぼん", "ぽん",
               "しぇ", "ふぁ", "ふぃ", "ふぇ", "ふぉ", "うぃ", "うぇ", "うぉ", "つぁ", "つぃ", "つぇ", "つぉ",
               "ちぇ", "くぁ", "くぃ", "くぇ", "くぉ", "とぅ", "でゅ",
               "ゔぁ", "まぁ",
               "でぃ", "ねぇ", "なぁ", "$は", "あぁ", "ふぃ", "じぇ", "とぅ", "てぃ", "ふぇ", "わっ", "ぁっ"]
jap_three_syl = ["きゃっ", "しゃっ", "ちゃっ", "にゃっ", "ひゃっ", "みゃっ", "りゃっ", "ぎゃっ", "じゃっ", "びゃっ", "ぴゃっ",
                 "きゅっ", "しゅっ", "ちゅっ", "にゅっ", "ひゅっ", "みゅっ", "りゅっ", "ぎゅっ", "じゅっ", "びゅっ", "ぴゅっ",
                 "きょっ", "しょっ", "ちょっ", "にょっ", "ひょっ", "みょっ", "りょっ", "ぎょっ", "じょっ", "びょっ", "ぴょっ",
                 "きゃん", "しゃん", "ちゃん", "にゃん", "ひゃん", "みゃん", "りゃん", "ぎゃん", "じゃん", "びゃん", "ぴゃん",
                 "きゅん", "しゅん", "ちゅん", "にゅん", "ひゅん", "みゅん", "りゅん", "ぎゅん", "じゅん", "びゅん", "ぴゅん",
                 "きょん", "しょん", "ちょん", "にょん", "ひょん", "みょん", "りょん", "ぎょん", "じょん", "びょん", "ぴょん"]

kor_one_syl = ["아", "카", "사", "타", "나", "하", "마", "야", "라", "와", "가", "자", "다", "바", "파",
               "이", "키", "시", "찌", "니", "히", "미", "리", "기", "지", "지", "비", "피",
               "우", "쿠", "스", "쯔", "누", "후", "무", "유", "루", "구", "즈", "즈", "부", "푸",
               "에", "케", "세", "테", "네", "헤", "메", "레", "게", "제", "데", "베", "페",
               "오", "코", "소", "토", "노", "호", "모", "요", "로", "고", "조", "도", "보", "포", "오", " ", "부", "ㅅ", "이"]
kor_two_syl = ["캬", "샤", "챠", "냐", "햐", "먀", "랴", "갸", "쟈", "뱌", "퍄",
               "큐", "슈", "츄", "뉴", "휴", "뮤", "류", "규", "쥬", "뷰", "퓨",
               "쿄", "쇼", "쵸", "뇨", "효", "묘", "료", "교", "죠", "뵤", "표",
               "앗", "캇", "삿", "탓", "낫", "핫", "맛", "얏", "랏", "왓", "갓", "잣", "닷", "밧", "팟",
               "잇", "킷", "싯", "칫", "닛", "힛", "밋", "릿", "깃", "짓", "짓", "빗", "핏",
               "웃", "쿳", "슷", "쯧", "눗", "훗", "뭇", "윳", "룻", "굿", "즛", "즛", "붓", "풋",
               "엣", "켓", "셋", "텟", "넷", "헷", "멧", "렛", "겟", "젯", "뎃", "벳", "펫",
               "옷", "콧", "솟", "톳", "놋", "홋", "못", "욧", "롯", "곳", "좃", "돗", "봇", "폿",
               "안", "칸", "산", "탄", "난", "한", "만", "얀", "란", "완", "간", "잔", "단", "반", "판",
               "인", "킨", "신", "찐", "닌", "힌", "민", "린", "긴", "진", "진", "빈", "핀",
               "운", "쿤", "슨", "쯘", "는", "훈", "문", "윤", "룬", "군", "즌", "즌", "분", "푼",
               "엔", "켄", "센", "텐", "넨", "헨", "멘", "렌", "겐", "젠", "덴", "벤", "펜",
               "온", "콘", "손", "톤", "논", "혼", "몬", "욘", "론", "곤", "존", "돈", "본", "폰",
               "쉐", "화", "휘", "훼", "훠", "위", "웨", "워", "촤", "취", "췌", "춰",
               "체", "콰", "퀴", "퀘", "쿼", "투", "듀",
               "봐", "마아",
               "디", "네이", "나이", "와", "아이", "휘", "제", "투", "티", "페", "왓", "앗"]
kor_three_syl = ["캿", "샷", "챳", "냣", "햣", "먓", "럇", "걋", "쟛", "뱟", "퍗",
                 "큣", "슛", "츗", "늇", "흇", "뮷", "륫", "귯", "쥿", "븃", "퓻",
                 "쿗", "숏", "춋", "뇻", "횻", "묫", "룟", "굣", "죳", "뵷", "푯",
                 "캰", "샨", "챤", "냔", "햔", "먄", "랸", "갼", "쟌", "뱐", "퍈",
                 "큔", "슌", "츈", "뉸", "휸", "뮨", "륜", "균", "쥰", "뷴", "퓬",
                 "쿈", "숀", "쵼", "뇬", "횬", "묜", "룐", "굔", "죤", "뵨", "푠"]

def furitohan_str(line):
    for idx, item in enumerate(jap_three_syl):
        line = line.replace(item, kor_three_syl[idx])
    for idx, item in enumerate(jap_two_syl):
        line = line.replace(item, kor_two_syl[idx])
    for idx, item in enumerate(jap_one_syl):
        line = line.replace(item, kor_one_syl[idx])
    return line

# Initialize translation API outside to reuse
translator = GoogleTranslator(source='ja', target='ko')

def correct_furi(lyrics: str):
    return lyrics.replace("君", "きみ")\
        .replace("Official髭男dism", "おふぃしゃるひげだんでぃずむ")\
        .replace("時間", "じかん")\
        .replace("後悔", "こうかい")\
        .replace("他の人", "ほかのひと")\
        .replace("日々", "ひび")\
        .replace("時々", "ときどき")\
        .replace("色々", "いろいろ")\
        .replace("二人", "ふたり")\
        .replace("2人", "ふたり")\
        .replace("実は", "じつは")\
        .replace("景色", "けしき")\
        .replace("色", "いろ")\
        .replace("年老い", "としおい")\
        .replace("光っ", "ひかっ")\
        .replace("今日", "きょう")\
        .replace("明日", "あした")\
        .replace("止ま", "やま")\
        .replace("交わ", "かわ")\
        .replace("温もり", "ぬくもり")\
        .replace("今年", "ことし")\
        .replace("花ビン", "かびん")\
        .replace("大人", "おとな")\
        .replace("人生", "じんせい")\
        .replace("街中", "まちじゅう")\
        .replace("隙間", "すきま")\
        .replace("近ごろ", "ちかごろ")\
        .replace("人", "ひと")\
        .replace("日", "ひ")\
        .replace("光", "ひかり")\
        .replace("頷", "うなず")\
        .replace("下", "した")\
        .replace("月", "つき")\
        .replace("間", "あいだ")\
        .replace("良い", "いい")\
        .replace("2時", "にじ")\
        .replace("灯る", "ともる")\
        .replace("灯", "あかり")\
        .replace("後", "あと")\
        .replace("暗がり", "くらがり")\
        .replace("無人", "むじん")\
        .replace("身体", "からだ")\
        .replace("孕んで", "はらんで")\
        .replace("縋っ", "すがっ")\
        .replace("弾け", "はじけ")\
        .replace("染み", "しみ")\
        .replace("曜日", "ようび")

def process_lyrics_text(raw_lyrics):
    tagger = MeCab.Tagger()
    
    lines = raw_lyrics.split('\n')
    results = []
    lines_to_translate = []
    
    for line in lines:
        # Strip timestamp like [00:17.12] or [00:17.123]
        clean_line = re.sub(r'\[\d{2}:\d{2}\.\d{2,3}\]', '', line).strip()
        if not clean_line:
            continue
            
        mecab_line = correct_furi(clean_line)
        
        # Preserve all whitespace by splitting and processing chunks
        chunks = re.split(r'(\s+)', mecab_line)
        katakana_reading = ""
        is_japanese_line = False
        
        for chunk in chunks:
            if not chunk.strip():
                katakana_reading += chunk
                continue
                
            parsed = tagger.parse(chunk)
            tokens = parsed.split('\n')
            
            for token in tokens:
                if token == 'EOS' or not token:
                    continue
                parts = token.split('\t')
                surface = parts[0]
                
                if len(parts) > 1:
                    pronunciation = parts[1]
                    if pronunciation and pronunciation != '*':
                        katakana_reading += pronunciation
                        is_japanese_line = True
                    else:
                        katakana_reading += surface
                else:
                    katakana_reading += surface
                
        # Convert Katakana to Hiragana
        hiragana_reading = jaconv.kata2hira(katakana_reading)
        
        # Convert Hiragana to Korean pronunciation
        pronunciation_ko = furitohan_str(hiragana_reading)
        
        has_japanese = bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', clean_line))
        
        # If not Japanese but contains English alphabet, generate phonetic Korean pronunciation
        if not has_japanese and re.search(r'[a-zA-Z]', clean_line):
            ipa_text = ipa.convert(clean_line)
            # Remove * that eng_to_ipa uses for OOV words, except we don't want to mess up user's phonetic
            # Actually, eng_to_ipa might insert '*' at the end of words. We should remove it before passing to phonetic.
            ipa_text = ipa_text.replace('*', '')
            pronunciation_ko = phonetic(ipa_text)
        
        lines_to_translate.append(clean_line)
        results.append({
            "original": clean_line,
            "pronunciation": pronunciation_ko,
            "translation": "",
            "is_japanese": is_japanese_line
        })
    # Batch Translation
    if lines_to_translate:
        # Google Translate preserves '\n' well. We join with newlines.
        text_to_translate = "\n".join(lines_to_translate)
        try:
            # Force auto detection so both English and Japanese songs translate perfectly
            t = GoogleTranslator(source='auto', target='ko')
            # Translate up to 5000 chars at once (API limit)
            # Most lyrics are ~1000 chars
            translated_text = t.translate(text_to_translate[:4999])
            
            if translated_text:
                translated_lines = translated_text.split('\n')
                
                # Sometimes Google Translate returns slightly fewer/more lines.
                # We map as closely as possible.
                for i, r in enumerate(results):
                    if i < len(translated_lines):
                        r["translation"] = translated_lines[i]
                    else:
                        r["translation"] = ""
        except Exception as e:
            print("Batch translate error:", e)
            for r in results:
                r["translation"] = "(번역 실패)"

    # Remove the internal flag before returning
    for r in results:
        r.pop("is_japanese", None)

    return results
