# 配信アーカイブから音声コーパスの作成

## 環境設定
仮想環境を設定しておくことを推奨。  (Linux推奨)
```
python3 -m pip install requirements.txt
```

配信アーカイブを入れておくディレクトリを作る（**必ず必要**）  
`mkdir ./{archive}`  
デフォルトは`./source`

## 実行方法

```
python CreateCorpus.py
```

デバック時  
```
python CreateCorpus.py --debug
```

その他オプション  
`--pitch_threshold`：設定する閾値以上のピッチの音声を抽出する（デフォルト：350）  
`source_audio_dir`：配信アーカイブを入れておくディレクトリ（デフォルト："./source"）  
`result_dir`：出力されるコーパスが入るディレクトリ（デフォルト："./result"）  
`json_file`：一度コーパス化した配信アーカイブを記録するJSONファイル（デフォルト："./file_mapping.json"）  

## 配信アーカイブの取得

### mac OS の場合

**youtube-dl**
youtube-dl：YoutubeやTwitchの動画をダウンロード出来るライブラリ
[youtube-dl -公式-](https://github.com/ytdl-org/youtube-dl/)  

#### Instal
```
brew install youtube-dl
```

#### How to Use
```
youtube-dl 'URL' -x --audio-format wav
```


#### Config File の設定
一部の設定はconfigファイルとして設定している。[【Mac】ターミナルで動画ダウンロード](https://mac-ra.com/terminal-youtube-dl/)  

##### 作成

~/.config/youtube-dl にディレクトリを作成。ココにconfigファイルを作成

```config
-o '~/Desktop/youtube/MIKO_youtube_%(upload_data)s.%(ext)s'
```
コレは配信日を取得しファイル名にしている。
