import os
import random


def media_player(genre):
    media_dir = './media'
    sub_music_dir = None

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
        # music_list = os.listdir(media_dir)
        # dir_choice = random.choice(music_list)
        # choice_music = os.listdir(media_dir + '/' + dir_choice)
        # random_music = random.choice(choice_music)
        # sub_music_dir = dir_choice

    else:
        return None
    print("music_list {} ".format(music_list))
    return media_dir + '/' + sub_music_dir + '/' + random_music

if __name__ == "__main__":
    a = media_player('song')
    print(a)

