import pygame as pg
from constants import *
import painting as pnt
import clouds as cl
import lives as liv
import bullets as bul
import bonuses as bon


pg.init()
win = pg.display.set_mode((win_w, win_h))  # Создание экрана для отрисовки
pg.display.set_caption("FLYDODGE")  # Название, которое будет в шапке окна
clock = pg.time.Clock()  # Штуковина для отсчета clock'ов

# Подгружаем всякие картинки для отрисовки
f = 'Agitpropc.otf'
font_huge = pg.font.Font(f, int(62 * scaling))
font_normal = pg.font.Font(f, int(38 * scaling))
font_ns = pg.font.Font(f, int(30 * scaling))
font_small = pg.font.Font(f, int(26 * scaling))

# Подгружаем картинки и изменяем их размер для отрисовки
logo = pg.image.load("img/logo_tr.png").convert_alpha()
logo = pg.transform.smoothscale(logo, (int(192 * scaling), int(192 * scaling)))

plane = pg.image.load("img/plane.png").convert_alpha()
plane = pg.transform.smoothscale(plane, (int(pl_w * scaling), int(pl_h * scaling)))

plane_dmg = pg.image.load("img/plane_dmg.png").convert_alpha()
plane_dmg = pg.transform.smoothscale(plane_dmg, (int(pl_w * scaling), int(pl_h * scaling)))

# противник
rkn = pg.image.load("img/circle.png").convert_alpha()
rkn = pg.transform.smoothscale(rkn, (int(bull_w * scaling), int(bull_w * scaling)))

# Бонус Щит
vpn = pg.image.load("img/Щит.png").convert_alpha()
vpn = pg.transform.smoothscale(vpn, (int(bonus_w * scaling), int(bonus_w * scaling)))

# Дополнительная жизнь
extr_l = pg.image.load("img/life.png").convert_alpha()
extr_l = pg.transform.smoothscale(extr_l, (int(bonus_w * scaling), int(bonus_w * scaling)))

# Подгружаем картинки облаков и изменяем их размер для отрисовки
cloud_0 = pg.image.load("img/cloud0.png").convert_alpha()
cloud_1 = pg.image.load("img/cloud1.png").convert_alpha()
cloud_2 = pg.image.load("img/cloud2.png").convert_alpha()
cloud_3 = pg.image.load("img/cloud3.png").convert_alpha()
cloud0 = pg.transform.smoothscale(cloud_0, (cld_w, cld_h))
cloud1 = pg.transform.smoothscale(cloud_1, (cld_w, cld_h))
cloud2 = pg.transform.smoothscale(cloud_2, (cld_w, cld_h))
cloud3 = pg.transform.smoothscale(cloud_3, (cld_w, cld_h))

clouds_img = [cloud0, cloud1, cloud2, cloud3]  # Массив всех возможных форм облачков
clouds = []  # Массив облачков, которые на экране уже бегут

pl_spdx0 = spd
pl_spdy0 = 0
pl_spdx = pl_spdx0  # Текущие скорости самолётика по осям
pl_spdy = pl_spdy0

pl_lives0 = 3
pl_lives = pl_lives0

pl_x = midle_x  # Текущие координаты самолётика
pl_y = midle_y

vulnerable = True  # Флаг, показывающий является ли цель уязвимой в данный момент

best_result = open('best_result.txt', 'r+')
game_time = 0  # Счётчик текущего времени игры
best_time = float(best_result.readline())  # Тут хранится лучшее время на данном устройстве

counter_cloud = cld_border_shift

# Всякие флаги
crashed = False  # Флаг для проверки закрывания программы
menu = True  # Флаг, показывающий, что игрок находится (не находится) в меню
game_over = False  # Флаг, показывающий, что игрок играет (не играет)
game = False  # Флаг, показывающий, что игрок видит (не видит) окно GAME OVER
pause = False

# Прогружаем звуки для игры
hit = pg.mixer.Sound('sound/telerun_hit.ogg')
bonus_life = pg.mixer.Sound('sound/telerun_bonus_life.ogg')
music = pg.mixer.music.load('sound/telerun_theme.ogg')
up = pg.mixer.Sound('sound/telerun_up.ogg')
click = pg.mixer.Sound('sound/telerun_click.ogg')
pg.mixer.music.play(-1)
pg.mixer.music.set_volume(0.03)


# Функция, свободного падения
def fall(dt, y, spdy, ay):
    y += spdy * dt + ay * dt ** 2 / 2
    spdy += ay * dt
    return y, spdy


