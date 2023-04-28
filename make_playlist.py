import spotipy
import spotipy.util as util
import time

# 認証パート
username = 'hulot9'
my_id = '99309c621926435c998cdaf2f193aa33'  # clientID
my_secret = 'e807ad78ea424e05a24ce5e533313db9'  # client my_secret
redirect_uri = 'http://localhost:3000'

scope = 'user-library-read \
         user-read-playback-state \
         playlist-read-private \
         user-read-recently-played \
         playlist-read-collaborative \
         playlist-modify-public \
         playlist-modify-private'

token = util.prompt_for_user_token(username, scope, my_id, my_secret, redirect_uri)
spotify = spotipy.Spotify(auth=token)


# トラックのテンポを確認
def check_bpm(target_track):
    track_data = spotify.audio_features(target_track)
    bpm = track_data[0]['tempo']
    print(f'この曲のテンポは {bpm} です。')
    return bpm


# 追加先のプレイリストを作成 または 指定
def make_a_playlist():
    new_playlist_name = input('\n新しいプレイリストの名前を入力してください。：')
    spotify.user_playlist_create(user=username, name=new_playlist_name)
    lists_data = spotify.user_playlists(user=username)
    print(f'\nプレイリスト「{new_playlist_name}」を作成しました!')
    for i in range(lists_data['total']):
        playlist_name = lists_data['items'][i]['name']
        if playlist_name == new_playlist_name:
            url = lists_data['items'][i]['external_urls']['spotify']
            return url
            break
        else:
            pass


def search_playlists():
    url = ''
    lists_data = spotify.user_playlists(user=username)

    while True:
        to_playlist_name = input('\n追加先のプレイリスト名を教えてください。：')
        for i in range(lists_data['total']):
            playlist_name = lists_data['items'][i]['name']
            if playlist_name == to_playlist_name:
                url = lists_data['items'][i]['external_urls']['spotify']
                return url
                break
            else:
                pass

        if url == '':
            print('\n【!】指定したプレイリストが見当たりません。')
            make_playlist = input('\n新しいプレイリストを作成する場合は ”y” を、\
                                   \n作成しない場合は "n" を、\
                                   \nもう一度プレイリストを検索する場合は "c" を、\
                                   \n入力してください。：')
            if make_playlist == 'n':
                break
            elif make_playlist == 'c':
                pass
            elif make_playlist == 'y':
                url = make_a_playlist()
                return url


# プレイリストから各トラックのリンクを抽出
def make_urls_list(target_playlist):
    list_data = spotify.playlist_tracks(target_playlist)
    track_num = list_data['total']
    if track_num > 100:
        track_num = 100
    urls_list = []
    for i in range(track_num):
        track_url = list_data['items'][i]['track']['external_urls']['spotify']
        urls_list.append(track_url)
    return urls_list


# リストから好みのテンポのトラックを抽出
def make_favorite_bpm_list(urls_list, set_bpm, set_bpm_range):
    print('\nサヴェージを開始!')
    bpm_urls_list = []
    for i in range(len(urls_list)):
        track_url = urls_list[i]
        track_feature = spotify.audio_features(track_url)[0]
        time.sleep(1)
        bpm = track_feature['tempo']
        if (set_bpm - set_bpm_range) <= bpm <= (set_bpm + set_bpm_range):
            bpm_urls_list.append(track_url)
        else:
            pass
    print('サヴェージ完了!')
    return bpm_urls_list


# 実行
target_track = input("\n好みのテンポな曲のリンクを入力してください：")
set_bpm = check_bpm(target_track)
set_bpm_range = 5

while True:
    make_or_search = input('\n①追加先となるプレイリストを新しく作りますか？\
                            \n②元からあるプレイリストを追加先にしますか？\
                            \n\n①の場合は"1"を、②の場合は"2"を入力してください：')
    if make_or_search == "1":
        add_to_playlist = make_a_playlist()
        break
    elif make_or_search == "2":
        add_to_playlist = search_playlists()
        break
    else:
        print('\n【!】1 か 2 を入力してください。')

target_playlist = input('\nどのプレイリストをサヴェージしますか？\
                         \nプレイリストのリンクを入力してください：')
urls_list = make_urls_list(target_playlist)
favorite_bpm_urls_list = make_favorite_bpm_list(urls_list, set_bpm, set_bpm_range)
print('プレイリストに曲を追加中…')
spotify.user_playlist_add_tracks(username, add_to_playlist, favorite_bpm_urls_list)
print('完了!')
