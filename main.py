import pygame
import pytmx

# Объявление констант с величинами , размер окна , fps и размеры платформ
SIZE = WIDTH, HEIGHT = 400, 400

FPS = 80

PLATFORM_WIDTH = 32
PLATFORM_HEIGHT = 32

# Объявление групп спрайтов
platforms = pygame.sprite.Group()
players = pygame.sprite.Group()
land = pygame.sprite.Group()
monsters = pygame.sprite.Group()
coins = pygame.sprite.Group()
chests = pygame.sprite.Group()
finish = pygame.sprite.Group()

font_name = 'font/Pixel_font.TTF'

# Константы с изображениями для анимированных спрайтов
MOVE_DOWN = ['entity/player/stand.png', 'entity/player/down1.png',
             'entity/player/down2.png', 'entity/player/down3.png']

MOVE_UP = ['entity/player/up1.png', 'entity/player/up2.png',
           'entity/player/up3.png', 'entity/player/up4.png']

MOVE_RIGHT = ['entity/player/right1.png', 'entity/player/right2.png',
              'entity/player/right3.png', 'entity/player/right4.png']

MOVE_LEFT = ['entity/player/left1.png', 'entity/player/left2.png',
             'entity/player/left3.png', 'entity/player/left4.png']

SKELETON_UP = ['entity/monsters/up1.png', 'entity/monsters/up2.png',
               'entity/monsters/up3.png', 'entity/monsters/up4.png']

SKELETON_DOWN = ['entity/monsters/stand.png', 'entity/monsters/down1.png',
                 'entity/monsters/down2.png', 'entity/monsters/down3.png']

SKELETON_RIGHT = ['entity/monsters/right1.png', 'entity/monsters/right2.png',
                  'entity/monsters/right3.png', 'entity/monsters/right4.png']

SKELETON_LEFT = ['entity/monsters/left1.png', 'entity/monsters/left2.png',
                 'entity/monsters/left3.png', 'entity/monsters/left4.png']

COIN_ANIMATION = ['objects/coin/coin1.png', 'objects/coin/coin2.png', 'objects/coin/coin3.png',
                  'objects/coin/coin4.png', 'objects/coin/coin5.png']

pygame.mixer.init()
coin_sound = pygame.mixer.Sound('sounds/coin.mp3')
coin_sound.set_volume(0.3)
coins_sound = pygame.mixer.Sound('sounds/coins.mp3')
coins_sound.set_volume(0.3)


