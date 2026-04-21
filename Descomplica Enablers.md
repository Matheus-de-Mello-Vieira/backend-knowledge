# Extract video info

Download and concatenate subtitles:
```bash
set -euo pipefail

URLS=(
  "https://url1.m3u8"
  "https://url2.m3u8"
  ...
)

OUTPUT_FILE="${1:-merged.vtt}"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

printf 'WEBVTT\n\n' > "$OUTPUT_FILE"

first=true

for url in "${URLS[@]}"; do
  vtt_url="${url%.m3u8}.vtt"
  local_file="$TMP_DIR/$(basename "$vtt_url")"

  echo "Downloading: $vtt_url"
  curl -fsSL "$vtt_url" -o "$local_file"

  if $first; then
    cat "$local_file" >> "$OUTPUT_FILE"
    first=false
  else
    awk '!/^[[:space:]]*WEBVTT([[:space:]].*)?$/' "$local_file" >> "$OUTPUT_FILE"
  fi

  printf '\n\n' >> "$OUTPUT_FILE"
done

echo "Done: $OUTPUT_FILE"
```

Now go to any LLM, get the written text and:
```
You are given:

1. A text extracted from concatenated auto-generated .vtt subtitle files (it may include timestamps, repeated headers, broken sentences, and transcription errors)
2. Written notes about the same subject (more accurate but possibly incomplete or summarized)

Your task is to reconstruct a clean, accurate transcript of what was said.

---

REQUIREMENTS:

CONTENT CLEANUP:

* Ignore timestamps, cue numbers, and "WEBVTT" headers completely
* Remove duplicates, broken fragments, and obvious transcription artifacts
* Merge split sentences into full, natural sentences

CORRECTION:

* Fix transcription errors using the written notes as the primary source of truth
* When notes and transcript conflict, prefer the notes if clearly more accurate
* Improve grammar, spelling, punctuation, and capitalization
* Preserve the original meaning, tone, and technical terminology
* Do NOT hallucinate or add content not supported by the input or notes

STRUCTURE:

* Produce a coherent, well-flowing text (like a cleaned transcript or lecture notes)
* Organize into paragraphs
* Optionally group ideas into sections if the topic naturally allows it

EDGE CASES:

* If a part is unclear and not covered in the notes, make the most reasonable correction based on context
* If something is unintelligible, omit it rather than inventing content

---

OUTPUT RULES:

* Return ONLY the cleaned transcript
* No timestamps, no formatting artifacts, no commentary
* Write in clear, natural language
```
