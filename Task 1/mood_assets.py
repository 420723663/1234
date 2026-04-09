from __future__ import division


BLACK = (0, 0, 0)
YELLOW = (255, 210, 0)
WHITE = (255, 255, 255)
BLUE = (70, 170, 255)
RED = (255, 70, 70)
PINK = (255, 120, 170)
ORANGE = (255, 140, 0)
GREEN = (60, 220, 120)
CYAN = (0, 210, 210)
AMBER = (255, 180, 0)

DIM_BLACK = (0, 0, 0)
DIM_YELLOW = (40, 30, 0)
DIM_WHITE = (50, 50, 50)

FACE_PALETTE = {
    "K": BLACK,
    "Y": YELLOW,
    "W": WHITE,
    "B": BLUE,
    "R": RED,
    "P": PINK,
    "O": ORANGE,
    "G": GREEN,
    "C": CYAN,
    "A": AMBER,
}

SLEEP_PALETTE = {
    "K": DIM_BLACK,
    "Y": DIM_YELLOW,
    "W": DIM_WHITE,
}


def build_frame(lines, palette):
    if len(lines) != 8:
        raise ValueError("Each frame must have 8 rows.")

    pixels = []
    for line in lines:
        if len(line) != 8:
            raise ValueError("Each frame row must have 8 columns.")
        for char in line:
            pixels.append(palette[char])
    return pixels


MOOD_EMOJIS = [
    {
        "name": "SunnySmile",
        "frames": [
            build_frame(
                [
                    "AYYYYYYA",
                    "YGWYYWGY",
                    "YKKYYKKY",
                    "YKKYYKKY",
                    "YYYYYYYY",
                    "YPPYYPPY",
                    "YKKYYKKY",
                    "YYYKKYYY",
                ],
                FACE_PALETTE,
            ),
            build_frame(
                [
                    "GYYYYYYG",
                    "YAWYYWAY",
                    "YKKYYKKY",
                    "YKKYYKKY",
                    "YYYYYYYY",
                    "YPPYYPPY",
                    "YKKYYKKY",
                    "YYYKKYYY",
                ],
                FACE_PALETTE,
            ),
            build_frame(
                [
                    "AYGYYGYA",
                    "YYWYYWYY",
                    "YKKYYKKY",
                    "YKKYYKKY",
                    "YYYYYYYY",
                    "YPPYYPPY",
                    "YKKYYKKY",
                    "YYYKKYYY",
                ],
                FACE_PALETTE,
            ),
        ],
    },
    {
        "name": "RainySad",
        "frames": [
            build_frame(
                [
                    "BYYYYYYB",
                    "YYWYYWYY",
                    "YKKYYKKY",
                    "YKKYYKKY",
                    "YYYYYYYY",
                    "YYYKKYYY",
                    "YKKYYKKY",
                    "BYYYYYYB",
                ],
                FACE_PALETTE,
            ),
            build_frame(
                [
                    "YYBYYBYY",
                    "YBWYYWBY",
                    "YKKYYKKY",
                    "YKKYYKKY",
                    "YYYYYYYY",
                    "YYYKKYYY",
                    "YKKYYKKY",
                    "YYBYYBYY",
                ],
                FACE_PALETTE,
            ),
            build_frame(
                [
                    "BYYBBYYB",
                    "YYWYYWYY",
                    "YKKYYKKY",
                    "YKKYYKKY",
                    "YYYYYYYY",
                    "YYYKKYYY",
                    "YKKYYKKY",
                    "YBYYYYBY",
                ],
                FACE_PALETTE,
            ),
        ],
    },
    {
        "name": "CalmFace",
        "frames": [
            build_frame(
                [
                    "CYYYYYYC",
                    "YYWYYWYY",
                    "YKKYYKKY",
                    "YKKYYKKY",
                    "YYYYYYYY",
                    "YYYYYYYY",
                    "YYKKKKYY",
                    "YYYYYYYY",
                ],
                FACE_PALETTE,
            ),
            build_frame(
                [
                    "YYCYYCYY",
                    "YCWYYWCY",
                    "YKKYYKKY",
                    "YKKYYKKY",
                    "YYYYYYYY",
                    "YYYYYYYY",
                    "YYKKKKYY",
                    "YYYYYYYY",
                ],
                FACE_PALETTE,
            ),
            build_frame(
                [
                    "CYYCCYYC",
                    "YYWYYWYY",
                    "YKKYYKKY",
                    "YKKYYKKY",
                    "YYYYYYYY",
                    "YYYYYYYY",
                    "YYKKKKYY",
                    "YYYYYYYY",
                ],
                FACE_PALETTE,
            ),
        ],
    },
    {
        "name": "SpicyMood",
        "frames": [
            build_frame(
                [
                    "RYYYYYYR",
                    "YKYYYYKY",
                    "YYKYYKYY",
                    "YKYYYYKY",
                    "YYYYYYYY",
                    "YYYKKYYY",
                    "YKKYYKKY",
                    "OYYYYYYO",
                ],
                FACE_PALETTE,
            ),
            build_frame(
                [
                    "RYYOOYYR",
                    "YKYYYYKY",
                    "YYKYYKYY",
                    "YKYYYYKY",
                    "YYYYYYYY",
                    "YYYKKYYY",
                    "YKKYYKKY",
                    "ORYYYYRO",
                ],
                FACE_PALETTE,
            ),
            build_frame(
                [
                    "ORYYYYRO",
                    "YKYYYYKY",
                    "YYKYYKYY",
                    "YKYYYYKY",
                    "YYYYYYYY",
                    "YYYKKYYY",
                    "YKKYYKKY",
                    "RYYOOYYR",
                ],
                FACE_PALETTE,
            ),
        ],
    },
    {
        "name": "BigWow",
        "frames": [
            build_frame(
                [
                    "AYYYYYYA",
                    "YKKYYKKY",
                    "YKKYYKKY",
                    "YYYYYYYY",
                    "YYKKKKYY",
                    "YYKYYKYY",
                    "YYKKKKYY",
                    "AYYYYYYA",
                ],
                FACE_PALETTE,
            ),
            build_frame(
                [
                    "YYAYYAYY",
                    "YKKYYKKY",
                    "YKKYYKKY",
                    "YYYYYYYY",
                    "YYKKKKYY",
                    "YYKYYKYY",
                    "YYKKKKYY",
                    "YYAYYAYY",
                ],
                FACE_PALETTE,
            ),
            build_frame(
                [
                    "AAYYYYAA",
                    "YKKYYKKY",
                    "YKKYYKKY",
                    "YYYYYYYY",
                    "YYKKKKYY",
                    "YYKYYKYY",
                    "YYKKKKYY",
                    "AAYYYYAA",
                ],
                FACE_PALETTE,
            ),
        ],
    },
]

