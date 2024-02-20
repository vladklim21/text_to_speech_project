import os
import shutil

from gtts import gTTS
from django.shortcuts import render, redirect

NUM_AUDIO = 5
audio_files_prompt_list = []
prompt_dict = dict(zip([f"output{i}.mp3" for i in range(1, NUM_AUDIO+1)], [''] * NUM_AUDIO))


# Function that counts audio files in directory
def count_audio(directory):
    audio_count = 0
    audio_extensions = ['.mp3']
    for filename in os.listdir(directory):
        if any(filename.lower().endswith(ext) for ext in audio_extensions):
            audio_count += 1
    return audio_count


# Function that generates audio from prompt and saves it as output1.mp3
def generate_audio(prompt, audio_directory):
    tts = gTTS(text=prompt, lang='en', slow=False)
    audio_file_path = os.path.join(audio_directory, "output1.mp3")
    tts.save(audio_file_path)


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
                prompt_dict['output1.mp3'] = prompt

            # Saving outputs until NUM_AUDIO
            elif 0 < audio_count < NUM_AUDIO:
                list_of_audio = os.listdir('audio')

                for filename in sorted(list_of_audio, reverse=True):
                    num = int(filename[6])
                    os.rename(f'{audio_directory}/{filename}', f'{audio_directory}/output{num+1}.mp3')
                    # Collecting prompt dict
                    prompt_dict[f'output{num + 1}.mp3'] = prompt_dict[filename]

                generate_audio(prompt, audio_directory)
                prompt_dict['output1.mp3'] = prompt

            # Saving outputs after reaching NUM_AUDIO with deleting last element
            elif audio_count >= NUM_AUDIO:
                list_of_audio = os.listdir('audio')

                for filename in sorted(list_of_audio, reverse=True):
                    num = int(filename[6])
                    os.rename(f'{audio_directory}/{filename}', f'{audio_directory}/output{num + 1}.mp3')
                    # Collecting prompt dict
                    prompt_dict[f'output{num + 1}.mp3'] = prompt_dict[filename]

                generate_audio(prompt, audio_directory)
                prompt_dict['output1.mp3'] = prompt

                # WRITE A CODE TO REMOVE ALL FILES AFTER NUM_AUDIO
                os.remove(f'{audio_directory}/output{NUM_AUDIO + 1}.mp3')
                del prompt_dict[f'output{NUM_AUDIO + 1}.mp3']

        audio_count = count_audio(audio_directory)

        # Creating a list of pairs audio_directory and prompt for sending it to HTML page
        if audio_count > 0:
            audio_files_prompt_list = [[f"{audio_directory}/output{i}.mp3", prompt_dict[f'output{i}.mp3']] for i in range(1, audio_count + 1)]

    return render(request, 'text_to_speech.html', {'audio_files_prompt': audio_files_prompt_list})


def delete_audio_directory(request):
    audio_directory = 'audio'
    if os.path.exists(audio_directory):
        shutil.rmtree(audio_directory)
    return redirect('text_to_speech')
