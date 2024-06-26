import logging

####################
# 基本的なログ設定 #
####################

def setup_logging(name):

    logging.basicConfig(level=logging.DEBUG,
                    filename='data_prep.log',
                    filemode='w',
                    format='%(asctime)s (%(funcName)s:%(lineno)d) %(levelname)s: %(message)s')

    # ロガーを作成
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # ログレベルを設定

    # コンソールハンドラーを作成して設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # フォーマッターを作成してハンドラーに追加
    formatter = logging.Formatter('%(asctime)s (%(funcName)s:%(lineno)d) %(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)

    # ロガーにハンドラーを追加
    if not logger.handlers:  # ハンドラーが重複しないように確認
        logger.addHandler(console_handler)

    return logger

# 標準出力の設定
class CreateLogger(object):
    def __init__(self):
        self.output = []

    def write(self, message):
        self.output.append(message)

    def flush(self):
        pass
    def get_output(self):
        return ''.join(self.output)