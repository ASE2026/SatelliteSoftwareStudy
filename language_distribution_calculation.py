import pandas as pd
import re
from collections import defaultdict
import os


INPUT_FILE = 'TestLanguage.xlsx' 

LANGUAGE_COLUMN_NAME = 'languages'


def parse_languages(lang_str):
    if pd.isna(lang_str) or lang_str is None or str(lang_str).strip().lower() == 'none':
        return []

    s = str(lang_str)
    parsed_data = []


    pattern = re.compile(
        r'([^\n]+?)\s*(?:\n\s*|\s+)(\d+(?:\.\d+)?)%',
        re.MULTILINE
    )

    matches = pattern.findall(s)

    print(f"Regex match results: {matches}")

    for lang_name, percent_str in matches:
        lang_name = lang_name.strip()
        try:
            lang_percent = float(percent_str)
        except ValueError:
            continue

        parsed_data.append((lang_name, lang_percent))

    return parsed_data

def main():
    try:
        df = pd.read_excel(INPUT_FILE)
        df['Parsed_Languages'] = df[LANGUAGE_COLUMN_NAME].apply(parse_languages)
        language_totals = defaultdict(float)
        for lang_list in df['Parsed_Languages']:
            for lang, percent in lang_list:
                language_totals[lang] += percent

        print(f"Language Totals (Pass 1 Results): {dict(language_totals)}")

        total_percent = sum(language_totals.values())
        print(f"All language percentages：{total_percent:.2f}")

        language_shares = {
            lang: (percent / total_percent) *100
            for lang, percent in language_totals.items()
        }

        TOP_K = 10
        sorted_langs = sorted(language_shares.items(),
                              key = lambda x:x[1],
                              reverse=True)
        
        print(len(sorted_langs))
        
        if len(sorted_langs) > TOP_K:
            top_langs = sorted_langs[:TOP_K]          
            other_langs = sorted_langs[TOP_K:]        

            other_share = sum(share for _, share in other_langs)
            final_langs = top_langs + [("OtherLanguages", other_share)]
        else:
            final_langs = sorted_langs
        
        
        for lang, share in final_langs:
            print(f"{lang}: {share:.2f}%")

    except Exception as e:
        print(f"\n error occurs {e}")

if __name__ == "__main__":
    main()