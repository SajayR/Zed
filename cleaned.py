import replicate
from pymongo import MongoClient
import PyPDF2
import os
import google.generativeai as genai
import xml.etree.ElementTree as ET
import json
import tqdm
import tts
import random
from PIL import Image
import random
import string
from rembg import remove
import urllib.request
import re
from groq import Groq
from pydub import AudioSegment
import vid_gen

from google.generativeai.types import HarmCategory, HarmBlockThreshold
client_groq = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

client = MongoClient('mongodb://localhost:27017/')
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
malevoices=["vits-eng-2", "vits-eng-4", "vits-eng-5", "vits-eng-6", "vits-eng-10", "vits-eng-11", "vits-eng-12", "vits-eng-16", "vits-eng-18", "vits-eng-19", "vits-eng-25", "vits-eng-26", "vits-eng-28", "vits-eng-30", "vits-eng-31", "vits-eng-33", "vits-eng-34", "vits-eng-36", "vits-eng-39", "vits-eng-42", "vits-eng-44", "vits-eng-47", "vits-eng-56", "vits-eng-59", "vits-eng-64", "vits-eng-66", "vits-eng-69", "vits-eng-71", "vits-eng-74", "vits-eng-76", "vits-eng-77", "vits-eng-78", "vits-eng-82", "vits-eng-83", "vits-eng-86", "vits-eng-88", "vits-eng-89", "vits-eng-97", "vits-eng-98", "vits-eng-100", "vits-eng-101", "vits-eng-102", "vits-eng-103", "vits-eng-107", "vits-eng-109", "vits-eng-110", "vits-eng-111", "vits-eng-115", "vits-eng-116", "vits-eng-118", "vits-eng-121", "vits-eng-122", "vits-eng-123", "vits-eng-124", "vits-eng-125", "vits-eng-127", "vits-eng-128", "vits-eng-130", "vits-eng-131", "vits-eng-132", "vits-eng-133", "vits-eng-139", "vits-eng-141", "vits-eng-143", "vits-eng-160", "vits-eng-163", "vits-eng-164", "vits-eng-165", "vits-eng-171", "vits-eng-172", "vits-eng-173", "vits-eng-175", "vits-eng-177", "vits-eng-180", "vits-eng-181", "vits-eng-184", "vits-eng-185", "vits-eng-186", "vits-eng-192", "vits-eng-193", "vits-eng-194", "vits-eng-198", "vits-eng-199", "vits-eng-200", "vits-eng-201", "vits-eng-202", "vits-eng-203", "vits-eng-205", "vits-eng-217", "vits-eng-221", "vits-eng-222", "vits-eng-223", "vits-eng-226", "vits-eng-229", "vits-eng-232", "vits-eng-233", "vits-eng-235", "vits-eng-237", "vits-eng-238", "vits-eng-239"]
femalevoices=["vits-eng-3", "vits-eng-7", "vits-eng-8", "vits-eng-9", "vits-eng-13", "vits-eng-14", "vits-eng-15", "vits-eng-17", "vits-eng-20", "vits-eng-21", "vits-eng-22", "vits-eng-23", "vits-eng-24", "vits-eng-27", "vits-eng-29", "vits-eng-32", "vits-eng-35", "vits-eng-37", "vits-eng-38", "vits-eng-40", "vits-eng-41", "vits-eng-43", "vits-eng-45", "vits-eng-46", "vits-eng-48", "vits-eng-49", "vits-eng-50", "vits-eng-51", "vits-eng-52", "vits-eng-53", "vits-eng-54", "vits-eng-55", "vits-eng-57", "vits-eng-58", "vits-eng-60", "vits-eng-61", "vits-eng-62", "vits-eng-63", "vits-eng-65", "vits-eng-67", "vits-eng-68", "vits-eng-70", "vits-eng-72", "vits-eng-73", "vits-eng-75", "vits-eng-79", "vits-eng-80", "vits-eng-81", "vits-eng-84", "vits-eng-85", "vits-eng-87", "vits-eng-90", "vits-eng-91", "vits-eng-92", "vits-eng-93", "vits-eng-94", "vits-eng-95", "vits-eng-96", "vits-eng-99", "vits-eng-104", "vits-eng-105", "vits-eng-106", "vits-eng-108", "vits-eng-112", "vits-eng-113", "vits-eng-114", "vits-eng-117", "vits-eng-119", "vits-eng-120", "vits-eng-126", "vits-eng-129", "vits-eng-134", "vits-eng-136", "vits-eng-137", "vits-eng-150", "vits-eng-157", "vits-eng-159", "vits-eng-166", "vits-eng-167", "vits-eng-168", "vits-eng-169", "vits-eng-170", "vits-eng-174", "vits-eng-178", "vits-eng-179", "vits-eng-187", "vits-eng-188", "vits-eng-189", "vits-eng-190", "vits-eng-191", "vits-eng-195", "vits-eng-196", "vits-eng-197", "vits-eng-204", "vits-eng-207", "vits-eng-209", "vits-eng-210", "vits-eng-212", "vits-eng-213", "vits-eng-214"]
femalevoices=["angela-merkel", "angie", "anna-kendrick", "ariana-grande", "beyonce", "billie-eilish", "cardi-b", "demi-lovato", "elizabeth-holmes", "ellen-degeneres", "emma-watson", "greta-thunberg", "hillary-clinton", "kamala-harris", "kardashian", "pokimane", "rachel-maddow", "scarlett-johansson", "taylor-swift", "uk-female-1", "us-female-7", "us-female-8", "us-female-9", "us-female-10", "us-female-11", "us-female-12", "us-female-13", "us-female-14", "us-female-15", "us-female-16", "us-female-17", "us-female-18"]
malevoices=["50-cent", "alex-jones", "anderson-cooper","andrew-tate","andrew-yang", "anthony-fauci", "antonio-banderas", "arnold-schwarzenegger", "ben-affleck", "ben-shapiro", "bernie-sanders", "bill-clinton", "bill-gates", "bill-oreilly", "casey-affleck", "charlamagne", "conor-mcgregor", "darth-vader", "dj-khaled", "donald-trump", "dr-dre", "dr-phil", "drake", "dwayne-johnson", "elon-musk", "gilbert-gottfried", "jason-alexander", "jay-z", "jeff-bezos", "jerry-seinfeld", "jim-cramer", "joe-biden", "joe-rogan", "john-cena", "jordan-peterson", "justin-bieber", "justin-trudeau", "kanye-west", "kevin-hart", "lex-fridman", "lil-wayne", "mark-zuckerberg", "martin-shkreli", "matt-damon", "matthew-mcconaughey", "mike-tyson", "patrick-stewart", "paul-mccartney", "prince-harry", "rober-downey-jr", "ron-desantis", "sam-altman", "samuel-jackson", "sbf", "sean-hannity", "snoop-dogg", "stephen-hawking", "tucker-carlson", "tupac", "warren-buffett", "will-smith", "william", "uk-male-1", "uk-male-2", "uk-male-3", "uk-male-4", "uk-male-5", "uk-male-6", "uk-male-7", "uk-male-8", "us-male-6", "us-male-7", "us-male-8", "us-male-9", "us-male-10", "us-male-11", "us-male-12", "us-male-13", "us-male-14", "us-male-15", "us-male-16"]

