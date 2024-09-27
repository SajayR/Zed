import xml.etree.ElementTree as ET
import re

def validate_screenplay(file_path):
    try:
        # Read the file content
        with open(file_path, 'r') as file:
            content = file.read()

        # Parse the XML
        root = ET.fromstring(content)

        # Check overall structure
        if root.tag != 'scenes':
            print("Error: Root element should be 'scenes'")
            return False

        # Initialize counters and sets
        scene_count = 0
        character_set = set()
        background_count = 0

        # Iterate through scenes
        for scene in root.findall('scene'):
            scene_count += 1

            # Check background
            background = scene.find('background')
            if background is None:
                print(f"Error: Scene {scene_count} is missing a background")
            else:
                background_count += 1
                if len(background.text.strip()) < 10:
                    print(f"Warning: Scene {scene_count} has a very short background description")

            # Check dialogues
            dialogues = scene.find('dialogues')
            if dialogues is None:
                print(f"Error: Scene {scene_count} is missing dialogues")
            else:
                dialogue_count = 0
                for dialogue in dialogues:
                    dialogue_count += 1
                    character_id = dialogue.get('id')
                    if character_id:
                        character_set.add(character_id)
                    else:
                        print(f"Error: Dialogue {dialogue_count} in scene {scene_count} is missing a character id")
                
                #if dialogue_count < 3:
                    #print(f"Warning: Scene {scene_count} has fewer than 3 dialogues")

        # Print summary
        print(f"\nValidation Summary:")
        print(f"Total scenes: {scene_count}")
        print(f"Total backgrounds: {background_count}")
        print(f"Unique characters: {len(character_set)}")
        print(f"Characters: {', '.join(character_set)}")

        return True

    except ET.ParseError as e:
        print(f"XML Parsing Error: {e}")
        return False
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    screenplay_file = "screenplay.txt"
    if validate_screenplay(screenplay_file):
        print("\nScreenplay validation completed successfully.")
    else:
        print("\nScreenplay validation failed.")