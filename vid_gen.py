import xml.etree.ElementTree as ET
import ffmpeg
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import tempfile
import os
from textwrap import wrap
import subprocess

def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    scenes = []
    for scene in root.findall('scene'):
        background = scene.find('background').get('image')
        dialogues = []
        for dialogue in scene.find('dialogues').findall('dialogue'):
            dialogues.append({
                'id': dialogue.get('id'),
                'character_image': dialogue.get('character_image'),
                'text': dialogue.text,
                'tts_audio': dialogue.get('tts_audio')
                
            })
        scenes.append({'background': background, 'dialogues': dialogues})
    return scenes

import os

def create_frame(background_url, current_char_path, last_char_path, dialogue_text, frame_number, speaker_name):
    # Download and open background image
    try:
        response = requests.get(background_url)
        response.raise_for_status()
        background = Image.open(BytesIO(response.content)).convert('RGBA')
        background = background.resize((1344, 768))
    except (requests.RequestException, IOError) as e:
        print(f"Error downloading or opening background image: {e}")
        background = Image.new('RGBA', (1344, 768), (0, 0, 0, 255))  # Create a black background as fallback

    # Function to load and resize image while maintaining aspect ratio
    def load_and_resize_image(path, max_width, max_height):
        if path and "https://" in path:
            response = requests.get(path)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert('RGBA')
        elif path:
            img = Image.open(path).convert('RGBA')
        else:
            return None
        
        # Calculate aspect ratio
        aspect_ratio = img.width / img.height
        
        # Determine new size while maintaining aspect ratio
        if aspect_ratio > 1:  # Width is greater than height
            new_width = min(max_width, img.width)
            new_height = int(new_width / aspect_ratio)
        else:  # Height is greater than or equal to width
            new_height = min(max_height, img.height)
            new_width = int(new_height * aspect_ratio)
        
        return img.resize((new_width, new_height), Image.LANCZOS)

    # Add characters if paths are provided
    max_char_width = int(1344 * 0.25)  # Reduced width to fit two characters
    max_char_height = int(768 * 0.8)
    
    if current_char_path and speaker_name.lower() != "narrator":
        try:
            current_char = load_and_resize_image(current_char_path, max_char_width, max_char_height)
            if current_char:
                left_pos = (int(1344 * 0.05), 768 - current_char.height)
                background.paste(current_char, left_pos, current_char)
        except Exception as e:
            print(f"Error opening current character image: {e}")

    if last_char_path and speaker_name.lower() != "narrator":
        try:
            last_char = load_and_resize_image(last_char_path, max_char_width, max_char_height)
            if last_char:
                right_pos = (1344 - int(1344 * 0.05) - last_char.width, 768 - last_char.height)
                background.paste(last_char, right_pos, last_char)
        except Exception as e:
            print(f"Error opening last character image: {e}")

    # Add dialogue box
    draw = ImageDraw.Draw(background)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
    except OSError:
        font = ImageFont.load_default()
    dialogue_box = Image.new('RGBA', (1344, 150), (0, 0, 0, 128))
    background.paste(dialogue_box, (0, 618), dialogue_box)

    # Wrap and draw text
    margin = 20
    max_width = 1344 - 2 * margin
    full_text = f"{speaker_name}: {dialogue_text}"
    wrapped_text = wrap(full_text, width=int(max_width / font.getlength("x")))
    y_text = 628
    for line in wrapped_text:
        line_width = draw.textlength(line, font=font)
        draw.text(((1344 - line_width) / 2, y_text), line, font=font, fill=(255, 255, 255, 255))
        y_text += font.size + 5

    # Save the frame
    frame_path = f'frame_{frame_number:04d}.png'
    background.save(frame_path)
    return frame_path

import subprocess
import os
from pydub import AudioSegment
import tempfile
import tqdm

def get_audio_duration(audio_file):
    audio = AudioSegment.from_file(audio_file)
    return len(audio) / 1000.0  # Convert milliseconds to seconds

import os
import subprocess
from pydub import AudioSegment
import tempfile
import tqdm

def create_video(scenes, output_file):
    frame_number = 0
    video_segments = []
    last_character = None

    with tempfile.TemporaryDirectory() as temp_dir:
        for scene in tqdm.tqdm(scenes):
            background_url = scene['background']
            for dialogue in scene['dialogues']:
                # Prepare frame
                current_char_path = None
                if dialogue['id'].lower() != "narrator":
                    current_char_path = os.path.join('/Users/cisco/Documents/CisStuff/corny', dialogue['character_image'])
                
                last_char_path = None
                if last_character and last_character['id'] != dialogue['id']:
                    last_char_path = os.path.join('/Users/cisco/Documents/CisStuff/corny', last_character['character_image'])

                frame_path = create_frame(background_url, current_char_path, last_char_path, dialogue['text'], frame_number, dialogue['id'])

                # Prepare audio
                audio_file = dialogue['tts_audio']

                # Generate video segment
                segment_file = os.path.join(temp_dir, f'segment_{frame_number}.mp4')
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-y',  # Overwrite output files without asking
                    '-loop', '1',
                    '-i', frame_path,
                    '-i', audio_file,
                    '-c:v', 'libx264',
                    '-tune', 'stillimage',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-shortest',
                    segment_file
                ]
                subprocess.run(ffmpeg_cmd, check=True)
                video_segments.append(segment_file)

                frame_number += 1

                # Update last character
                if dialogue['id'].lower() != "narrator":
                    last_character = dialogue
                    
        filelist_path = os.path.join(temp_dir, 'filelist.txt')
        with open(filelist_path, 'w') as f:
            for segment_file in video_segments:
                f.write(f"file '{segment_file}'\n")

        # Concatenate the segments
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # Overwrite output files without asking
            '-f', 'concat',
            '-safe', '0',
            '-i', filelist_path,
            '-c', 'copy',
            output_file
        ]
        subprocess.run(ffmpeg_cmd, check=True)

    print(f"Video created successfully: {output_file}")

if __name__ == "__main__":
    xml_file = "/Users/cisco/Documents/CisStuff/corny/screenplay.xml"  # Replace with your XML file path
    output_file = "output_video.mp4"
    scenes = parse_xml(xml_file)
    create_video(scenes, output_file)