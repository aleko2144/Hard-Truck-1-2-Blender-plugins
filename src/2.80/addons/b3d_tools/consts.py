
EMPTY_NAME = '~'

blockTypeList = [
    ('6566754', "b3d", "b3d"),
    ('00', "00", "2D фон"),
    ('01', "01", "Камера"),
    ('02', "02", "Неизв. блок"),
    ('03', "03", "Контейнер"),
    ('04', "04", "Контейнер с возможностью привязки к нему других блоков"),
    ('05', "05", "Контейнер с возможностью привязки к нему другого блока"),
    ('06', "06", "Блок вершин"),
    ('07', "07", "Блок вершин"),
    ('08', "08", "Блок полигонов"),
    ('09', "09", "Триггер"),
    ('10', "10", "LOD"),
    ('11', "11", "Неизв. блок"),
    ('12', "12", "Плоскость коллизии"),
    ('13', "13", "Триггер (загрузчик карты)"),
    ('14', "14", "Блок, связанный с автомобилями"),
    ('15', "15", "Неизв. блок"),
    ('16', "16", "Неизв. блок"),
    ('17', "17", "Неизв. блок"),
    ('18', "18", "Связка локатора и 3D-модели, например: FiatWheel0Space и Single0Wheel14"),
    ('19', "19", "Контейнер, в отличие от блока типа 05, не имеет возможности привязки"),
    ('20', "20", "Плоская коллизия"),
    ('21', "21", "Контейнер с обработкой событий"),
    ('22', "22", "Блок-локатор"),
    ('23', "23", "Объёмная коллизия"),
    ('24', "24", "Локатор"),
    ('25', "25", "Звуковой объект"),
    ('26', "26", "Блок-локатор"),
    ('27', "27", "Блок-локатор"),
    ('28', "28", "Блок-локатор"),
    ('29', "29", "Неизв. блок"),
    ('30', "30", "Триггер для загрузки участков карты"),
    ('31', "31", "Неизв. блок"),
    ('33', "33", "Источник света"),
    ('34', "34", "Неизв. блок"),
    ('35', "35", "Блок полигонов"),
    ('36', "36", "Блок вершин"),
    ('37', "37", "Блок вершин"),
    ('39', "39", "Блок-локатор"),
    ('40', "40", "Генератор объектов")
    # ('444', "Разделитель", "Разделитель"),
]

collisionTypeList = [
    ('0', "стандарт", ""),
    ('1', "асфальт", ""),
    ('2', "земля", ""),
    ('3', "вязкое болото", ""),
    ('4', "легкопроходимое болото", ""),
    ('5', "мокрый асфальт", ""),
    ('7', "лёд", ""),
    ('8', "вода (уничтожает автомобиль)", ""),
    ('10', "песок", ""),
    ('11', "пустыня", ""),
    ('13', "шипы", ""),
    ('16', "лёд (следы от шин не остаются)", "")
]

lTypeList = [
    ('0', 'Тип 0', ""),
    ('1', 'Тип 1', ""),
    ('2', 'Тип 2', ""),
    ('3', 'Тип 3', "")
]


sTypeList = [
    ('2', "Тип 2, координаты + UV + нормали", "Данный тип используется на обычных моделях"),
    ('3', "Тип 3, координаты + UV", "Данный тип используется на моделях света фар"),
    ('258', "Тип 258, координаты + UV + нормали + 2 float", "Данный тип используется для моделей асфальтированных дорог"),
    ('514', "Тип 514, координаты + UV + нормали + 4 float", "Данный тип используется на моделях поверхности воды"),
    ('515', "Тип 515, координаты + UV + нормали + 2 float", "Тоже самое, что и 258. Данный тип используется для моделей асфальтированных дорог")
]

mTypeList = [
    ('1', "Тип 1, с разрывной UV", "Каждый трис модели записывается вместе со собственной UV."),
    ('3', "Тип 3, без разрывной UV", "Этот тип можно использовать для моделей, которые используют текстуру отражений.")
]

generatorTypeList = [
    ('$SeaGenerator', "$SeaGenerator", ""),
    ('$$TreeGenerator1', "$$TreeGenerator1", ""),
    ('$$TreeGenerator', "$$TreeGenerator", ""),
    ('$$CollisionOfTerrain', "$$CollisionOfTerrain", ""),
    ('$$GeneratorOfTerrain', "$$GeneratorOfTerrain", ""),
    ('$$People', "$$People", ""),
    ('$$WeldingSparkles', "$$WeldingSparkles", ""),
    ('$$DynamicGlow', "$$DynamicGlow", ""),
    ('$$StaticGlow', "$$StaticGlow", "")
]

