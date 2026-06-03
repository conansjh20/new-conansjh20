def join_jamos(text):
    CHOSUNG = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
    JUNGSUNG = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
    JONGSUNG = ' ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ'
    result = ''
    i = 0
    while i < len(text):
        has_star = False
        
        while i < len(text) and text[i] == '*':
            has_star = True
            i += 1
            
        if i < len(text) and text[i] in CHOSUNG:
            cho_char = text[i]
            
            j = i + 1
            while j < len(text) and text[j] == '*':
                has_star = True
                j += 1
                
            if j < len(text) and text[j] in JUNGSUNG:
                jung_char = text[j]
                
                k = j + 1
                while k < len(text) and text[k] == '*':
                    has_star = True
                    k += 1
                    
                jong_char = ' '
                if k < len(text) and text[k] in JONGSUNG:
                    m = k + 1
                    while m < len(text) and text[m] == '*':
                        m += 1
                    if m == len(text) or text[m] not in JUNGSUNG:
                        jong_char = text[k]
                        if m > k + 1:
                            has_star = True
                        k = m
                
                cho = CHOSUNG.index(cho_char)
                jung = JUNGSUNG.index(jung_char)
                jong = JONGSUNG.index(jong_char)
                
                char = chr(0xAC00 + ((cho * 21) + jung) * 28 + jong)
                if has_star:
                    result += '*' + char
                else:
                    result += char
                    
                i = k
                continue
                
        if i < len(text):
            if has_star:
                result += '*' + text[i]
            elif text[i] != '*':
                result += text[i]
            i += 1
            
    return result

# --- 글로벌 상수 (규칙 함수들에서 사용) ---

# 이 리스트들은 님의 규칙 함수 내부에서 `in vowels` 등으로 참조되므로 유지합니다.
vowels = ["i", "ɪ", "ʊ", "u", "ɛ", "e", "ə", "æ", "a", "ʌ", "ɑ", "ɒ", "ɔ", "o", "ɚ", "ɝ", "ɜ", "œ"]
consonants = ["p", "θ", "h", "b", "ð", "m", "t", "s", "n", "d", "z", "ŋ", "k", "ʃ", "r", "g", "ʒ", "l", "f", "w", "v"]

# --- 1. 모음 핸들러 (Refactored) ---

# 반복되는 모음 로직을 하나로 통합하기 위한 맵(Map)입니다.
# 형식: IPA: (기본 자모, 'ㅇ'초성, 'y'계열, 'w'결합 시 예외)
VOWEL_MAP = {
    # IPA: (base, initial, yotized, w_special)
    'a': ('ㅏ', 'ㅇㅏ', 'ㅑ', None),
    'ɑ': ('ㅏ', 'ㅇㅏ', 'ㅑ', None),
    'ɒ': ('ㅏ', 'ㅇㅏ', 'ㅑ', None),
    'æ': ('ㅐ', 'ㅇㅐ', 'ㅒ', None),
    'i': ('ㅣ', 'ㅇㅣ', 'ㅣ', None),
    'ɪ': ('ㅣ', 'ㅇㅣ', 'ㅣ', None),
    'u': ('ㅜ', 'ㅇㅜ', 'ㅠ', None),
    'ʊ': ('ㅜ', 'ㅇㅜ', 'ㅠ', 'ㅓ'), # 'w' + 'ʊ'는 '워'로 발음 (예외)
    'e': ('ㅔ', 'ㅇㅔ', 'ㅖ', None),
    'ɛ': ('ㅔ', 'ㅇㅔ', 'ㅖ', None),
    'ə': ('ㅓ', 'ㅇㅓ', 'ㅕ', None),
    'ʌ': ('ㅓ', 'ㅇㅓ', 'ㅕ', None),
    'ɜ': ('ㅓ', 'ㅇㅓ', 'ㅕ', None),
    'o': ('ㅗ', 'ㅇㅗ', 'ㅛ', None),
    'ɔ': ('ㅗ', 'ㅇㅗ', 'ㅛ', 'ㅓ'), # 'w' + 'ɔ'는 '워'로 발음 (예외)
}