def clear_background(image_path: str)->str:
    print("Path recieved ", image_path)
    with open(image_path, 'rb') as img_file:
        img_data = img_file.read()
    
    output = remove(img_data)
    output_path = f"clear_{image_path}"
    with open(output_path, 'wb') as out_file:
        out_file.write(output)
    return output_path

def generate_background(prompt: str) -> str:
    output = replicate.run(
        "black-forest-labs/flux-schnell",
        input={
            "prompt": prompt+ " cartoon look.",
            "go_fast": True,
            "num_outputs": 1,
            "aspect_ratio": "16:9",
            "output_format": "webp",
            "output_quality": 80,
            "disable_safety_checker": True
        }
    )
    return output[0] #returns the image path (online link)

def check_xml_structure(xml_string):
    try:
        root = ET.fromstring(xml_string)
        # Pretty-print the XML structure
        ET.dump(root)
        print("XML structure is valid.")
        return True
    except ET.ParseError as e:
        print(f"XML structure is invalid: {e}")
        return False 

def generate_character(prompt: str) -> str:
    output = replicate.run(
        "black-forest-labs/flux-schnell",
        input={
            "prompt": prompt+ " cartoon style, chibi, white background, only person",
            "go_fast": True,
            "num_outputs": 1,
            "aspect_ratio": "1:1",
            "output_format": "webp",
            "output_quality": 80,
            "disable_safety_checker": True
        }
    )
    return output[0] #returns the image path (online link)

