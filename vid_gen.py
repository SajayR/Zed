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

def create_frame(background_url, left_char_path, right_char_path, dialogue_text, frame_number):
    # Download and open background image
    try:
        response = requests.get(background_url)
        response.raise_for_status()
        background = Image.open(BytesIO(response.content)).convert('RGBA')
        background = background.resize((1344, 768))
    except (requests.RequestException, IOError) as e:
        print(f"Error downloading or opening background image: {e}")
        background = Image.new('RGBA', (1344, 768), (0, 0, 0, 255))  # Create a black background as fallback

    # Function to load image from URL or local path
    def load_image(path):
        if "https://" in path:
            response = requests.get(path)
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert('RGBA')
        else:
            return Image.open(path).convert('RGBA')

    # Add characters if paths are provided
    if left_char_path:
        try:
            left_char = load_image(left_char_path)
            left_char = left_char.resize((int(1344*0.3), int(768*0.8)))
            background.paste(left_char, (int(1344*0.1), int(768*0.2)), left_char)
        except Exception as e:
            print(f"Error opening left character image: {e}")

    if right_char_path:
        try:
            right_char = load_image(right_char_path)
            right_char = right_char.resize((int(1344*0.3), int(768*0.8)))
            background.paste(right_char, (int(1344*0.6), int(768*0.2)), right_char)
        except Exception as e:
            print(f"Error opening right character image: {e}")

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
    wrapped_text = wrap(dialogue_text, width=int(max_width / font.getlength("x")))
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

def create_video(scenes, output_file):
    frame_files = []
    audio_files = []
    frame_number = 0

    with tempfile.TemporaryDirectory() as temp_dir:
        for scene in tqdm.tqdm(scenes):
            background_url = scene['background']
            for dialogue in scene['dialogues']:
                if dialogue['id'] != "Narrator":
                    left_char_path = os.path.join('/Users/cisco/Documents/CisStuff/corny', dialogue['character_image'])
                else:
                    left_char_path = None
                right_char_path = None  # We're not handling multiple characters in this example
                
                frame_path = create_frame(background_url, left_char_path, right_char_path, dialogue['text'], frame_number)
                frame_files.append(frame_path)
                print(dialogue)
                audio_file = dialogue['tts_audio']
                if os.path.exists(audio_file):
                    audio_files.append(audio_file)
                else:
                    # Create a silent audio file if the TTS audio doesn't exist
                    silent_audio = AudioSegment.silent(duration=3000)  # 3 seconds of silence
                    silent_audio_path = os.path.join(temp_dir, f"silent_{frame_number}.wav")
                    silent_audio.export(silent_audio_path, format="wav")
                    audio_files.append(silent_audio_path)
                
                frame_number += 1

        # Prepare ffmpeg command
        ffmpeg_cmd = ['ffmpeg']
        
        # Add input files
        for frame, audio in zip(frame_files, audio_files):
            ffmpeg_cmd.extend(['-i', frame, '-i', audio])
        
        # Prepare filter complex
        filter_complex = []
        for i in range(len(frame_files)):
            filter_complex.append(f'[{i*2}:v][{i*2+1}:a]')
        
        filter_complex.append(f'concat=n={len(frame_files)}:v=1:a=1[outv][outa]')
        
        # Complete the ffmpeg command
        ffmpeg_cmd.extend([
            '-filter_complex', ''.join(filter_complex),
            '-map', '[outv]',
            '-map', '[outa]',
            output_file
        ])
        
        # Execute ffmpeg command
        try:
            subprocess.run(ffmpeg_cmd, check=True)
            print(f"Video created successfully: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error creating video: {e}")

        # Clean up frame files
        for file in frame_files:
            os.remove(file)

if __name__ == "__main__":
    xml_file = "/Users/cisco/Documents/CisStuff/corny/screenplay.xml"  # Replace with your XML file path
    output_file = "output_video.mp4"
    scenes = parse_xml(xml_file)
    create_video(scenes, output_file)