def handle_vowel(index, word, ipa_vowel):
    """
    모든 IPA 모음의 변환 로직을 통합하여 처리하는 단일 함수입니다.
    """
    if ipa_vowel not in VOWEL_MAP:
        return ""  # 맵에 없는 모음(ɚ, ɝ)은 처리하지 않음

    # 맵에서 현재 모음에 해당하는 한글 자모 세트를 가져옵니다.
    jamos = VOWEL_MAP[ipa_vowel]
    base, initial, yotized, w_special = jamos

    # --- 님의 원본 모음 규칙 로직 (하나로 통합) ---

    if index != 0:
        prev_char = word[index-1]

        if prev_char == "ŋ":
            return initial
        
        if prev_char == 'w':
            if w_special:  # 'ʊ'나 'ɔ'의 'w' 결합 예외 처리
                return w_special
            return base
        
        if prev_char == "ʃ":
            # func_ɑ에 있던 'ʃ' + 'ɑ' + 'l' 예외 규칙
            if ipa_vowel == 'ɑ' and index < len(word)-2:
                if (word[index+1] in ["'","ˌ"]) and (word[index+2] == "l"):
                    return "ㅑㄹ"
            return yotized
        
        if prev_char == "y":
            if index > 1 and word[index-2] in ["'","ˌ"]:
                # func_ə에 있던 'y' + 'ə' 예외 규칙
                if ipa_vowel == 'ə' and word[index-2] in vowels:
                    return initial
                return initial
            return yotized
            
        if prev_char == "j":
            return yotized

    # 'l' 받침 규칙 (미래)
    if index < len(word)-2:
        if (word[index+1] in ["'","ˌ"]) and (word[index+2] == "l"):
            # func_ɪ에 있던 'ɪ' + 'l' 예외 규칙
            if ipa_vowel == 'ɪ' and index == 0:
                return initial + "ㄹ"
            
            # 표준 'l' 받침 규칙
            if (index > 0 and word[index-1] in consonants):
                return base + "ㄹ"
            return initial + "ㄹ"

    # 'l' 받침 규칙 (과거)
    if index > 1:
        if (word[index-1] in ["'","ˌ"]) and (word[index-2] == "l"):
            return "ㄹ" + base  # 예: ㄹ + ㅏ

    # 첫 글자 또는 모음 뒤 (초성 'ㅇ' 필요)
    if (index == 0) or (word[index-1] in ["^","-",";"]) or (word[index-1] in ["'","ˌ"]):
        return initial
    
    if index > 0 and word[index-1] in vowels:
        return initial
    
    # 그 외 자음 뒤 (모음만 필요)
    return base

# --- 2. 자음 및 기타 기호 핸들러 ---
# (님의 원본 코드를 그대로 유지. 이 규칙들은 매우 독자적이라 통합이 불필요)

def func_œ(index, word):
    return "ㅗㅣ"

def func_p (index, word):
    if index == 0:## 첫글자일때
        return "ㅍ"
    if index == len(word)-1:## 마지막글자일때
        return "ㅍ"
    if word[index+1] in ["^",";","-"]:## 마지막글자일때
        return "ㅍ"
    if word[index-1] in consonants:
        if word[index+1] in vowels:
            return "ㅍ"
        return "ㅍㅡ"
    if word[index+1] in vowels:
        return "ㅍ"
    if word[index+1] in consonants:
        return "ㅍㅡ"
    return "ㅍ"

def func_θ (index, word):
    if index == 0:## 첫글자일때
        return "ㅆ"
    if index == len(word)-1:## 마지막글자일때
        return "ㅆㅡ"
    if word[index+1] in ["^",";"]:## 마지막글자일때
        return "ㅆㅡ"
    return "ㅆ"

def func_h (index, word):
    if index == 0:## 첫글자일때
        return "ㅎ"
    if index == len(word)-1:## 마지막글자일때
        return "ㅎㅡ"
    if word[index+1] in ["^",";"]:## 마지막글자일때
        return "ㅎㅡ"
    return "ㅎ"

def func_b (index, word):
    if index == 0:## 첫글자일때
        if word[index+1] == "w":
            return "ㅂ"
        if word[index+1] in consonants:
            return "ㅂㅡ"
        return "ㅂ"
    if (index == len(word)-1) or (word[index+1] in ["^", ";"]):## 마지막글자일때
        if word[index-1] in consonants:
            return "ㅂㅡ"
        return "ㅂ"
    if word[index+1] in ["^",";"]:## 마지막글자일때
        return "ㅂ"
    if word[index-1] in vowels:
        if word[index+1] in consonants:
            return "ㅂㅡ"
        return "ㅂ"
    if word[index+1] in vowels:
        return "ㅂ"
    if word[index+1] in {"l", "r"}:
        return "ㅂㅡ"
    return "ㅂ"

