from module.Setting import clear_directory
from module.fanctions import Delete_BGM,Separate_Audio,Select_Audio,make_script
from module.log import setup_logging

import argparse
import whisper # whisperのライブラリ
import gc
import os

# 引数の設定
def parse_args():
    parser = argparse.ArgumentParser(description="Audio Processing Script")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")
    parser.add_argument('--pitch_threshold', type=int, default=350, help="Pitch threshold value")
    parser.add_argument('--source_audio_dir', type=str, default="./source", help="Directory for source audio files")
    parser.add_argument('--result_dir', type=str, default="./result", help="Directory for transcription results")
    parser.add_argument('--json_file', type=str, default="file_mapping.json", help="JSON file name")
    
    return parser.parse_args()

def Specifying_Arguments(DEBUG):
    if DEBUG:
        # 元データを入れているディレクトリ
        source_audio_dir = "./source_test"
        # 文字起こしした結果を入れるディレクトリ
        result_dir = "./result_test"
        # jsonファイル
        json_file = "file_mapping_test.json"
    else:
        # 元データを入れているディレクトリ
        source_audio_dir = "./source"
        # 文字起こしした結果を入れるディレクトリ
        result_dir = "./result"
        # jsonファイル
        json_file = "file_mapping.json"

def main():
    # ログ設定を読み込む
    logger = setup_logging('main')
    args = parse_args()
    DEBUG = args.debug
    pitch_threshold = args.pitch_threshold
    source_audio_dir = args.source_audio_dir
    result_dir = args.result_dir
    json_file = args.json_file

    if DEBUG:
        source_audio_dir = source_audio_dir + "_test"
        result_dir = result_dir + "_test"
        # 新しいファイル名を作成
        base, ext = os.path.splitext(json_file)
        new_filename = f"{base}_text{ext}"
        # ファイル名を変更
        os.rename(json_file, new_filename)


    logger.info(f"Stage 1 <<< BGM除去 >>> ")
    Delete_BGM(source_audio_dir, "./demucs", json_file)

    logger.info(f"Stage 2 <<< 発話分割 >>> ")
    Separate_Audio("./demucs", "./Separate")

    logger.info(f"Stage 3 <<< 音声選択（高ピッチのみ） >>> ")
    Select_Audio("./Separate", "./high-pitch", pitch_threshold)

    logger.info(f"Stage 4 <<< 文字起こし >>> ")
    model = whisper.load_model("large-v2")  # ここで 'tiny', 'base', 'small', 'medium', 'large' のいずれかを選べます
    make_script("./high-pitch", result_dir, model, json_file)

    # 利用するディレクトリのリスト
    directories_to_clear = [
        "./demucs",  # DemucsでBGM除去したファイルを格納するディレクトリ
        "./Separate",  # 分割したデータを入れるディレクトリ
        "./high-pitch"  # 高ピッチのデータを入れるディレクトリ
    ]

    # 各ディレクトリに対して削除処理を実行
    for directory in directories_to_clear:
        clear_directory(directory)

    # モデルに対する参照を削除
    del model

    # ガベージコレクションを強制的に実行
    gc.collect()

if __name__ == "__main__":
    main()