while not crashed:
    win.fill((255, 255, 255))
    if cl.clouds_run(win, clouds, clouds_img, counter_cloud):
        counter_cloud = 0
    else:
        counter_cloud += 1

    if menu:
        pg.time.delay(delay)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                click_channel = click.play()
                click_channel.set_volume(0.5)
                crashed = True

        pnt.draw_menu(win, font_small, font_normal, font_ns, font_huge, logo, best_time)  # Рисуем меню
        pg.display.update()
        keys = pg.key.get_pressed()  # Все нажатые кнопки

        if keys[pg.K_RETURN]:  # Новая игра
            click_channel = click.play()
            click_channel.set_volume(0.05)
            pl_x, pl_y, = pl_x0, pl_y0
            pl_spdx, pl_spdy = pl_spdx0, pl_spdy0
            pl_lives = pl_lives0
            menu = False
            game = True
            game_time = 0
            bon.n_vpn = 1
            bon.n_ext = 1
            clock.tick()

    if game:
        if pl_lives > 0:
            clock.tick()
            bul.speed_counter += 1
            pg.time.delay(delay)

            for event in pg.event.get():  # Проверка на выход из игры
                if event.type == pg.QUIT:
                    crashed = True
                    click_channel = click.play()
                    click_channel.set_volume(0.1)

            keys = pg.key.get_pressed()  # Все нажатые кнопки

            if keys[pg.K_SPACE]:
                pause = True
                click_channel = click.play()
                click_channel.set_volume(0.1)

            if keys[pg.K_RIGHT] and (win_w - pl_x >= pl_w + brd):  # Движение вправо
                pl_x += pl_spdx * t

            if keys[pg.K_LEFT] and (pl_x >= brd):  # Движение влево
                pl_x -= pl_spdx * t

            if (not keys[pg.K_DOWN] and not keys[pg.K_UP]) or (
                    keys[pg.K_DOWN] and keys[pg.K_UP]):  # Падение
                pl_y, pl_spdy = fall(t, pl_y, pl_spdy, pl_g)

            else:
                if keys[pg.K_UP] and (pl_y > brd):  # Движение вверх
                    pl_y, pl_spdy = fall(t, pl_y, spd_up, pl_g)

                if pl_y < brd:  # Выход за границы по высоте
                    pl_spdy = 0

                if keys[pg.K_DOWN]:  # Движение вниз
                    pl_y, pl_spdy = fall(t, pl_y, pl_spdy, a_down)
            if pl_y <= brd:  # Ограничение сверху
                pl_y = brd

            if pl_y >= win_h - brd:
                up_channel = up.play()
                up_channel.set_volume(0.1)

            polygon = [[pl_x + 0.21 * pl_w, pl_y + 0.32 * pl_h], [pl_x + 0.19 * pl_w, pl_y],
                       [pl_x + pl_w, pl_y + 0.32 * pl_h], [pl_x + 0.21 * pl_w, pl_y + pl_h],
                       [pl_x + 0.21 * pl_w, pl_y + 0.75 * pl_h], [pl_x, pl_y + 0.85 * pl_h]]
            bul.bullet_generator(win, pl_x + pl_w / 2, pl_y + pl_h / 2, rkn)

            game_time += clock.get_time() / 1000  # Обновление игрового времени
            pnt.print_time(win, font_small, game_time)  # Вывод времени на экран

            pl_lives, vulnerable = liv.check_bonuses(pl_lives, vulnerable, polygon, bonus_life)
            pl_spdy, pl_lives, vulnerable = liv.check_lives(pl_y, pl_spdy, pl_lives, vulnerable,
                                                            polygon, hit)
            bon.bonus_generation(win, game_time, extr_l, vpn)
            pnt.lives_counter(win, font_normal, pl_lives)  # Прорисовка счетчика жизней

            pnt.draw_plane(win, pl_x, pl_y, plane, plane_dmg, vulnerable)
            pg.display.update()  # Перерисовка всего экрана

        else:
            game = False
            game_over = True
            if game_time > best_time:  # Сохранение лучшего времени
                best_time = game_time
                best_result.seek(0)
                best_result.truncate()
                best_result.write(str(round(best_time, 2)) + '\n')
    if pause:
        pg.time.delay(delay)
        game = False
        clock.tick()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                crashed = True
                click_channel = click.play()
                click_channel.set_volume(0.05)

        keys2 = pg.key.get_pressed()  # Все нажатые кнопки

        if keys2[pg.K_RETURN]:
            pause = False
            game = True
            click_channel = click.play()
            click_channel.set_volume(0.05)

        pnt.draw_pause(win, font_small, font_normal, font_huge, game_time)
        pg.display.update()

    if game_over:
        vulnerable = True
        bul.speed_counter = 0
        bul.bullet_array = []
        bon.list_of_lives = []
        bon.list_of_vpn = []
        pg.time.delay(delay)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                crashed = True
        pnt.draw_go(win, font_small, font_normal, font_huge, game_time,
                    best_time)  # Отрисовка game_over
        pg.display.update()

        keys = pg.key.get_pressed()

        if keys[pg.K_RETURN]:  # Новая игра
            click_channel = click.play()
            click_channel.set_volume(0.05)
            pl_x, pl_y, = pl_x0, pl_y0
            pl_spdx, pl_spdy = pl_spdx0, pl_spdy0
            pl_lives = pl_lives0
            game_over = False
            game = True
            game_time = 0
            bon.n_vpn = 1
            bon.n_ext = 1
            clock.tick()

        if keys[pg.K_BACKSPACE]:  # Выход в меню
            click_channel = click.play()
            click_channel.set_volume(0.05)
            game_over = False
            menu = True

best_result.close()
pg.quit()  # Завершение программы
quit()