def func_ð (index, word):
    if index == 0:## 첫글자일때
        return "ㄸ"
    if index == len(word)-1:## 마지막글자일때
        return "ㄸㅡ"
    if word[index+1] in ["^",";"]:## 마지막글자일때
        return "ㄸㅡ"
    return "ㄸ"

def func_m (index, word):
    if index == 0:## 첫글자일때
        return "ㅁ"
    if index == len(word)-1:## 마지막글자일때
        return "ㅁ"
    if word[index+1] in ["^",";"]:## 마지막글자일때
        return "ㅁ"
    return "ㅁ"

def func_t (index, word):
    if index == 0:## 첫글자일때
        return "ㅌ"
    if index == len(word)-1:## 마지막글자일때
        if word[index-1] in vowels:
            return "ㅌ"
        return "ㅌㅡ"
    if word[index+1] in ["^",";"]:## 마지막글자일때
        if word[index-1] in vowels:
            return "ㅌ"
        return "ㅌㅡ"
    if word[index-1] in vowels:
        return "ㅌ"
    if word[index+1] in vowels:
        return "ㅌ"
    if word[index+1] in ["w"]:
        return "ㅌ"
    if word[index+1] == "ʃ":
        if word[len(word)-1] == "ʃ":
            return "ㅊㅜ"
        return "ㅊ"
    return "ㅌㅡ"

def func_s (index, word):
    if index == 0:## 첫글자일때
        if word[index+1] in consonants:## 마지막글자일때
            return "ㅅㅡ"
        return "ㅅ"
    if index == len(word)-1:## 마지막글자일때
        return "ㅅㅡ"
    if word[index+1] in consonants+["^",";"]:## 마지막글자일때
        return "ㅅㅡ"
    if word[index+1] == "^":
        return "ㅅㅡ"
    if word[index+1] in vowels:
        return "ㅅ"
    if word[index+1] in ["t", "k"]:
        return "ㅅㅡ"
    if word[index-1] in vowels:
        return "ㅅㅡ"
    if word[index-1] in consonants:
        if word[index+1] in consonants or word[index+1] in ["'","ˌ"] :
            return "ㅅㅡ"
    return "ㅅ"

def func_n (index, word):
    if index == 0:## 첫글자일때
        return "ㄴ"
    if index == len(word)-1:## 마지막글자일때
        return "ㄴ"
    if word[index+1] in ["^",";"]:## 마지막글자일때
        return "ㄴ"
    if word[index-1] in vowels:
        if word[index+1] == "l":
            return "ㄴㅓ"
        return "ㄴ"
    if word[index+1] == "l":
        return "ㄴㅓ"
    if word[index+1] in consonants:
        if word[index+1] in ["t", "d", "s", "θ"]:
            return "ㄴ"
        return "ㄴㅡ"
    return "ㄴ"

def func_d (index, word):
    if index != len(word)-1:## 첫글자일때
        if word[index+1] == "ʒ":
            return "ㅈ"
        if word[index+1] in consonants+["'","ˌ"]:
            return "ㄷㅡ"
    if index == len(word)-1:## 마지막글자일때
        return "ㄷㅡ"
    if word[index+1] in ["^",";"]:## 마지막글자일때
        return "ㄷㅡ"
    return "ㄷ"

def func_ʒ (index, word):
    if index == 0:## 첫글자일때
        return "ㅈ"
    if word[index-1] in [";","^"]:## 첫글자일때
        return "ㅈ"
    if index == len(word)-1:
        return "ㅈㅡ"
    if word[index+1] in [";","^"]:
        if (word[index-1] == "d"):
            return "ㅡ"
        return "ㅈㅡ"
    if (word[index-1] == "d"):
        if (index == len(word)-1):
            return "ㅣ"
        if (word[index+1] in [";","^"]):
            return "ㅣ"
        return ""
    return "ㅈ"

