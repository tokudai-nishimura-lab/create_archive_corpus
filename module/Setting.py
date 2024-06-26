import logging
import os
import json
import shutil # ファイルを移動させる
import subprocess # コマンド実行のためのライブラリ

import module.log as log
# ログ設定を読み込む
logger = log.setup_logging('Setting')

####################
#   音声変換関係   #
####################

def stereo_to_mono(input_file_path, output_file_path):
    # ffmpegコマンドを構築
    command = [
        'ffmpeg',
        '-i', input_file_path,  # 入力ファイル
        '-ac', '1',  # オーディオチャンネル数を1に設定
        '-ar', '48000',  # サンプリングレートを指定
        output_file_path  # 出力ファイル
    ]

    # subprocessを使用してffmpegコマンドを実行
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        logger.info('Command executed successfully:')
        # logger.info('Command executed successfully:\n%s', result.stdout)

    except subprocess.CalledProcessError as e:
        logging.error('Command failed with error:\n%s', e.stderr)

####################
# JSONファイル関係 #
####################

def load_mapping(filename):
    """JSON ファイルからマッピングを読み込む"""
    try:
        with open(filename, 'r') as f:
            mapping = json.load(f)
        return mapping
    except FileNotFoundError:
        return {}

def save_mapping(mapping, filename):
    """マッピングを JSON ファイルとして保存する"""
    with open(filename, 'w') as f:
        json.dump(mapping, f, indent=4)

def update_mapping(archive_files, filename):
    """アーカイブファイルのリストを更新し、マッピングを保存する"""
    mapping = load_mapping(filename)
    new_files = []
    start_index = max(mapping.values(), default=0) + 1
    updated = False

    for archive in archive_files:
        if archive not in mapping:
            mapping[archive] = start_index
            new_files.append(archive)
            start_index += 1
            updated = True

    if updated:
        save_mapping(mapping, filename)
        logger.info(f"File list to be processed : {new_files}")
    else:
        logger.info(f"No update.")


    return new_files, mapping

####################
# ディレクトリ関係 #
####################
def make_dir(dir_path):
    """ディレクトリパスを確認してディレクトリが存在しなければ作る

    Args:
        dir_path (path): directory path.
    """
    if os.path.exists(dir_path):
        logger.info(f"{dir_path} is already created.")
    else :
        # 自動でフォルダを作成
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"Create {dir_path}.")

def clear_directory(directory):
    """
    指定されたディレクトリが存在する場合、ディレクトリとその内容を再帰的に削除します。
    存在しない場合、ディレクトリが存在しないことを表示します。
    """
    if os.path.exists(directory):
        shutil.rmtree(directory)
        logger.info(f"Directory '{directory}' has been deleted.")
    else:
        logger.info(f"The directory '{directory}' does not exist.")