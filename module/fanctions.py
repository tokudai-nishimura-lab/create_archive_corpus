
import webrtcvad
import parselmouth

import subprocess # コマンド実行のためのライブラリ
import shutil # ファイルを移動させる
import os
import whisper # whisperのライブラリ

import module.Setting as Setting
import module.transcript as transcript
import module.VADSetting as VADSetting
import module.log as log

# ログ設定を読み込む
logger = log.setup_logging('Facntions')

# 五十音のリスト（基本、濁音、半濁音を含む）
syllables = [
    'あ', 'い', 'う', 'え', 'お',
    'か', 'き', 'く', 'け', 'こ',
    'さ', 'し', 'す', 'せ', 'そ',
    'た', 'ち', 'つ', 'て', 'と',
    'な', 'に', 'ぬ', 'ね', 'の',
    'は', 'ひ', 'ふ', 'へ', 'ほ',
    'ま', 'み', 'む', 'め', 'も',
    'や', 'ゆ', 'よ',
    'ゃ','ゅ','ょ','っ','゛',
    'ら', 'り', 'る', 'れ', 'ろ',
    'わ', 'を', 'ん',
    'が', 'ぎ', 'ぐ', 'げ', 'ご',
    'ざ', 'じ', 'ず', 'ぜ', 'ぞ',
    'だ', 'ぢ', 'づ', 'で', 'ど',
    'ば', 'び', 'ぶ', 'べ', 'ぼ',
    'ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ'
]

# パターンリストの生成
patterns = transcript.generate_patterns(syllables)

