#!/usr/bin/env python3
"""引数に指定したユーザが投稿した全ての動画を表示します。（ニコニコのAPIサーバへの過度な負荷を避けるため、5秒ほどの遅延があります。）"""
import argparse
import time

import nicovideo.user

def main() -> None:
    """Main function"""
    parser = argparse.ArgumentParser(prog="get_user_uploaded.py", description=__doc__)
    parser.add_argument("userid", help="対象ユーザのID (数字)")
    args = parser.parse_args()

    for video in nicovideo.user.get_metadata(user_id=int(args.userid)).videolist:
        print(str(object=video))
        time.sleep(5)

if __name__ == "__main__":
    main()
