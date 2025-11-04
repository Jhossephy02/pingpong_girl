# ============================================================================
# src/characters.py - Sistema de Personajes y Expresiones Dinámicas
# ============================================================================

import pygame
import random
import os

# Frases según el estado de la flaca
neutral_lines = [
    "Tranqui nomás 😌",
    "A ver ps, demuéstrame 😏",
    "Yo confío bb 👀",
    "Vamos a ver 🤔",
    "Okay okay 😊",
]

smug_lines = [
    "No pues bebé, yo mando 😈",
    "Uy ya te cansaste 😮‍💨",
    "Ven ps te enseño 😘",
    "Así me gusta 💅",
    "Muy fácil esto 🤭",
    "¿Eso es todo? 😏",
]

angry_lines = [
    "Oe ya no seas abusivo 😡",
    "Ya me estás humillando 😤",
    "Aaaaa calla 😳",
    "No juegues así 😠",
    "Tramposo 🥺",
    "Para para 😭",
]

def load_girl_sprites():
    """
    Carga los sprites de la flaca desde assets/sprites/
    Retorna una tupla: (neutral, smug, angry)
    """
    sprite_path = "assets/sprites/"
    sprites = []
    
    # Intentar cargar cada sprite
    sprite_files = ["girl_neutral.png", "girl_smug.png", "girl_angry.png"]
    
    for sprite_file in sprite_files:
        full_path = os.path.join(sprite_path, sprite_file)
        try:
            if os.path.exists(full_path):
                sprite = pygame.image.load(full_path)
                sprite = pygame.transform.scale(sprite, (160, 160))
                sprites.append(sprite)
            else:
                # Si no existe, crear placeholder
                sprites.append(create_placeholder_sprite())
        except Exception as e:
            print(f"⚠️ Error cargando {sprite_file}: {e}")
            sprites.append(create_placeholder_sprite())
    
    return tuple(sprites)

def create_placeholder_sprite():
    """Crea un sprite placeholder simple"""
    surface = pygame.Surface((160, 160))
    surface.fill((30, 30, 30))
    
    # Dibujar rostro simple
    pygame.draw.circle(surface, (255, 200, 150), (80, 80), 50)
    pygame.draw.circle(surface, (50, 50, 50), (65, 75), 6)
    pygame.draw.circle(surface, (50, 50, 50), (95, 75), 6)
    pygame.draw.arc(surface, (50, 50, 50), (60, 85, 40, 20), 0, 3.14, 2)
    
    return surface

def get_girl_expression(score_player, score_ai, sprites):
    """
    Retorna el sprite y frase correctos según el marcador
    
    Args:
        score_player: Puntos del jugador
        score_ai: Puntos de la IA
        sprites: Tupla (neutral, smug, angry)
    
    Returns:
        Tupla (sprite, frase)
    """
    neutral, smug, angry = sprites
    
    # Calcular diferencia de puntos
    diff = score_ai - score_player
    
    if diff >= 2:
        # IA está ganando por mucho → Dominante
        return smug, random.choice(smug_lines)
    elif diff <= -2:
        # Jugador está ganando por mucho → Enojada
        return angry, random.choice(angry_lines)
    else:
        # Partido parejo → Neutral
        return neutral, random.choice(neutral_lines)

def get_expression_by_confianza(confianza, sprites):
    """
    Retorna el sprite y frase según el nivel de confianza
    
    Args:
        confianza: Valor del confianzómetro (0-100)
        sprites: Tupla (neutral, smug, angry)
    
    Returns:
        Tupla (sprite, frase)
    """
    neutral, smug, angry = sprites
    
    if confianza >= 75:
        # Dominante
        return smug, random.choice(smug_lines)
    elif confianza <= 29:
        # Enojada
        return angry, random.choice(angry_lines)
    else:
        # Neutral
        return neutral, random.choice(neutral_lines)

class Character:
    """Clase para manejar personajes con diferentes dificultades"""
    
    def __init__(self, difficulty):
        """
        Inicializa un personaje según la dificultad
        difficulty: 0=Fácil, 1=Normal, 2=Difícil, 3=Dios
        """
        self.difficulty = difficulty
        self.hp = 100
        
        # Diálogos según dificultad (para la pantalla de diálogo inicial)
        self.dialogue_sets = {
            0: [  # Fácil
                "¡Hola! Soy principiante... ¡Vamos a divertirnos!",
                "Wow, eres rápido... Intentaré seguirte el ritmo.",
                "¡Esto es más difícil de lo que pensaba!"
            ],
            1: [  # Normal
                "Hmm... Veamos de qué estás hecho.",
                "No está mal... Pero puedo hacerlo mejor.",
                "¡La victoria será mía!"
            ],
            2: [  # Difícil
                "¿Crees que puedes vencerme? ¡Qué ingenuo!",
                "Mis reflejos son superiores a los tuyos.",
                "¡Prepárate para la derrota!"
            ],
            3: [  # Dios
                "...",
                "Patético.",
                "Fin del juego."
            ]
        }
        
        self.dialogues = self.dialogue_sets[difficulty]
        
        # Intentar cargar imagen del personaje
        self.image = self.load_character_image()
        
        # Nombres según dificultad
        self.names = ["Novata", "Competidora", "Maestra", "Leyenda"]
        self.name = self.names[difficulty]
    
    def load_character_image(self):
        """Intenta cargar la imagen del personaje para la pantalla de diálogo"""
        # Para la pantalla de diálogo, usar el sprite neutral
        try:
            sprites = load_girl_sprites()
            return sprites[0]  # Neutral
        except:
            return create_placeholder_sprite()
    
    def get_dialogue(self, index):
        """Obtiene un diálogo específico"""
        if 0 <= index < len(self.dialogues):
            return self.dialogues[index]
        return ""
    
    def get_all_dialogues(self):
        """Retorna todos los diálogos del personaje"""
        return self.dialogues