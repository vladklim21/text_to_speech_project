import os
import shutil
import requests
from django.shortcuts import render, redirect

# Settings
AUDIO_TYPE = 'mp3'
NUM_AUDIO = 5

# IP and port of container which generates audio
generator_docker_container_ip = 'localhost'
generator_docker_container_port = '8080'

# Making lists and dictionaries to store audio and prompts
audio_files_prompt_list = []
prompt_dict = dict(zip([f"output{i}.{AUDIO_TYPE}" for i in range(1, NUM_AUDIO+1)], [''] * NUM_AUDIO))


# Function that counts audio files in directory
def count_audio(directory):
    audio_count = 0
    audio_extensions = [f'.{AUDIO_TYPE}']
    for filename in os.listdir(directory):
        if any(filename.lower().endswith(ext) for ext in audio_extensions):
            audio_count += 1
    return audio_count


# Function that sends request to audio generator container which generates audio from prompt and saves it in audio_directory as output1.mp3
def generate_audio(prompt, audio_directory):
    get_response_to_url = f'http://{generator_docker_container_ip}:{generator_docker_container_port}/generate?prompt={prompt}'
    response = requests.get(get_response_to_url)

    filename = f'output.{AUDIO_TYPE}'
    response = requests.get(f'http://{generator_docker_container_ip}:{generator_docker_container_port}/audio/{filename}')

    if response.status_code == 200:
        audio_file_path = os.path.join(audio_directory, f"output1.{AUDIO_TYPE}")
        with open(audio_file_path, 'wb') as audio:
            audio.write(response.content)


def text_to_speech(request):
    # Global variables to make possible running the page when audio directory not exists
    global prompt_dict, audio_files_prompt_list

    # Creating directory if it not exists
    audio_directory = 'audio'
    if not os.path.exists(audio_directory):
        os.makedirs(audio_directory)

    # Counting audio files in directory
    audio_count = count_audio(audio_directory)

    if request.method == 'POST':

        # Getting prompt from POST request
        prompt = request.POST['prompt']

        if prompt != "":

            # Saving first output
            if audio_count == 0:
                generate_audio(prompt, audio_directory)
                prompt_dict[f'output1.{AUDIO_TYPE}'] = prompt

            # Saving outputs until NUM_AUDIO
            elif 0 < audio_count < NUM_AUDIO:
                list_of_audio = os.listdir('audio')

                for filename in sorted(list_of_audio, reverse=True):
                    num = int(filename[6])
                    os.rename(f'{audio_directory}/{filename}', f'{audio_directory}/output{num+1}.{AUDIO_TYPE}')
                    # Collecting prompt dict
                    prompt_dict[f'output{num + 1}.{AUDIO_TYPE}'] = prompt_dict[filename]

                generate_audio(prompt, audio_directory)
                prompt_dict[f'output1.{AUDIO_TYPE}'] = prompt

            # Saving outputs after reaching NUM_AUDIO with deleting last element
            elif audio_count >= NUM_AUDIO:
                list_of_audio = os.listdir('audio')

                for filename in sorted(list_of_audio, reverse=True):
                    num = int(filename[6])
                    os.rename(f'{audio_directory}/{filename}', f'{audio_directory}/output{num + 1}.{AUDIO_TYPE}')
                    # Collecting prompt dict
                    prompt_dict[f'output{num + 1}.{AUDIO_TYPE}'] = prompt_dict[filename]

                generate_audio(prompt, audio_directory)
                prompt_dict[f'output1.{AUDIO_TYPE}'] = prompt

                # WRITE A CODE TO REMOVE ALL FILES AFTER NUM_AUDIO
                os.remove(f'{audio_directory}/output{NUM_AUDIO + 1}.{AUDIO_TYPE}')
                del prompt_dict[f'output{NUM_AUDIO + 1}.{AUDIO_TYPE}']

        audio_count = count_audio(audio_directory)

        # Creating a list of pairs audio_directory and prompt for sending it to HTML page
        if audio_count > 0:
            audio_files_prompt_list = [[f"{audio_directory}/output{i}.{AUDIO_TYPE}", prompt_dict[f'output{i}.{AUDIO_TYPE}']] for i in range(1, audio_count + 1)]

    return render(request, 'text_to_speech.html', {'audio_files_prompt': audio_files_prompt_list})


def delete_audio_directory(request):
    audio_directory = 'audio'
    if os.path.exists(audio_directory):
        shutil.rmtree(audio_directory)
    return redirect('text_to_speech')
    #return render('text_to_speech.html')