# Класс земли под ногами пользователя , унаследуется от Sprite
class Landing(pygame.sprite.Sprite):
    def __init__(self, group, x, y, image):
        # Вызов конструктора базового класса и загрузка изображения
        super().__init__(group)
        self.image = image
        # Вычисление позиции объекта с помощью умножения кординат тайла по x,y на его размер
        self.rect = pygame.Rect(PLATFORM_WIDTH * x, PLATFORM_HEIGHT * y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        # Вычисление маски для дальнейшей проверки столкновений
        self.mask = pygame.mask.from_surface(self.image)


# Класс платформ , наследуется от Landing
class Platform(Landing):
    def __init__(self, group, x, y, image):
        # Все переменные унаследованы от Landing
        super().__init__(group, x, y, image)


# Класс камеры , которая перемещает все объекты на карте относительно позиции игрока
class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        # Обновление позиции объекта объекта
        obj.rect.x += -self.dx
        obj.rect.y += -self.dy

    def update(self, target):
        # Обновление смещения по x,y относительно текущей скорости передвижения игрока
        self.dx = target.vel_x
        self.dy = target.vel_y


class Player(pygame.sprite.Sprite):
    def __init__(self, group, x, y, image):
        super().__init__(group)

        # Загрузка изображения , вычисление маски, установка x,y координат
        self.image = image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x
        self.rect.y = y
        # Скорость персонажа по x,y
        self.vel_x = 0
        self.vel_y = 0
        # Переменные для проверки определенных условий во время игры
        self.coins_count = 0
        self.frame_c = 0
        self.direction = 0
        self.heart_count = 3
        self.is_finish = False

    def update(self, *args):
        # Обнуляем скорость каждый раз при вызове update
        self.vel_y = 0
        self.vel_x = 0
        # Если кол-во кадров > 4 то обнуляем
        if self.frame_c == 4:
            self.frame_c = 0
        # Проверка нажатия клавиш пользователем
        # Изменение скорости персонажа исходя из нажатой клавиши
        # Смена кадра анимации спрайта
        if args and args[0].type == pygame.KEYDOWN:
            if args[0].key == pygame.K_DOWN:
                self.vel_y += 4
                self.image = pygame.image.load(MOVE_DOWN[self.frame_c])
                self.direction = 0
            elif args[0].key == pygame.K_UP:
                self.vel_y -= 4
                self.image = pygame.image.load(MOVE_UP[self.frame_c])
                self.direction = 1
            elif args[0].key == pygame.K_LEFT:
                self.vel_x -= 4
                self.image = pygame.image.load(MOVE_LEFT[self.frame_c])
                self.direction = 2
            elif args[0].key == pygame.K_RIGHT:
                self.vel_x += 4
                self.image = pygame.image.load(MOVE_RIGHT[self.frame_c])
                self.direction = 3
        # Если персонаж стоит на месте то кол-во кадров = 0
        # Ставим изображение персонажа на месте
        else:
            self.frame_c = 0
            self.image = pygame.image.load(MOVE_DOWN[self.frame_c])
        # Вызов функций проверки столкновенний с группами спрайтов
        self.collide(self.vel_x, self.vel_y, platforms)
        self.collide(self.vel_x, self.vel_y, monsters)
        self.collide(self.vel_x, self.vel_y, chests)
        self.collide(self.vel_x, self.vel_y, finish)
        self.frame_c += 1

    # Скорость по x,y
    # Группа спрайтов которую надо проверить на столкновение
    def collide(self, vel_x, vel_y, sp_group):
        for elements in sp_group:
            # Если персонаж столкнулся с группой спрайтов , то
            # Сдвигаем его в противоположную сторону
            # Если персонаж стоит и сталкивается с группой спрайтов
            # Сдвигаем в сторону противоположную последней траектории передвижения
            if pygame.sprite.collide_rect(self, elements) and elements.rect.y > self.rect.y:
                if vel_x > 0:
                    self.vel_x -= 6
                elif vel_y < 0:
                    self.vel_y += 6
                elif vel_x < 0:
                    self.vel_x += 6
                elif vel_y > 0:
                    self.vel_y -= 6
                elif self.direction == 0:
                    self.vel_y -= 6
                elif self.direction == 1:
                    self.vel_y += 6
                elif self.direction == 2:
                    self.vel_x += 6
                elif self.direction == 3:
                    self.vel_x -= 6
                # Проверка на определенные группы спрайтов
                # Для взаимодействия с этими объектами
                if type(elements) == Monsters:
                    self.heart_count -= 1
                if type(elements) == Chest and elements.is_closed:
                    elements.is_closed = False
                    self.coins_count += elements.secret
                    coins_sound.play()
                if type(elements) == Finish:
                    self.is_finish = True

    # Функция конца игры
    # Вызывается в двух случаях:
    # 1.Персонаж умер 2.Пересек финиш
    def game_over(self, *args):
        # Вывод текста в зависимости от исхода
        if self.heart_count <= -1:
            font = pygame.font.Font(font_name, 40)
            pre_text = font.render('GAME OVER', True, 'WHITE')
            screen.blit(pre_text, (30, 170))
            font = pygame.font.Font(font_name, 20)
            pre_text = font.render('press up key to try again', True, 'WHITE')
            screen.blit(pre_text, (5, 220))
            pre_text = font.render('esc to exit', True, 'WHITE')
            screen.blit(pre_text, (130, 250))
        elif self.is_finish:
            font = pygame.font.Font(font_name, 40)
            pre_text = font.render(' YOU WIN', True, 'WHITE')
            screen.blit(pre_text, (30, 170))
            font = pygame.font.Font(font_name, 20)
            pre_text = font.render('esc to exit', True, 'WHITE')
            screen.blit(pre_text, (120, 250))
        # Если пользователь хочет переиграть
        # Удаляем все объекты и перезагружаем карту
        if args and args[0].type == pygame.KEYDOWN:
            if args[0].key == pygame.K_ESCAPE:
                return False
            elif args[0].key == pygame.K_UP and not self.is_finish:
                for enemy in monsters:
                    enemy.kill()
                for coin in coins:
                    coin.kill()
                for landing in land:
                    landing.kill()
                for platform in platforms:
                    platform.kill()
                for end in finish:
                    end.kill()
                load_lvl()
                self.heart_count = 3
                self.coins_count = 0
        return True


# Класс монет
class Coin(pygame.sprite.Sprite):
    def __init__(self, group, pos_x, pos_y, image):
        super().__init__(group)
        self.frame_c = 0

        self.image = image

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = pos_x
        self.rect.y = pos_y

    def update(self):
        self.frame_c += 1
        if self.frame_c == 5:
            self.frame_c = 0
        self.image = pygame.image.load(COIN_ANIMATION[self.frame_c])
        for elements in players:
            if pygame.sprite.collide_rect(self, elements) and elements.rect.y < self.rect.y:
                self.kill()
                coin_sound.play()
                elements.coins_count += 10


# Класс монстров , унаследован от класса персонажа
class Monsters(Player):
    def __init__(self, group, x, y, u_l, r_d, move_direct, image):
        super().__init__(group, x, y, image)
        self.u_l = u_l
        self.r_d = r_d
        self.count = 0
        self.direction = 0
        self.move_direct = move_direct

    def update(self):
        # Проверка по какой оси должен ходить монстр
        # Смена координат и анимации монстра

        if self.move_direct == 0:
            if self.frame_c == 4:
                self.frame_c = 0
            if self.count < abs(self.u_l - self.r_d) and self.direction == 0:
                self.count += 2
                self.rect.y += 2
                self.image = pygame.image.load(SKELETON_DOWN[self.frame_c])

            elif self.count > 0 and self.direction == 1:
                self.count -= 2
                self.rect.y -= 2
                self.image = pygame.image.load(SKELETON_UP[self.frame_c])

            if self.count == abs(self.u_l - self.r_d):
                self.direction = 1
            elif self.count == 0:
                self.direction = 0

            self.frame_c += 1
        else:
            if self.frame_c == 4:
                self.frame_c = 0
            if self.count < abs(self.u_l - self.r_d) and self.direction == 0:
                self.count += 2
                self.rect.x += 2
                self.image = pygame.image.load(SKELETON_RIGHT[self.frame_c])

            elif self.count > 0 and self.direction == 1:
                self.count -= 2
                self.rect.x -= 2
                self.image = pygame.image.load(SKELETON_LEFT[self.frame_c])

            if self.count == abs(self.u_l - self.r_d):
                self.direction = 1
            elif self.count == 0:
                self.direction = 0
            self.frame_c += 1


# Класс сундука
class Chest(pygame.sprite.Sprite):
    def __init__(self, group, pos_x, pos_y, image, secret):
        super().__init__(group)

        self.frame_c = 0

        self.image = image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos_x
        self.rect.y = pos_y

        self.secret = secret

        self.is_closed = True

    def update(self):
        # Если сундук открыли меняем картинку
        if not self.is_closed:
            self.image = pygame.image.load('chest/open_chest.png')


# Класс индикаторов для вывода информации о счете и тд

class Indicator:
    def __init__(self, x, y, icon, font_size, text):
        self.x = x
        self.y = y

        self.icon = pygame.image.load(icon)

        self.font_size = font_size

        self.text = text

    def draw(self):
        font = pygame.font.Font(font_name, 20)
        pre_text = font.render(self.text, True, 'WHITE')
        screen.blit(self.icon, (self.x, self.y))
        screen.blit(pre_text, (self.x + self.icon.get_width() + 15, self.y))


# Класс финишной линии
class Finish(pygame.sprite.Sprite):
    def __init__(self, group, x, y, image):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


def load_lvl():
    map_tmx = pytmx.load_pygame('map/Test_map.tmx')
    tile_height = map_tmx.height
    tile_width = map_tmx.width
    for y in range(tile_height):
        for x in range(tile_width):
            tiled = map_tmx.get_tile_image(x, y, 0)
            tiled1 = map_tmx.get_tile_image(x, y, 1)
            if tiled is not None:
                Platform(platforms, x, y, tiled)
            if tiled1 is not None:
                Landing(land, x, y, tiled1)

    m_layer = map_tmx.get_layer_by_name('Monsters')
    for m in m_layer:
        Monsters(monsters, m.x, m.y, m.u_l, m.r_d, m.move_direct, m.image)

    h_layer = map_tmx.get_object_by_name('Knight')
    Player(players, h_layer.pos_x, h_layer.pos_y, h_layer.image)

    c_layer = map_tmx.get_layer_by_name('Coins')
    for c in c_layer:
        Coin(coins, c.x, c.y, c.image)

    ch_layer = map_tmx.get_layer_by_name('Chest')
    for ch in ch_layer:
        Chest(chests, ch.x, ch.y, ch.image, ch.secret)

    f_layer = map_tmx.get_layer_by_name('Finish')
    for f in f_layer:
        Finish(finish, f.x, f.y, f.image)


# Игровой цикл
if __name__ == '__main__':
    pygame.init()
    timer = pygame.time.Clock()
    screen = pygame.display.set_mode(SIZE)
    running = True
    load_lvl()
    camera = Camera()
    coins_indicator = Indicator(10, 10, 'objects/coin/coin1.png', 20, '0X')
    heart_indicator = Indicator(125, 10, 'objects/heart.png', 20, '3X')
    for i in players:
        player = i
    while running:
        coins_indicator.text = str(player.coins_count) + 'X'
        heart_indicator.text = str(player.heart_count) + 'X'
        timer.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
        if player.heart_count > -1 and not player.is_finish:
            screen.fill((66, 57, 58))

            camera.update(player)
            for i in platforms:
                camera.apply(i)
            for i in land:
                camera.apply(i)
            for i in monsters:
                camera.apply(i)
            for i in coins:
                camera.apply(i)
            for i in chests:
                camera.apply(i)
            for i in finish:
                camera.apply(i)

            platforms.draw(screen)
            land.draw(screen)
            coins.draw(screen)
            coins.update()
            chests.draw(screen)
            chests.update()
            monsters.draw(screen)
            monsters.update()
            players.draw(screen)
            players.update(event)
            finish.draw(screen)
            coins_indicator.draw()
            heart_indicator.draw()
            pygame.time.delay(50)
        else:
            running = player.game_over(event)
