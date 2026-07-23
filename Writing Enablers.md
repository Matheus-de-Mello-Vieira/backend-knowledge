# Enables
## Transcript download

Download subtitles:
```bash
set -euo pipefail

OUT_DIR="subtitles"
mkdir -p "$OUT_DIR"

urls=(
  "https://...vtt"
  ""
  ""
  ""
)

rm $OUT_DIR/*

for url in "${urls[@]}"; do
  filename="${url##*/}"
  echo "Downloading $filename"
  curl -L --fail --retry 3 --retry-delay 2 \
    -o "$OUT_DIR/$filename" \
    "$url"
done

echo "Done. Files saved in: $OUT_DIR/"
```

## Transcript to text

use [prompt_example](prompt_example.md)
## Notes section writer

Transform a texto into a single section with a title, a short introduction and bullet points.

```
I want you to act as an expert technical writer. Please rewrite the following notes/topic into a highly scannable, easy-to-read format using the specific style rules below. 

Style Rules:
- Title: Start with a simple, direct title.
- Introduction: Write a brief 1-2 sentence introductory paragraph that clearly defines the core concept. Do not use any filler language. 
- Format: Do not use numbered lists, heavy headers (like H2 or H3), or excessive subsections. 
- Catchy Identifiers: Break the detailed information into distinct points. Start each point with a bolded, catchy, and descriptive short phrase, followed by a colon (e.g., **The Rule of Thumb:**, **The Code Tax:**, **Under the Hood:**).
- Tone: Keep the writing professional, punchy, and direct. Avoid being pendantic.

Topic/Notes to rewrite:
[Insert your raw text, topic, or rough notes here]
```