import os
import random


def media_player(genre):
    media_dir = '../Media'

    classical_music_dir = 'classical_music'
    jazz_music_dir = 'jazz_music'
    pop_music_dir = 'pop_music'
    song_music_dir = 'song_music'

    if 'classic' == genre:
        music_list = os.listdir(media_dir + '/' + classical_music_dir)
        random_music = random.choice(music_list)
        sub_music_dir = classical_music_dir

    elif 'jazz' == genre:
        music_list = os.listdir(media_dir + '/' + jazz_music_dir)
        random_music = random.choice(music_list)
        sub_music_dir = jazz_music_dir

    elif 'pop' == genre:
        music_list = os.listdir(media_dir + '/' + pop_music_dir)
        random_music = random.choice(music_list)
        sub_music_dir = pop_music_dir

    elif 'song' == genre:
        music_list = os.listdir(media_dir + '/' + song_music_dir)
        random_music = random.choice(music_list)
        sub_music_dir = song_music_dir

    else:
        return None

    return media_dir + '/' + sub_music_dir + '/' + random_music