def Delete_BGM(source_audio_dir, demucs_dir, json_file):
    """
    demucsを使ってBGMを除去する
    """
    Setting.make_dir(demucs_dir) # Demucs用ディレクトリの作成
    # 元データの音声ファイルをリストで取得
    source_audio_list = os.listdir(source_audio_dir)
    source_audio_list = sorted(source_audio_list)
    new_files, mapping = Setting.update_mapping(source_audio_list, json_file)
    for source_audio_filename in new_files:
        logger.info(f"==================================================")
        logger.info(f"Files to be processed : {source_audio_filename}")
        # 元音声のパスを作成
        source_audio_path = os.path.join(source_audio_dir, source_audio_filename)
        # ファイル名から拡張子を除いた部分を取得
        demucs_dir_name = source_audio_filename.split(".")[0]
        # Demucs用フォルダのパスを作成
        demucs_dir_path = os.path.join(demucs_dir, demucs_dir_name)

        # ファイル名から拡張子を除いた部分を取得
        delete_bgm_name = source_audio_filename.split(".")[0] + "_vocals." +source_audio_filename.split(".")[1]
        # Demucs用フォルダのパスを作成
        delete_bgm_path = os.path.join(demucs_dir, delete_bgm_name)

        # 音声ファイルが既に存在するか確認
        if os.path.exists(delete_bgm_path):
            logger.info(f"Skip because the BGM can already be removed.")
            continue # 以下の処理はスキップされる

        # 自動でフォルダを作成
        os.makedirs(demucs_dir_path, exist_ok=True)

        # demucsコマンドの構築
        command = (
            f'demucs --two-stems vocals --filename "{{track}}_{{stem}}.{{ext}}" -n htdemucs '
            f'-o \'{demucs_dir_path}\' \'{source_audio_path}\''
        )

        # 実行するコマンドを表示
        logger.info(f"Commands: {command}")

        try:
            # コマンドの実行
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            logger.info(f"Command success : {source_audio_path}")
            logger.info("STDOUT:")
            logger.info(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.info(f"Command failed : {source_audio_path}")
            logger.info("STDERR:")
            logger.info(e.stderr)

        # BGM除去音声ファイルパス
        delete_bgm_file_path = os.path.join(demucs_dir_path, 'htdemucs',delete_bgm_name)
        Setting.stereo_to_mono(delete_bgm_file_path,os.path.join(demucs_dir,delete_bgm_name))

        # ディレクトリの削除（ディレクトリが空でなくても削除されます）
        try:
            shutil.rmtree(demucs_dir_path)
            logger.info("htdemucs directory has been deleted.")
        except OSError as e:
            logger.info(f"Failed to delete htdemucs directory : {e}")

def Separate_Audio(demucs_dir, Separate_audio_dir):
    """
    webrtcvadを使って音声ファイルを発話区間で分割する
    """
    Setting.make_dir(Separate_audio_dir) # 音声分離用ディレクトリの作成

    # 元データの音声ファイルをリストで取得
    demucs_audio_list = os.listdir(demucs_dir)
    demucs_audio_list = sorted(demucs_audio_list)
    for demucs_audio_filename in demucs_audio_list:
        logger.info(f"Files to be processed : {demucs_audio_filename}")
        # ファイル名から拡張子を除いた部分を取得
        Separate_dir_name = demucs_audio_filename.split(".")[0]
        # 新しいフォルダのパスを作成
        Separate_dir_path = os.path.join(Separate_audio_dir, Separate_dir_name)

        # フォルダが既に存在するか確認
        if os.path.exists(Separate_dir_path):
            logger.info(f"Skip because it is already split.")
            continue

        # 自動でフォルダを作成
        os.makedirs(Separate_dir_path, exist_ok=True)

        vad = webrtcvad.Vad()

        # set aggressiveness from 0 to 3
        vad.set_mode(3)

        audio, sample_rate = VADSetting.read_wave(os.path.join(demucs_dir, demucs_audio_filename))
        frames = VADSetting.frame_generator(30, audio, sample_rate)
        frames = list(frames)
        segments = VADSetting.vad_collector(sample_rate, 30, 300, vad, frames)
        for i, segment in enumerate(segments):
                file_pattern = Separate_dir_name + "-%002d.wav"
                path = os.path.join(os.path.join(Separate_audio_dir, Separate_dir_name), file_pattern % i)
                logger.info(' Writing %s' % (path,))
                VADSetting.write_wave(path, segment, sample_rate)

def Select_Audio(Separate_audio_dir, high_pitch_dir, pitch_threshold):
    """
    ピッチにによって音声を分けるプログラム
    """
    Setting.make_dir(high_pitch_dir) # 高音音声選択用ディレクトリの作成

    Separate_audio_list = os.listdir(Separate_audio_dir)
    Separate_audio_list = sorted(Separate_audio_list)
    for Separate_dir in Separate_audio_list:
        logger.info(f"Files to be processed : {Separate_dir}")
        high_pitch_dir_name = "high-" + Separate_dir
        # 新しいフォルダのパスを作成
        high_pitch_path = os.path.join(high_pitch_dir, high_pitch_dir_name)

        # フォルダが既に存在するか確認
        if os.path.exists(high_pitch_path):
            logger.info(f"Skip because it can already be classified by pitch.")
            continue

        # 自動でフォルダを作成
        os.makedirs(high_pitch_path, exist_ok=True)

        #-- ディレクトリに.wavファイル以外があった場合の対策 --#
        Separate_audio_path = os.path.join(Separate_audio_dir, Separate_dir)
        files = os.listdir(Separate_audio_path)
        audio_files = []
        for file in files:
            if file.endswith(".wav"):
                audio_files.append(file)
        audio_files = sorted(audio_files)

        #--閾値による音声分類--#
        for audio_file in audio_files:
            audio_path = os.path.join(Separate_audio_path, audio_file)
            logger.info(f"Audio file : {audio_path}")
            audio_pitch = 0 # 音声ピッチ
            flame_count = 0 # 有声区間のフレーム数
            # wavファイルのパスを取得
            if not os.path.isfile(audio_path):
                logger.info(audio_path)
                continue

            #ここでparselmouthのオブジェクトに音声データを変換する
            snd = parselmouth.Sound(str(audio_path))
            # -----ピッチに対する処理-----#
            pitch = snd.to_pitch() # 10ms毎にpitchを計算(10ms毎の平均を取ってるかと思われる)
            pitch_avg = pitch.selected_array['frequency'] #これで配列になる
            # 配列から10ms毎のピッチを取り出し平均する
            for i in pitch_avg:
                if i != 0:
                    audio_pitch += i
                    flame_count += 1
            if audio_pitch != 0:
                audio_pitch = audio_pitch/flame_count
            # logger.info(f"パス：{audio_path}, ピッチ：{int(audio_pitch)}")
            target_audio_path = os.path.join(high_pitch_path, audio_file)
            if audio_pitch > pitch_threshold:
                shutil.move(audio_path, target_audio_path)

def make_script(high_pitch_dir, result_dir, model, json_file):
    """
    whisperで音声の文字起こしを行うプログラム
    """
    Setting.make_dir(result_dir) # 結果用ディレクトリの作成
    text_dir = os.path.join(result_dir, "text")
    Setting.make_dir(text_dir) # 書き起こし用ディレクトリの作成
    wav_dir = os.path.join(result_dir, "wav")
    Setting.make_dir(wav_dir) # 音声用ディレクトリの生成

    archive_files = os.listdir(high_pitch_dir)
    archive_files = sorted(archive_files)
    mapping = Setting.load_mapping(json_file)
    for archive in archive_files:
        unique_number = mapping[archive.replace("high-", "").replace("_vocals", ".wav")]
        spk = f"MIKO_{unique_number:03d}"
        logger.info(f"==================================================")
        logger.info(f"Processe this file : {archive}, Directory name : {spk}")

        text_path = os.path.join(text_dir, spk)
        wav_path = os.path.join(wav_dir, spk)
        logger.info(f"Test Path : {text_dir}, Audio Path : {wav_dir}")

        # フォルダが既に存在するか確認
        if (os.path.exists(text_path) and os.path.exists(wav_path)):
            logger.info(f"Already transcribed.")
            continue

        # 自動でフォルダを作成
        os.makedirs(text_path, exist_ok=True)
        os.makedirs(wav_path, exist_ok=True)

        archive_path = os.path.join(high_pitch_dir, archive)
        audio_files = os.listdir(archive_path)
        audio_files = sorted(audio_files)
        for audio_file in audio_files:
            if audio_file.endswith(".wav"):
                audio_path = os.path.join(archive_path, audio_file)
                audio = whisper.load_audio(audio_path)
                audio = whisper.pad_or_trim(audio)

                # make log-Mel spectrogram and move to the same device as the model
                mel = whisper.log_mel_spectrogram(audio).to(model.device)

                # detect the spoken language
                _, probs = model.detect_language(mel)
                language = max(probs, key=probs.get)
                logger.info(f'Detected language: {language}')
                # language = "ja"

                # decode the audio
                options = whisper.DecodingOptions()
                if language == "ja":
                    result = whisper.decode(model, mel, options)
                    if(transcript.is_text_clean(result.text)):
                        # create the filename for the text file in the new folder
                        reduced_text = transcript.reduce_repetitions(result.text, patterns)
                        text_file = os.path.splitext(audio_file)[0] + ".txt"
                        text_write_path = os.path.join(text_path, text_file)

                        # write the recognized text to the text file
                        with open(text_write_path, "w") as f:
                            f.write(transcript.convert_punctuation(reduced_text))

                        logger.info(f"Wrote text to {text_write_path}")

                        target_audio_path = os.path.join(wav_path, audio_file)
                        shutil.move(audio_path, target_audio_path)
                    else:
                        logger.info(f"This {audio_file} did not provide a correct transcription.")
                else:
                    logger.info(f"{audio_file} was not judged as Japanese.")






