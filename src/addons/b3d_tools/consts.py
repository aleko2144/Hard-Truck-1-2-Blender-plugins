
EMPTY_NAME = '~'

LEVEL_GROUP = 'level_group'

BLOCK_TYPE = 'block_type'

TRANSF_COLLECTION = 'Transformed objects'

TEMP_COLLECTION = 'Temporary objects'

BORDER_COLLECTION = 'Border objects'

blockTypeList = [
    ('111', "b3d root", "b3d"),
    ('444', "Group", "Grouping object"),
    ('00', "00(Unk?)", "2D background"),
    ('01', "01(Camera)", "Camera"),
    ('02', "02(Unk?)", "Unknown block"),
    ('03', "03(Container)", "Container"),
    ('04', "04(Container)", "Container containing other blocks"),
    ('05', "05(Container)", "Container containing other blocks"),
    ('06', "06(Vertexes)", "Vertex block (HT1)"),
    ('07', "07(Vertexes)", "Vertex block (HT2)"),
    # ('08', "08(Polygons)", "Polygon block"),
    ('09', "09(Trigger)", "Trigger"),
    ('10', "10(LOD)", "LOD"),
    ('11', "11(Trigger)", "Unknown block"),
    ('12', "12(Trigger)", "Unknown trigger"),
    ('13', "13(Trigger)", "Unknown trigger(map load)"),
    ('14', "14(Trigger)", "Unknown trigger(car related)"),
    ('15', "15(Trigger)", "Unknown block"),
    ('16', "16(Trigger)", "Unknown block"),
    ('17', "17(Trigger)", "Unknown block"),
    ('18', "18(Connector)", "Connector between space block(24) and root container block. Exmaple: FiatWheel0Space and Single0Wheel14"),
    ('19', "19(Room)", "Room container"),
    # ('20', "20(2D collision)", "Flat vertical collision"),
    ('21', "21(Event)", "Container with event handling"),
    ('22', "22(Trigger)", "Locator?"),
    # ('23', "23(3D collision)", "3D collision"),
    ('24', "24(Space)", "Space"),
    ('25', "25(Sound)", "Sound"),
    ('26', "26(Unk?)", "Locator?"),
    ('27', "27(Unk?)", "Locator?"),
    ('28', "28(2D Sprite)", "2D Sprite"),
    ('29', "29(Unk?)", "Unknown block"),
    ('30', "30(Portal)", "Portal"),
    ('31', "31(Unk?)", "Unknown block"),
    ('33', "33(Light)", "Light source"),
    ('34', "34(Unk?)", "Unknown block"),
    # ('35', "35(Polygons)", "Polygon block"),
    ('36', "36(Vertexes)", "Vertex block (HT1)"),
    ('37', "37(Vertexes)", "Vertex block (HT2)"),
    ('39', "39(Unk?)", "Locator?"),
    ('40', "40(Generator)", "Object generator"),
    # ('50', "50(Path)", "Path"),
    ('51', "51(Unoriented point)", "Unoriented point"),
    ('52', "52(Oriented point)", "Oriented point"),
]

collisionTypeList = [
    ('0', "standart", ""),
    ('1', "asphalt", ""),
    ('2', "grass", ""),
    ('3', "swamp (hard to pass)", ""),
    ('4', "swamp (easy to pass)", ""),
    ('5', "wet asphalt", ""),
    ('7', "ice", ""),
    ('8', "water (destroys truck)", ""),
    ('10', "sand", ""),
    ('11', "desert", ""),
    ('13', "spikes", ""),
    ('16', "ice (no tire marks)", "")
]



vTypeList = [
    ('0', '0(No normals)', "No normals"),
    ('1', '1(With normals)', "With normals"),
    ('2', '2(With normals)', "With normals"),
    ('3', '3(Normal switch)', "Normal switch")
]


sTypeList = [
    ('2', "Type 2, coords + UV + normals", "Is used on common models"),
    ('3', "Type 3, coords + UV", "Is used on headlight models"),
    ('258', "Type 258, coords + UV + normals + 2 float", "Is used on asphalt road models"),
    ('514', "Type 514, coords + UV + normals + 4 float", "Is used on water surface"),
    ('515', "Type 515, coords + UV + normals + 2 float", "Same as 258. Is used on asphalt road models")
]

fTypeList = [
    ('0', "Type 0", "With normals"),
    ('1', "Type 1", "No normals"),
    ('2', "Type 2", "With normals, breakable UV"),
    ('128', "Type 128", ""),
    ('144', "Type 144", "")
]


mTypeList = [
    ('1', "Type 1, Breakable UV", "Each polygon saves its own UV."),
    ('3', "Type 3, Unbroken UV", "Can be used for models, that use reflection texture.")
]

b24FlagList = [
    ('0', "0", "Attached object won't be shown"),
    ('1', "1", "Attached object will be shown")
]

b14Enum = [
    ('car', "For car", ""),
    ('trl', "For trailer", ""),
    ('trl_cyc', "For tank-trailer", ""),
    ('clk', "For collision", "")
]

triggerTypeList = [
    ('loader', "Loader", "Map part loader"),
    ('radar0', "Radar 0", "Event 0"),
    ('radar1', "Radar 1", "Event 1")
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



