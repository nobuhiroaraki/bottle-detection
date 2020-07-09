import numpy as np
import sys
import argparse
import ntpath
import matplotlib.pyplot as plt
# import picamera
from datetime import datetime
from yolo import YOLO
from PIL import Image
from time import sleep

import warnings

warnings.filterwarnings('ignore')
photo_filename = '/tmp/data.jpg'

def shutter():
    photofile = open(photo_filename, 'wb')
    print(photofile)

    # pi camera 用のライブラリーを使用して、画像を取得
    with picamera.PiCamera() as camera:
        #camera.resolution = (640,480)
        camera.resolution = (300,400)
        camera.start_preview()
        sleep(1.000)
        camera.capture(photofile)

def scan():
    shutter()
    try:
        image = Image.open(photo_filename)
    except:
        print('読込みエラー、再度入力お願いします。')
    else:
        output_dir = 'output/'
        _, file_name = ntpath.split(photo_filename)

        time = datetime.now().strftime('%Y%m%d%H%M%S')

        pred, score, r_image = yolo.detect_image(image)
        r_image.save(output_dir + 'result_{}_{}.jpg'.format(file_name.replace('.jpg', ''), time))
        plt.imshow(r_image)

    return pred, score


if __name__ == '__main__':
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    """
    コマンドライン引数
    """
    parser.add_argument(
        '-c', '--camera', default=False, action="store_true",
        help='カメラ検出モード'
    )

    parser.add_argument(
        '-f', '--file', default=False, action="store_true",
        help='ファイル検出モード'
    )

    parser.add_argument(
        '-s', '--sales', default=False, action="store_true",
        help='売上帳簿出力'
    )

    FLAGS = parser.parse_args()

    # モデルを読み込む
    yolo = YOLO()

    # 商品名・価格を読み込む
    class_dic = {39: ['ボトル', 100]}
    # class_names = class_dic['39'][0]
    # prices = class_dic['39'][1]

    if FLAGS.camera:
        """
        カメラ検出
        """
        checkout_list = []
        while True:
            key = input('商品をスキャンします。「Enter」を押して下さい')
            pred, score = scan()

            # 未検出ループ
            if len(pred)==0:
                key = input('商品を検出しませんでした。再度読み込みますか？ \nはい[y]、いいえ[n]？')
                if key == 'y':
                    continue

            # 未登録商品検出ループ
            if not all([x==39 for x in pred]):
                key = input('未登録商品を検出しました。再度読み込みますか？ \nはい[y]、いいえ[n]？')
                if key == 'y':
                    continue
                else:
                    print('未登録商品はお会計されません。')
                    pred = [x for x in pred if x==39]
                    pass

            for i, item in enumerate(pred):
                print('商品番号{} {}の金額は{}'.format(i, class_dic[item][0], class_dic[item][1]))

            # 商品選択
            flag = True
            while flag:
                key = input('お会計を行いたい商品番号を入力してください。(例：0 3 5): ')
                productid = set(map(int, key.split()))
                flag = False
                for i in productid:
                    if i not in range(len(pred)):
                        print('商品番号の誤りを検知しました。0-{}の間の番号を入力してください'.format(len(pred)-1))
                        flag = True
                        break


            checkout_list.extend([pred[x] for x in productid])

            print('買い物カゴに次の商品が入っています。')
            for item in checkout_list:
                print('{} ¥{}'.format(class_dic[item][0], class_dic[item][1]))

            # 会計終了プロセス
            key = input('他の商品もお会計しますか？ \nはい[y]、いいえ[n]？')
            if key=='y':
                continue
            else:
                break

        print('合計金額は¥{}です。'.format(sum([class_dic[x][1] for x in checkout_list])))


    elif FLAGS.file:
        """
        データファイル検出
        """
        checkout_list = []
        while True:
            img = input('ファイルパスを入力してください: ')
            try:
                image = Image.open(img)
            except:
                print('読込みエラー、再度入力お願いします。')
                continue
            else:
                output_dir = 'output/'
                _, file_name = ntpath.split(img)

                pred, score, r_image = yolo.detect_image(image)
                r_image.save(output_dir + 'result_{}.jpg'.format(file_name.replace('.jpg', '')))
                plt.imshow(r_image)

            # 未検出ループ
            if len(pred)==0:
                key = input('商品を検出しませんでした。再度読み込みますか？ \nはい[y]、いいえ[n]？')
                if key == 'y':
                    continue

            # 未登録商品検出ループ
            if not all([x==39 for x in pred]):
                key = input('未登録商品を検出しました。再度読み込みますか？ \nはい[y]、いいえ[n]？')
                if key == 'y':
                    continue
                else:
                    print('未登録商品はお会計されません。')
                    pred = [x for x in pred if x==39]
                    pass

            for i, item in enumerate(pred):
                print('商品番号{} {}の金額は{}'.format(i, class_dic[item][0], class_dic[item][1]))

            # 商品選択
            flag = True
            while flag:
                key = input('お会計を行いたい商品番号を入力してください。(例：0 3 5): ')
                productid = set(map(int, key.split()))
                flag = False
                for i in productid:
                    if i not in range(len(pred)):
                        print('商品番号の誤りを検知しました。0-{}の間の番号を入力してください'.format(len(pred)-1))
                        flag = True
                        break


            checkout_list.extend([pred[x] for x in productid])

            print('買い物カゴに次の商品が入っています。')
            for item in checkout_list:
                print('{} ¥{}'.format(class_dic[item][0], class_dic[item][1]))

            # 会計終了プロセス
            key = input('他の商品もお会計しますか？ \nはい[y]、いいえ[n]？')
            if key=='y':
                continue
            else:
                break

        print('合計金額は¥{}です。'.format(sum([class_dic[x][1] for x in checkout_list])))

    yolo.close_session()
