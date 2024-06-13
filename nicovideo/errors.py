"""
このモジュールは、nicovideo.py全般にて送出される例外を定義します。

"""

class APIRequestError(RuntimeError):
    """ニコニコのAPIサーバへのリクエストに失敗した。"""
class ContentNotFoundError(APIRequestError):
    """指定されたコンテンツが見つからなかった。"""

class FrozenInstanceError(AttributeError):
    """イミュータブルなオブジェクトの属性に代入しようとした。"""
