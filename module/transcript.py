import re

def convert_punctuation(string):
    string = string.replace("!", "！")
    string = string.replace("?", "？")
    return string

def is_text_clean(text):
    # 日本語（平仮名、カタカナ、漢字）、英数字、句読点、感嘆符、疑問符以外の文字を検出
    pattern = r'[^\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u0030-\u0039\u0041-\u005A\u0061-\u007A、。！？]'
    non_specified_chars = re.findall(pattern, text)
    # 検出された文字がなければTrue、あればFalseを返す
    return not non_specified_chars

def generate_patterns(syllables):
    # 二文字の組み合わせパターンを生成
    return [a + b for a in syllables for b in syllables]

def reduce_repetitions(text, patterns, max_repeats=4):
    # 任意の文字の繰り返しを検出し、6回に制限
    general_pattern = r'(.)\1{1,}'
    def limit_general_repeats(match):
        return match.group(1) * min(len(match.group(0)), max_repeats)

    # 各パターンに対して正規表現を適用
    for pattern in patterns:
        regex = fr'({pattern})(?:\1)+'
        text = re.sub(regex, limit_general_repeats, text)

    return re.sub(general_pattern, limit_general_repeats, text)