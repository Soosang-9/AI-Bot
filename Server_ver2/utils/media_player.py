import os
import random


def media_player(text):
    if "클래식" in text:
        music_list = os.listdir("media/classical_music_dir")
        return random.choice(music_list)

    elif "재즈" in text:
        music_list = os.listdir("media/jazz_music_dir")
        return random.choice(music_list)

    elif "팝송" in text:
        music_list = os.listdir("media/pop_music_dir")
        return random.choice(music_list)

    elif "음악" in text:
        music_list = os.listdir("media/")
        dir_choice = random.choice(music_list)
        music_choice = os.listdir("media/" + dir_choice)
        return random.choice(music_choice)

    else:
        pass