SLEEP_FACE = build_frame(
    [
        "YYYYYYYY",
        "YYYYYYYY",
        "YYKKKKYY",
        "YYYYYYYY",
        "YYYYYYYY",
        "YYYKKYYY",
        "YYYYYYYY",
        "YYYYYYYY",
    ],
    SLEEP_PALETTE,
)

SPECIAL_FLIP_ANIMATION = [
    build_frame(
        [
            "CCYYYYCC",
            "KKKYYKKK",
            "KYKYYKYK",
            "KKKYYKKK",
            "YYYYYYYY",
            "YYYYYYYY",
            "YYKKKKYY",
            "CCYYYYCC",
        ],
        FACE_PALETTE,
    ),
    build_frame(
        [
            "CYYYYYYC",
            "KKKYYKKK",
            "KYKYYKYK",
            "KKKYYKKK",
            "YYYYYYYY",
            "YYYYYYYY",
            "YYKKKKYY",
            "CYYYYYYC",
        ],
        FACE_PALETTE,
    ),
    build_frame(
        [
            "CCYYYYCC",
            "KKKYYKKK",
            "KYKYYKYK",
            "KKKYYKKK",
            "YYYYYYYY",
            "YYYYYYYY",
            "YYKKKKYY",
            "CCYYYYCC",
        ],
        FACE_PALETTE,
    ),
    build_frame(
        [
            "YYCCCCYY",
            "KKKYYKKK",
            "KYKYYKYK",
            "KKKYYKKK",
            "YYYYYYYY",
            "YYYYYYYY",
            "YYKKKKYY",
            "YYCCCCYY",
        ],
        FACE_PALETTE,
    ),
    build_frame(
        [
            "CYYYYYYC",
            "KKKYYKKK",
            "KYKYYKYK",
            "KKKYYKKK",
            "YYYYYYYY",
            "YYYYYYYY",
            "YYKKKKYY",
            "CYYYYYYC",
        ],
        FACE_PALETTE,
    ),
    build_frame(
        [
            "CCYYYYCC",
            "KKKYYKKK",
            "KYKYYKYK",
            "KKKYYKKK",
            "YYYYYYYY",
            "YYYYYYYY",
            "YYKKKKYY",
            "CCYYYYCC",
        ],
        FACE_PALETTE,
    ),
]

ORIENTATION_ANIMATIONS = {
    "tilt_right": MOOD_EMOJIS[2]["frames"],
    "tilt_left": MOOD_EMOJIS[1]["frames"],
    "tilt_forward": MOOD_EMOJIS[3]["frames"],
    "tilt_back": MOOD_EMOJIS[4]["frames"],
    "flat": MOOD_EMOJIS[0]["frames"],
}