def extract_text_from_pdf(pdf_path: str) -> str:
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def get_new_character_info(character_name: str, novel_text: str) -> dict:
    instruction = f"""<novel>{novel_text}</novel>
    Generate detailed information for the character named {character_name}. 
    Return it in XML format as follows:
    <character>
    <name>{character_name}</name>
    <description>An elaborate and well-described description of the character's physical appearance. Do not include anything other than the PHYSICAL description of the character.</description>
    <gender>their gender (male or female)</gender>
    </character>
    """
    
    generation_config = {
        "temperature": 0.3,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
        #"safety_settings": [{"harm_block_level": "block_none"}],
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    )
    chat_session = model.start_chat(history=[])
    while True:
        try:
            response = chat_session.send_message(instruction).text
            break
        except Exception as e:
            print(e)
            continue
    response = re.search(r'<character>.*?</character>', response, re.DOTALL)
    xml_data = ET.fromstring(response.group(0))
    character_info = {
        "name": xml_data.find("name").text,
        "description": xml_data.find("description").text,
        "gender": xml_data.find("gender").text
    }

    return character_info

from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument

def get_or_create_character(db, character_name: str, novel_text: str) -> dict:
    characters_collection = db['characters']

    # Attempt to insert a placeholder character document
    try:
        character = characters_collection.find_one_and_update(
            {"name": character_name},
            {"$setOnInsert": {
                "name": character_name,
                "description": None,
                "gender": None,
                "image": None,
                "voice": None
            }},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
    except DuplicateKeyError:
        # If a duplicate key error occurs, retrieve the existing character
        character = characters_collection.find_one({"name": character_name})

    # If the character info is incomplete, generate and update it
    if character['description'] is None:
        character_info = get_new_character_info(character_name, novel_text)
        image_online_link = generate_character(character_info["description"])
        os.makedirs('/Users/cisco/Documents/CisStuff/corny/characters', exist_ok=True)
        random_filename = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + ".png"
        offline_image_path = os.path.join('characters', random_filename)
        urllib.request.urlretrieve(image_online_link, offline_image_path)
        image = clear_background(offline_image_path)
        voicelist = femalevoices if character_info["gender"].lower() == "female" else malevoices
        voice = random.choice(voicelist) if character_info["name"].lower() != "narrator" else "morgan-freeman"
        if character_info["name"].lower() != "narrator":
            voicelist.remove(voice)

        # Update the character document
        characters_collection.update_one(
            {"name": character_name},
            {"$set": {
                "description": character_info["description"],
                "gender": character_info["gender"],
                "image": image,
                "voice": voice
            }}
        )
        # Retrieve the updated character
        character = characters_collection.find_one({"name": character_name})

    return character


    

def get_scene_info(section_text: str, character_names: list) -> str:
        screenplay_prompt=f"""Your job is to return the entire scene properly structured in xml format, along with a background setting and its description. Do NOT mention any actions that characters are doing in the description tags. There should be ATLEAST 5-6 dialogues for each scene, if there are not then do NOT make the scene. The 'Narrator' is also considered a character, btw, but that doesn't mean that the scenes should be Narrator-heavy. If a character in the dialogues is in the list:{character_names}, use only the EXACT name from the list, even if the name you've come up with is different for that character. \nExample\n<scenes>\n<scene>\n<background> [An extremely elaborate description of the background to be used] </background>\n<dialogues>\n<dialogue id="character_name"> Dialogue.... </dialogue>\n<dialogue id="character_name"> Dialogue.... </dialogue>\n.\n.\n.\n</dialogues>\n</scene>\n.\n.\n.\n</scenes>
                        Here's a few example descriptions: '<background>A quiet suburban street, with neat gardens and tidy curtains. The houses are small and ordinary, with old-fashioned street lamps casting a warm glow. The atmosphere is quiet and suburban.</description>
                                                        <background>A living room with a TV, armchairs, and a coffee table. The room is tidy and ordinary, with a hint of suburban comfort.</description>'
                        Examples of some scenes: 
                        <scene>
                            <background>A dimly lit street in the Muggle world, with old-fashioned street lamps casting a warm glow. The houses are small and ordinary, with neat gardens and tidy curtains. The atmosphere is quiet and suburban.</background>
                            <dialogues>
                            <dialogue id="Narrator">"The cat's tail twitched and its eyes narrowed."</dialogue>
                            <dialogue id="Albus Dumbledore">"I should have known."</dialogue>
                            <dialogue id="Albus Dumbledore">"Fancy seeing you here, Professor McGonagall."</dialogue>
                            <dialogue id="Professor McGonagall">"How did you know it was me?"</dialogue>
                            <dialogue id="Albus Dumbledore">"My dear Professor, I've never seen a cat sit so stiffly."</dialogue>
                            <dialogue id="Professor McGonagall">"You'd be stiff if you'd been sitting on a brick wall all day."</dialogue>
                            </dialogues>
                            </scene>

                            <scene>
                            <background>The platform, with the red-haired family saying their goodbyes. The mother is fussing over Ron, trying to clean his nose.</background>
                            <dialogues>
                                <dialogue id="Mrs. Weasley">Ron, you've got something on your nose.</dialogue>
                                <dialogue id="Ron">Weasley>Mom -- geroff!</dialogue>
                                <dialogue id="Fred">Aaah, has ickle Ronnie got somefink on his nosie?</dialogue>
                                <dialogue id="Ron">Weasley>Shut up,</dialogue>
                                <dialogue id="Mrs. Weasley">Where's Percy?</dialogue>
                                <dialogue id="Percy">Weasley>He's coming now.</dialogue>
                            </dialogues>
                        </scene>

        """

        chat_session = client_groq.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are an experienced screen adapter for written novels. You will properly structure a script for a visual depiction of a section of a written novel as requested by the user. FOLLOW THE FORMAT and REFRAIN FROM saying anything except what is required of you, that is the XML."
        },

        {
            "role": "user",
            "content": "<novel>"+section_text+"</novel> "+screenplay_prompt,
        }
    ],
    model="llama3-70b-8192",

    temperature=0.3,
)

        response = chat_session.choices[0].message.content

        #response contains text, and then a xml section with the starting and ending tag <scenes>
        #we need to extract the text between these tags
        # print(response)
        response_text = response.split("<scenes>")[0] + "<scenes>" + response.split("<scenes>")[1].split("</scenes>")[0] + "</scenes>"

        return response_text

