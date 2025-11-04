# character state and expressions
import pygame
import random

def load_girl_sprites():
    neutral = pygame.transform.scale(pygame.image.load("assets/sprites/girl_neutral.png"), (160,160))
    smug = pygame.transform.scale(pygame.image.load("assets/sprites/girl_smug.png"), (160,160))
    angry = pygame.transform.scale(pygame.image.load("assets/sprites/girl_angry.png"), (160,160))
    return neutral, smug, angry

neutral_lines = [
    "Tranqui nomás 😌",
    "A ver ps, demuéstrame 😏",
    "Yo confío bb 👀",
]

smug_lines = [
    "No pues bebé, yo mando 😈",
    "Uy ya te cansaste 😮‍💨",
    "Ven ps te enseño 😘",
]

angry_lines = [
    "Oe ya no seas abusivo 😡",
    "Ya me estás humillando 😤",
    "Aaaaa calla 😳",
]

def get_girl_expression(score_player, score_ai, sprites):
    neutral, smug, angry = sprites
    if score_ai > score_player:
        return smug, random.choice(smug_lines)
    elif score_player > score_ai:
        return angry, random.choice(angry_lines)
    return neutral, random.choice(neutral_lines)
