# Blender-VWI
Плагины для форматов файлов игрового движка Virtual World Inventor. 
##### Текущие планы
* Доработка экспорта.
* Переход на Blender 2.9. 
* Поддержка импорта и экспорта игровых ресурсов.

## Поддерживаемые игры
| Название игры | Название игры (международное) | Год выхода |
|-----------|-----------------------|:----------:|
| Дальнобойщики: Путь к победе | Hard Truck: Road to Victory | 1998 |
| Дальнобойщики - 2 | Hard Truck 2 (King of the Road) | 2000 (2003)

## Поддерживаемые форматы файлов
| Расширение | Описание           | Импорт | Экспорт | 
|-----------|-----------------------|:----------:|:----------:|
| .b3d  | Модели, логика, различные объекты   | Да   | Да  | 
| .way  | Пути транспорта для ИИ   | Да   | Да  | 
| .tch/.tech  | Параметры транспорта и динамических объектов   |      | Да  | 
| .res/.rmp  | Архив игровых ресурсов   |      | в работе    | 
| .pro  | Архив игровых ресурсов  |      |  в работе   | 

## Файлы в проекте

#### Папка **src/2.79** 

Плагины для версии 2.79.

#### Папка **scenes** 

Готовые сцены для экспорта в игру: **ht2-way.blend** - пути транспорта, **ht2-vehicle-export.blend** - транспорт, **ht2-env-module.blend** - карта

## Авторы
Юрий Гладышенко и Андрей Прожога.

## Ссылки
[Сообщество VK](https://vk.com/rnr_mods)

***

# About

Hard Truck classic games (VWI engine) import/export plugins for Blender.

#### Roadmap
* Blender 2.9 support
* Add support for game resource files (.res/.rmp)

## Supported games and formats

1. Hard Truck: Road to Victory (1998)

| Расширение | Описание           | Import | 
|-----------|-----------------------|:----------:|
| .b3d  | Models, game logic, various objects    | Yes  | 

2. Hard Truck: King Of The Road (2003)

| Расширение | Описание           | Import | Export | 
|-----------|-----------------------|:----------:|:----------:|
| .b3d  | Models, game logic, various objects   | Yes   | Yes  | 
| .way  | AI paths   | Yes  | Yes  | 
| .tch/.tech  | Transport parameters |      | Yes | 