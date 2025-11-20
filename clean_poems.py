import re
import json
from pathlib import Path

def clean_dickinson_poems(
    input_file: str = "dickinson.txt",
    output_file: str = "poems.json",
):
    """
    Extracts Emily Dickinson poems from a raw Gutenberg text and writes them as
    JSON
    - detects roman numeral poem numbers ("I.", "II.", etc.)
    - skips section headings (e.g. "I. LIFE.")
    - skips ALL CAPS titles (e.g. "SUCCESS.")
    - collects the poem lines
    - writes a JSON list of { "poem_number": ..., "poem_text": ... }
    """
    text = Path(input_file).read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    # Roman numerals
    roman_re = re.compile(r"^[IVXLCDM]+\.$")

    poems = []
    current_poem_num = None
    current_lines = []

    for line in lines:
        stripped = line.strip()

        # Detects a poem-number line (e.g. "I.")
        if roman_re.match(stripped):
            # Save if already collecting a poem
            if current_poem_num is not None and current_lines:
                poem_text = "\n".join(current_lines).strip()
                if poem_text:
                    poems.append(
                        {
                            "poem_number": current_poem_num,
                            "poem_text": poem_text,
                        }
                    )

            current_poem_num = stripped.rstrip(".")
            current_lines = []
            continue

        # Skip section headers
        if stripped and stripped.upper() == stripped and any(c.isalpha() for c in stripped):
            continue

        # Collects poem lines
        if current_poem_num is not None:
            # Keep blank lines as stanza separators
            current_lines.append(line.rstrip())

    # Save the final poem
    if current_poem_num is not None and current_lines:
        poem_text = "\n".join(current_lines).strip()
        if poem_text:
            poems.append(
                {
                    "poem_number": current_poem_num,
                    "poem_text": poem_text,
                }
            )

    # Write JSON
    Path(output_file).write_text(json.dumps(poems, indent=2), encoding="utf-8")
    print(f"Saved {len(poems)} poems to {output_file}")

if __name__ == "__main__":
    clean_dickinson_poems()
    