import os
import sys
import pygame as pg
import random
import math


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),  # 上
    pg.K_DOWN: (0, +5), # 下
    pg.K_LEFT: (-5, 0),  # 左
    pg.K_RIGHT: (+5, 0),  # 右
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))
def get_kk_imgs() ->dict[tuple[int, int], pg.Surface]:
    kkk_img = pg.image.load("fig/3.png")
    kkk_r_img = pg.transform.flip(kkk_img, True, False)
    kk_dict = {
        (0, 0):pg.transform.rotozoom(kkk_img, 0, 0.9),
        (0, 5): pg.transform.rotozoom(kkk_r_img, -90, 0.9),
        (0, -5): pg.transform.rotozoom(kkk_r_img, 90, 0.9),  # こうかとんの画像
        (5, 0): pg.transform.flip(kkk_img, True, False),  # こうかとんの画像
        (-5, 0): pg.transform.rotozoom(kkk_img, 0, 0.9),  # こうかとんの画像
        (5, 5): pg.transform.rotozoom(kkk_r_img, -45, 0.9),  # こうかとんの画像
        (5, -5): pg.transform.rotozoom(kkk_r_img, 45, 0.9),  # こうかとんの画像
        (-5, 5): pg.transform.rotozoom(kkk_img, 45, 0.9),  # こうかとんの画像
        (-5, -5): pg.transform.rotozoom(kkk_img, 45, 0.9),  # こうかとんの画像
    
    }
    return kk_dict


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数:こうかとんrctまたは爆弾rct
    戻り値:横方向、縦方向のはみ出し判定(True:はみ出していない / False:はみ出している)
    """
    yoko, tate = True, True
    if rct.left < 0 or rct.right > WIDTH:  # 横方向判定
        yoko = False
    if rct.top < 0 or rct.bottom > HEIGHT:  # 縦方向判定
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を表示する関数
    引数:画面surface
    戻り値:なし
    """
    gameover_surf = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(gameover_surf, (0, 0, 0), (0, 0, WIDTH, HEIGHT))  # 黒い背景を描く
    gameover_surf.set_alpha(200)  # 透明度を設定

    font_surf = pg.Surface((WIDTH, HEIGHT))
    font = pg.font.Font(None, 100)  # フォントとサイズを指定
    text_surf = font.render("GAME OVER", True, (255, 255, 255))  # 白い文字で描画
    text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # 文字を画面中央に配置
    gameover_surf.blit(text_surf, text_rect)  # ゲームオーバーの文字を描画

    gmkk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    gmkk_rect1 = gmkk_img.get_rect(center=(WIDTH // 2 - 250, HEIGHT // 2))  # こうかとんの画像を文字の左に配置
    gmkk_rect2 = gmkk_img.get_rect(center=(WIDTH // 2 + 250, HEIGHT // 2))  # こうかとんの画像を文字の右に配置
    gameover_surf.blit(gmkk_img, gmkk_rect1)  # こうかとんの画像を描画
    gameover_surf.blit(gmkk_img, gmkk_rect2)  # こうかとんの画像を描画

    screen.blit(gameover_surf, (0, 0))  # ゲームオーバー画面を表示
    pg.display.update()  # 画面を更新
    pg.time.wait(5000) # 5秒間ゲームオーバー画面を表示


def init_bombs() -> tuple[list[pg.Rect], list[int]]:
    bb_imgs = []  # 爆弾の画像を格納するリスト
    for i in range(1,11):
        bb_img = pg.Surface((20*i, 20*i))  # 爆弾用Surface
        pg.draw.circle(bb_img, (255, 0, 0), (10*i, 10*i), 10*i)  # 半径10*iの赤い円を描く
        bb_img.set_colorkey((0, 0, 0))  # 黒を透明にする
        bb_imgs.append(bb_img)  # 爆弾の画像をリストに追加
        bb_accs =[a for a in range(1,11)] # 爆弾の加速度を格納するリスト
    return bb_imgs, bb_accs


def calc_bomb_velocity(org_pos, dst_pos, current_velocity):
    """
    爆弾の新しい速度ベクトルを計算する
    :param org_pos: 爆弾の座標 (x, y)
    :param dst_pos: こうかとんの座標 (x, y)
    :param current_velocity: 現在の速度ベクトル (vx, vy)
    :return: 更新後の速度ベクトル (vx, vy)
    """
    diff_x = dst_pos[0] - org_pos[0]  # 差ベクトルの計算
    diff_y = dst_pos[1] - org_pos[1]
    
    distance = math.sqrt(diff_x**2 + diff_y**2)  # 距離の計算
    
    if distance < 300:  # 慣性
        return current_velocity
    
    target_speed = math.sqrt(50)
    
    vx = (diff_x / distance) * target_speed
    vy = (diff_y / distance) * target_speed
    
    return vx, vy
        


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_img = pg.Surface((20, 20))  # 爆弾用Surface
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)  # 半径10の赤い円を描く
    bb_img.set_colorkey((0, 0, 0))  # 黒を透明にする
    bb_rect = bb_img.get_rect()
    bb_rect.centerx = random.randint(0, WIDTH)  # 爆弾の初期位置をランダムに設定
    bb_rect.centery = random.randint(0, HEIGHT)  # 爆弾の初期位置をランダムに設定
    vx, vy = +1, +1  # 爆弾の速度

    bb_imgs, bb_accs = init_bombs()
    kk_imgs = get_kk_imgs()
    

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        
        if kk_rct.colliderect(bb_rect):  # こうかとんと爆弾が衝突した場合
            gameover(screen)  # ゲームオーバー画面を表示
            return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:    
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])  # 移動を元に戻す
        kk_img = kk_imgs.get((sum_mv[0], sum_mv[1]), kk_imgs[(0, 0)])  # 移動方向に応じたこうかとんの画像を取得
        screen.blit(kk_img, kk_rct)

        vx, vy = calc_bomb_velocity(bb_rect.center, kk_rct.center, (vx, vy))  # 爆弾の新しい速度を計算
        avx = vx*bb_accs[min(tmr//500, 9)]  # 爆弾の加速度を適用
        avy = vy*bb_accs[min(tmr//500, 9)]  # 爆弾の加速度を適用 
        bb_img = bb_imgs[min(tmr//500, 9)]  # 爆弾の画像を更新
        bb_rect.width = bb_img.get_rect().width  # 爆弾の幅を更新
        bb_rect.height = bb_img.get_rect().height  # 爆弾の高さを更新   
        screen.blit(bb_img, bb_rect)  # 爆弾を画面に描画
        
        bb_rect.move_ip(avx, avy)  # 爆弾を移動
        yoko, tate = check_bound(bb_rect)
        if not yoko:  # 横方向に壁に当たった場合
            vx *= -1  # 横方向の速度を反転
        if not tate:  # 縦方向に壁に当たった場合
            vy *= -1  # 縦方向の速度を反転
        
        
        
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