conditionBlockTypeList = [
    ('GeometryKey', "GeometryKey", ""),
    ('CollisionKey', "CollisionKey", ""),
    ('GlassKey', "GlassKey", ""),
    ('RD_LampKey', "RD_LampKey", ""),
    ('RD_Key', "RD_Key", ""),
    ('RedSvetKey', "RedSvetKey", ""),
    ('GreenSvetKey', "GreenSvetKey", ""),
    ('TrafficLightKey0', "TrafficLightKey0", ""),
    ('TrafficLightKey1', "TrafficLightKey1", ""),
    ('ILLUM_LEVEL_00', "ILLUM_LEVEL_00", ""),
    ('ILLUM_LEVEL_01', "ILLUM_LEVEL_01", ""),
    ('ILLUM_LEVEL_02', "ILLUM_LEVEL_02", ""),
    ('ILLUM_LEVEL_03', "ILLUM_LEVEL_03", ""),
    ('ILLUM_LEVEL_04', "ILLUM_LEVEL_04", ""),
    ('ILLUM_LEVEL_05', "ILLUM_LEVEL_05", ""),
    ('ILLUM_LEVEL_06', "ILLUM_LEVEL_06", ""),
    ('ILLUM_LEVEL_07', "ILLUM_LEVEL_07", ""),
    ('ILLUM_LEVEL_08', "ILLUM_LEVEL_08", ""),
    ('ILLUM_LEVEL_09', "ILLUM_LEVEL_09", ""),
    ('ILLUM_LEVEL_10', "ILLUM_LEVEL_10", ""),
    ('ILLUM_LEVEL_11', "ILLUM_LEVEL_11", ""),
    ('ILLUM_LEVEL_12', "ILLUM_LEVEL_12", ""),
    ('ILLUM_LEVEL_13', "ILLUM_LEVEL_13", ""),
    ('ILLUM_LEVEL_14', "ILLUM_LEVEL_14", ""),
    ('ILLUM_LEVEL_15', "ILLUM_LEVEL_15", ""),
    ('Damage1Key', "Damage1Key", ""),
    ('DamageFRKey', "DamageFRKey", ""),
    ('DamageFCKey', "DamageFCKey", ""),
    ('DamageFLKey', "DamageFLKey", ""),
    ('DamageRKey', "DamageRKey", ""),
    ('DamageLKey', "DamageLKey", ""),
    ('DamageBRKey', "DamageBRKey", ""),
    ('DamageBCKey', "DamageBCKey", ""),
    ('DamageBLKey', "DamageBLKey", ""),
    ('DamageWheel0Key', "DamageWheel0Key", ""),
    ('DamageWheel1Key', "DamageWheel1Key", ""),
    ('DamageWheel2Key', "DamageWheel2Key", ""),
    ('DamageWheel3Key', "DamageWheel3Key", ""),
    ('DamageWheel4Key', "DamageWheel4Key", ""),
    ('DamageWheel5Key', "DamageWheel5Key", ""),
    ('DamageWheel6Key', "DamageWheel6Key", ""),
    ('DamageWheel7Key', "DamageWheel7Key", ""),
    ('HeadLightKey', "HeadLightKey", ""),
    ('BackFaraKeyR', "BackFaraKeyR", ""),
    ('StopFaraKeyR', "StopFaraKeyR", ""),
    ('BackFaraKeyL', "BackFaraKeyL", ""),
    ('StopFaraKeyL', "StopFaraKeyL", ""),
    ('IconKey', "IconKey", ""),
    ('SizeLightKey', "SizeLightKey", ""),
    ('HornKey', "HornKey", ""),
    ('SupportKey', "SupportKey", ""),
    ('CopSirenKey', "CopSirenKey", ""),
    ('CopLightKey', "CopLightKey", ""),
    ('GunRightKey', "GunRightKey", ""),
    ('GunLeftKey', "GunLeftKey", ""),
    ('StaticLightKey', "StaticLightKey", ""),
    ('BlinkLightKey', "BlinkLightKey", ""),
    ('SearchLightKey', "SearchLightKey", "")
]



