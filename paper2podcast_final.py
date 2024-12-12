# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 17:25:03 2024

@author: obayd
"""

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from gtts import gTTS
from pathlib import Path

# Step 1: Extract links from arXiv
def extract_links():
    url = "https://arxiv.org/list/cs/new"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve arXiv page: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    entries = soup.find_all('dt')[:1]  # Limit to the first entry

    for entry in entries:
        paper_link = entry.find('a', title='Abstract')['href']
        full_link = f"https://arxiv.org{paper_link}"
        entry_dd = entry.find_next_sibling('dd')
        title = entry_dd.find('div', class_='list-title').text.strip()[7:]  # Remove "Title: "
        abstract = entry_dd.find('p', class_='mathjax').text.strip()

        return {
            'title': title,
            'abstract': abstract,
            'link': full_link
        }

# Step 2: Fetch metadata from arXiv API
def fetch_metadata(arxiv_id):
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch metadata: {response.status_code}")
        return None

    root = ET.fromstring(response.content)
    ns = {'arxiv': 'http://www.w3.org/2005/Atom'}
    entry = root.find('arxiv:entry', ns)

    return {
        'title': entry.find('arxiv:title', ns).text.strip(),
        'summary': entry.find('arxiv:summary', ns).text.strip(),
        'authors': ', '.join([author.text for author in entry.findall('arxiv:author/arxiv:name', ns)]),
        'published': entry.find('arxiv:published', ns).text
    }

# Step 3: Generate podcast script
def generate_podcast_script(metadata):
    script = (
        f"Welcome to the podcast! Today, we discuss \"{metadata['title']}\", "
        f"authored by {metadata['authors']}, published on {metadata['published']}.\n\n"
        f"Summary:\n{metadata['summary']}\n\n"
        "Stay tuned for more insights!"
    )
    return script

# Step 4: Convert script to audio
def text_to_speech(script, output_path):
    tts = gTTS(text=script, lang='en')
    tts.save(output_path)
    print(f"Audio saved to {output_path}")

# Main Workflow
def main():
    # Step 1: Extract a paper link
    paper_info = extract_links()
    if not paper_info:
        return

    print(f"Paper Selected: {paper_info['title']}\n{paper_info['abstract']}\n{paper_info['link']}")

    # Step 2: Fetch metadata
    arxiv_id = paper_info['link'].split('/')[-1]
    metadata = fetch_metadata(arxiv_id)
    if not metadata:
        return

    # Step 3: Generate podcast script
    script = generate_podcast_script(metadata)
    script_path = Path(f"{arxiv_id}_podcast_script.txt")
    with open(script_path, 'w') as file:
        file.write(script)
    print(f"Podcast script saved to {script_path}")

    # Step 4: Convert to audio
    audio_path = Path(f"{arxiv_id}_podcast.mp3")
    text_to_speech(script, audio_path)

if __name__ == "__main__":
    main()