import concurrent.futures
from functools import partial

def process_dialogue(dialogue, db, novel_text, character_info_cache):
    if 'character_image' not in dialogue.attrib or 'character_voice' not in dialogue.attrib or 'tts_audio' not in dialogue.attrib:
        character_name = dialogue.get('id')
        if character_name not in character_info_cache:
            character_info = get_or_create_character(db, character_name, novel_text)
            character_info_cache[character_name] = character_info
        else:
            character_info = character_info_cache[character_name]

        dialogue.set('character_image', character_info['image'])
        dialogue.set('character_voice', character_info['voice'])
        
        # Generate TTS audio
        dialogue_text = dialogue.text
        while True:
            tts_audio_file = tts.get_audio(dialogue_text, voice_id=character_info['voice'])
            # Check if the audio file was generated successfully and is not corrupted
            if os.path.exists(tts_audio_file):
                try:
                    # Attempt to open and read the audio file
                    with open(tts_audio_file, 'rb') as audio_file:
                        audio_data = audio_file.read()
                    
                    # Check if the file is not empty
                    if len(audio_data) > 0:
                        # Try to load the audio file using pydub
                        AudioSegment.from_file(tts_audio_file)
                        # If we reach this point, the audio file is valid
                        break
                    else:
                        print(f"Audio file for '{dialogue_text}' is empty. Regenerating...")
                except Exception as e:
                    print(f"Audio file for '{dialogue_text}' is corrupted: {str(e)}. Regenerating...")
                
                # If we're here, the file was corrupted or empty, so we remove it and try again
                os.remove(tts_audio_file)
            else:
                print(f"Failed to generate audio for '{dialogue_text}'. Retrying...")
        dialogue.set('tts_audio', tts_audio_file)
    
    return dialogue

def process_scenes(screenplay_file: str, db, novel_text: str, start_index: int = 0):
    print("Processing scenes")
    if os.path.exists(screenplay_file):
        tree = ET.parse(screenplay_file)
        root = tree.getroot()
    else:
        root = ET.Element("scenes")
        tree = ET.ElementTree(root)

    scenes = root.findall('scene')
    character_info_cache = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for i, scene in tqdm.tqdm(enumerate(scenes[start_index:], start=start_index)):
            # Generate background image
            background = scene.find('background')
            if background is not None and 'image' not in background.attrib:
                background_prompt = background.text
                future = executor.submit(generate_background, background_prompt)
                background.set('image', future.result())
            
            # Process dialogues
            dialogues = scene.find('dialogues')
            if dialogues is not None:
                process_dialogue_partial = partial(process_dialogue, db=db, novel_text=novel_text, character_info_cache=character_info_cache)
                processed_dialogues = list(executor.map(process_dialogue_partial, dialogues.findall('dialogue')))
                dialogues.clear()
                for processed_dialogue in processed_dialogues:
                    dialogues.append(processed_dialogue)
            
            # Save progress after each scene
            tree.write(screenplay_file, encoding='unicode')
            
            # Save the current index
            with open('progress.txt', 'w') as f:
                f.write(str(i + 1))

