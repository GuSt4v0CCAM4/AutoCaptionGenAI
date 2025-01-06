import re
from difflib import SequenceMatcher

def parse_srt(srt_file):
    """Parse the SRT file and return a list of subtitle entries."""
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n\n', re.DOTALL)
    matches = pattern.findall(content)

    subtitles = []
    for match in matches:
        subtitles.append({
            'number': int(match[0]),
            'start_time': match[1],
            'end_time': match[2],
            'text': match[3].strip()
        })

    return subtitles

def save_srt(srt_file, subtitles):
    """Save the subtitles list into an SRT file."""
    with open(srt_file, 'w', encoding='utf-8') as f:
        for subtitle in subtitles:
            f.write(f"{subtitle['number']}\n")
            f.write(f"{subtitle['start_time']} --> {subtitle['end_time']}\n")
            f.write(f"{subtitle['text']}\n\n")

def compare_and_refine(subtitles, script_file):
    """Compare subtitles with the script and refine them."""
    with open(script_file, 'r', encoding='utf-8') as f:
        script_lines = f.readlines()

    for subtitle in subtitles:
        best_match = ''
        highest_ratio = 0

        for script_line in script_lines:
            ratio = SequenceMatcher(None, subtitle['text'], script_line.strip()).ratio()
            if ratio > highest_ratio:
                highest_ratio = ratio
                best_match = script_line.strip()

        if highest_ratio > 0.6:  # Only update if a significant match is found
            subtitle['text'] = best_match

    return subtitles

def sort_srt_by_time(subtitles):
    """Sort the subtitles by start time."""
    def time_to_seconds(time_str):
        hours, minutes, seconds = map(float, re.split('[:|,]', time_str))
        return hours * 3600 + minutes * 60 + seconds

    return sorted(subtitles, key=lambda x: time_to_seconds(x['start_time']))

# Main function to refine and sort subtitles
def refine_and_sort_srt(srt_file, script_file):
    subtitles = parse_srt(srt_file)
    subtitles = compare_and_refine(subtitles, script_file)
    subtitles = sort_srt_by_time(subtitles)

    for i, subtitle in enumerate(subtitles):
        subtitle['number'] = i + 1  # Renumber subtitles sequentially

    save_srt(srt_file, subtitles)

# Usage example
if __name__ == "__main__":
    refine_and_sort_srt("caption.srt", "guion.txt")