def func_z (index, word):
    if index == 0:## 첫글자일때
        return "*ㅈ"
    if index == len(word)-1:## 마지막글자일때
        return "*ㅈㅡ"
    if word[index+1] in ["^",";","'","ˌ"]:## 마지막글자일때
        return "*ㅈㅡ"
    if word[index+1] in consonants:
        return "*ㅈㅡ"
    if word[index-1] == "^":
        return "*ㅈㅡ"
    return "*ㅈ"

def func_k (index, word):
    if index == 0:## 첫글자일때
        return "ㅋ"
    if index == len(word)-1:## 마지막글자일때
        return "ㅋㅡ"
    if word[index+1] in ["l", "r", "m", "n", "ʃ"]:
        return "ㅋㅡ"
    if word[index+1] in vowels:
        return "ㅋ"
    if word[index-1] in vowels:
        return "ㅋ"
    if word[index+1] in ["^",";","'","ˌ"]:## 마지막글자일때
        return "ㅋㅡ"
    if word[index-1] in ["'","ˌ"]:
        return "ㅋ"
    return "ㅋ"

def func_r (index, word):
    if index == 0:## 첫글자일때
        return "*ㄹ"
    if index == len(word)-1:## 마지막글자일때
        return "ㄹ*"
    if word[index+1] in ["^",";"]:## 마지막글자일때
        return "ㄹ*"
    if word[index+1] in vowels:
        return "*ㄹ"
    if word[index-1] in vowels:
        return "ㄹ*"
    return "*ㄹ"

def func_g (index, word):
    if index == 0:## 첫글자일때
        if word[index+1] in consonants:
            return "ㄱㅡ"
        return "ㄱ"
    if index == len(word)-1:## 마지막글자일때
        if word[index-1] in consonants:
            return "ㄱㅡ"
        return "ㄱ"
    if word[index+1] in ["^",";","w","'","-"]:## 마지막글자일때
        if word[index-1] in consonants:
            return "ㄱㅡ"
        return "ㄱ"
    if word[index+1] in consonants:
        return "ㄱㅡ"
    return "ㄱ"

def func_f (index, word):
    if index == 0:## 첫글자일때
        return "*ㅍ"
    if index == len(word)-1:## 마지막글자일때
        return "*ㅍㅡ"
    if word[index+1] in ["^",";","-"]:## 마지막글자일때
        return "*ㅍㅡ"
    if word[index+1] in consonants:
        return "*ㅍㅡ"
    return "*ㅍ"

def func_v (index, word):
    if index == 0:## 첫글자일때
        return "*ㅂ"
    if index == len(word)-1:## 마지막글자일때
        return "*ㅂㅡ"
    if word[index+1] in vowels:
        return "*ㅂ"
    if word[index-1] in vowels:
        return "*ㅂㅡ"
    if word[index+1] in ["^",";"]:## 마지막글자일때
        return "*ㅂㅡ"
    return "*ㅂ"

def func_l (index, word):
    if (index == 0):## 첫글자일때
        return "ㄹ"
    
    if (word[index-1] in [";","^"]):## 첫글자일때
        return "ㄹ"

    if word[index-1] in ["r"]:
        if index != len(word)-1:
            if word[index+1] in consonants:
                return ""
        
        if (index == len(word)-1) or (word[index+1] in [";","^"]):## 마지막글자일때
            return ""
        
        if word[index+1] in ["n", "m"]:
            return "ㄹㅡ"
        
        if (word[index-1] in ["'","ˌ"]):
            return ""
        return "ㄹ"

    if index != len(word)-1:
        if word[index+1] in consonants:
            return "ㄹ"
    
    if (index == len(word)-1) or (word[index+1] in [";","^"]):## 마지막글자일때
        return "ㄹ"
    
    if word[index+1] in ["n", "m"]:
        return "ㄹㄹㅡ"
    
    if (word[index-1] in ["'","ˌ","m","n"]):
        return "ㄹ"
    
    if (word[index+1] in ["'","ˌ"]):
        return "ㄹ"
    
    return "ㄹㄹ"