def generate_screenplay(text, num_char_at_a_time, screenplay_file, character_names):
    with open(screenplay_file, "w") as file:
        file.write("<scenes>")
    
    for i in tqdm.tqdm(range(0, len(text), num_char_at_a_time)):
        section_text = text[i:i+num_char_at_a_time]
        while True:
            try:
                scene_text = get_scene_info(section_text, character_names)
                scene_text = process_scene_text(scene_text, i, num_char_at_a_time, len(text))
                
                if check_xml_structure("<scenes>" + scene_text + "</scenes>"):
                    update_character_names(scene_text, character_names)
                    
                    with open(screenplay_file, "a") as file:
                        file.write(scene_text)
                    break
                else:
                    print(f"Invalid scene XML, retrying scene from offset {i}")
            except Exception as e:
                print(f"Error processing scene: {e}")
                continue

    with open(screenplay_file, "a") as file:
        file.write("</scenes>")


def process_scene_text(scene_text, i, num_char_at_a_time, total_length):
    if i == 0:
        scene_text = scene_text.strip().rstrip('</scenes>')
    elif i + num_char_at_a_time < total_length:
        scene_text = scene_text.replace('<scenes>', '').replace('</scenes>', '').strip()
    else:
        scene_text = scene_text.lstrip('<scenes>').strip()

    if "xml" in scene_text:
        scene_text = scene_text.replace("xml", "")

    pattern = re.compile(r'(<scene>.*?</scene>)', re.DOTALL)
    matches = pattern.findall(scene_text)
    scene_text = ' '.join(matches)
    
    return scene_text

def update_character_names(scene_text, character_names):
    scene_root = ET.fromstring("<scenes>" + scene_text + "</scenes>")
    for scene in scene_root.findall('scene'):
        dialogues = scene.find('dialogues')
        if dialogues is not None:
            for dialogue in dialogues:
                character_id = dialogue.get('id')
                if character_id and character_id not in character_names:
                    character_names.append(character_id)
    print(f"Updated character names: {character_names}")

def main(file_path: str):
    text = extract_text_from_pdf(file_path)
    pdf_name = os.path.splitext(os.path.basename(file_path))[0]
    db = client[pdf_name.replace(" ", "_")]
    characters_collection = db['characters']
    characters_collection.create_index("name", unique=True)

    num_char_at_a_time = 2048
    screenplay_file = "screenplay.xml"

    if not os.path.exists(screenplay_file):
        print("Generating screenplay")
        db['characters'].delete_many({})
        print("Databases cleared. Ready to generate screenplay.")
        generate_screenplay(text, num_char_at_a_time, screenplay_file, [])

        # Collect all character names
        character_names = collect_character_names(screenplay_file)
        print(f"Found characters: {character_names}")

        # Create character info for all characters
        for character_name in character_names:
            get_or_create_character(db, character_name, text)

        # Now process scenes
        process_scenes(screenplay_file, db, text)

    print("Screenplay processing complete. Updated XML saved to", screenplay_file)

    screenplay_file = "/Users/cisco/Documents/CisStuff/corny/screenplay.xml"
    output_video_file = f"{pdf_name}.mp4"
    scenes=vid_gen.parse_xml(screenplay_file)
    vid_gen.create_video(scenes, output_video_file)

  
    
def collect_character_names(screenplay_file):
    tree = ET.parse(screenplay_file)
    root = tree.getroot()
    character_names = set()
    for scene in root.findall('scene'):
        dialogues = scene.find('dialogues')
        if dialogues is not None:
            for dialogue in dialogues.findall('dialogue'):
                character_name = dialogue.get('id')
                if character_name:
                    character_names.add(character_name)
    return character_names


if __name__ == "__main__":
    test_pdf_path = "/Users/cisco/Documents/CisStuff/corny/harry_tiny.pdf"
    main(test_pdf_path)