def func_ʃ (index, word):
    if index == 0:## 첫글자일때
        if word[index+1] in consonants:
            return "스"
        return "ㅅ"
    if word[index-1] == "t":
        if index == len(word)-1:
            return "ㅣ"
        if word[index+1] in ["^",";","'","ˌ"]:
            return "ㅣ"
        return ""
    if index == len(word)-1:## 마지막글자일때
        return "쉬"
    if word[index+1] in consonants:
        return "스"
    if word[index+1] in ["^",";"]:## 마지막글자일때
        return "쉬"
    return "ㅅ"

def func_j (index, word):
    return ""

def func_ŋ (index, word):
    if index == 0:## 첫글자일때
        return "ㅇ"
    if index == len(word)-1:## 마지막글자일때
        return "ㅇ"
    return "ㅇ"

def func_w (index, word):
    if index == 0:## 첫글자일때
        return "ㅇㅜ"
    if index == len(word)-1:## 마지막글자일때
        return "ㅜ"
    if word[index+1] in ["e","ɪ"]:
        if word[index-1] in ["k"]:
            return "ㅜ"
        if word[index-1] in ["'", "ˌ"]+consonants:
            return "ㅇㅜ"
    if word[index+1] in ["a","ɑ","ɒ","æ"]:
        if word[index-1] in ["k"]:
            return "ㅗ"
        if word[index-1] in ["'", "ˌ"]+consonants:
            return "ㅇㅗ"
        return "ㅗ"
    if word[index-1] in vowels:
        return "ㅇㅜ"
    if word[index-1] in ["'","ˌ"]:
        return "ㅇㅜ"
    return "ㅜ"

def func_y (index, word):
    if index == 0:
        return "ㅇ"
    if word[index-1] in ["^", ";"]:
        return "ㅇ"
    return ""

def func_long(index, word):
    return "-"

def func_accent(index, word):
    return "'"

def func_medium(index, word):
    return "ˌ"


# --- 3. 메인 변환 함수 (Refactored) ---

# 처리 함수들을 딕셔너리에 매핑 (dispatch table)
CONSONANT_HANDLERS = {
    'p': func_p, 'θ': func_θ, 'h': func_h, 'b': func_b, 'ð': func_ð,
    'm': func_m, 't': func_t, 's': func_s, 'n': func_n, 'd': func_d,
    'z': func_z, 'ŋ': func_ŋ, 'k': func_k, 'ʃ': func_ʃ, 'r': func_r,
    'g': func_g, 'ʒ': func_ʒ, 'l': func_l, 'f': func_f, 'j': func_j,
    'v': func_v, 'w': func_w, 'y': func_y,
}

OTHER_HANDLERS = {
    ':': func_long,
    "'": func_accent,
    'ˌ': func_medium,
    'œ': func_œ, # 'œ'는 규칙이 단순해 이곳에 포함
    '^': lambda idx, word: "^^", # 간단한 변환은 lambda 사용
    ';': lambda idx, word: ";;",
    '-': lambda idx, word: "-",
}

def phonetic(word):
    """
    IPA 문자열을 한글 자모로 변환합니다.
    if/elif 대신 딕셔너리(dispatch)를 사용하도록 리팩토링되었습니다.
    """
    result = []
    for idx, syl in enumerate(word):
        converted = ""
        
        if syl in VOWEL_MAP:
            # 1. 모음 처리 (통합된 함수 호출)
            converted = handle_vowel(idx, word, syl)
        elif syl in CONSONANT_HANDLERS:
            # 2. 자음 처리
            converted = CONSONANT_HANDLERS[syl](idx, word)
        elif syl in OTHER_HANDLERS:
            # 3. 기타 기호 처리
            converted = OTHER_HANDLERS[syl](idx, word)
        else:
            # 4. 맵에 없는 기호(ɚ, ɝ 등)는 원본처럼 'pass'
            pass
            
        result.append(converted)

    # 이중 모음 처리 (님의 원본 로직 유지)
    result_str = "".join(result)
    result_str = result_str.replace("ㅜㅔ","ㅞ")\
        .replace("ㅜㅣ", "ㅟ")\
        .replace("ㅜㅓ", "ㅝ")\
        .replace("ㅜㅐ", "ㅙ")\
        .replace("ㅗㅏ", "ㅘ")\
        .replace("ㅗㅐ", "ㅙ")\
        .replace("ㅗㅣ", "ㅚ")\
        .replace("ㅡㅣ", "ㅢ")
    
    return join_jamos(result_str)

