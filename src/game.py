# ============================================================================
# src/game.py - Lógica del Juego de Ping Pong
# ============================================================================

import pygame
import random
from src.ai import AI

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 128, 0)

# Configuración del juego
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 80
BALL_SIZE = 12

class Game:
    def __init__(self, difficulty):
        """
        Inicializa el juego con la dificultad seleccionada
        difficulty: 0=Fácil, 1=Normal, 2=Difícil, 3=Dios
        """
        self.difficulty = difficulty
        
        # Configuración según dificultad
        self.difficulty_settings = {
            0: {"ball_speed": 5, "ai_speed": 3, "ai_reaction": 0.7},
            1: {"ball_speed": 6, "ai_speed": 5, "ai_reaction": 0.85},
            2: {"ball_speed": 7, "ai_speed": 7, "ai_reaction": 0.95},
            3: {"ball_speed": 8, "ai_speed": 8, "ai_reaction": 1.0}
        }
        
        settings = self.difficulty_settings[difficulty]
        
        # Paletas
        self.player_paddle = pygame.Rect(30, HEIGHT//2 - PADDLE_HEIGHT//2, 
                                        PADDLE_WIDTH, PADDLE_HEIGHT)
        self.ai_paddle = pygame.Rect(WIDTH - 40, HEIGHT//2 - PADDLE_HEIGHT//2, 
                                     PADDLE_WIDTH, PADDLE_HEIGHT)
        
        # Pelota
        self.ball = pygame.Rect(WIDTH//2, HEIGHT//2, BALL_SIZE, BALL_SIZE)
        self.ball_speed_x = settings["ball_speed"] * random.choice([-1, 1])
        self.ball_speed_y = settings["ball_speed"] * random.choice([-1, 1])
        
        # Puntajes
        self.score_player = 0
        self.score_ai = 0
        
        # HP
        self.player_hp = 100
        self.ai_hp = 100
        
        # IA
        self.ai = AI(self.ai_paddle, settings["ai_speed"], settings["ai_reaction"])
        
        # Velocidad del jugador
        self.player_speed = 7
        
        # Fuente para puntaje
        self.font_score = pygame.font.SysFont("Courier New", 40, bold=True)
        self.font_small = pygame.font.SysFont("Courier New", 20)
    
    def reset_ball(self):
        """Reinicia la posición de la pelota"""
        self.ball.center = (WIDTH//2, HEIGHT//2)
        settings = self.difficulty_settings[self.difficulty]
        self.ball_speed_x = settings["ball_speed"] * random.choice([-1, 1])
        self.ball_speed_y = settings["ball_speed"] * random.choice([-1, 1])
    
    def update(self):
        """
        Actualiza la lógica del juego
        Retorna True si el juego terminó
        """
        # Movimiento del jugador
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.player_paddle.top > 0:
            self.player_paddle.y -= self.player_speed
        if keys[pygame.K_s] and self.player_paddle.bottom < HEIGHT:
            self.player_paddle.y += self.player_speed
        
        # Movimiento de la IA
        self.ai.move(self.ball)
        
        # Movimiento de la pelota
        self.ball.x += self.ball_speed_x
        self.ball.y += self.ball_speed_y
        
        # Rebote en paredes superior e inferior
        if self.ball.top <= 0 or self.ball.bottom >= HEIGHT:
            self.ball_speed_y *= -1
        
        # Colisión con paletas
        if self.ball.colliderect(self.player_paddle) or self.ball.colliderect(self.ai_paddle):
            self.ball_speed_x *= -1
            # Aumentar ligeramente la velocidad
            self.ball_speed_x *= 1.05
            self.ball_speed_y *= 1.05
        
        # Puntos
        if self.ball.left <= 0:
            self.score_ai += 1
            self.ai_hp = max(0, self.ai_hp - 10)
            self.player_hp = max(0, self.player_hp - 15)
            self.reset_ball()
        
        if self.ball.right >= WIDTH:
            self.score_player += 1
            self.ai_hp = max(0, self.ai_hp - 15)
            self.reset_ball()
        
        # Verificar fin del juego
        if (self.player_hp <= 0 or self.ai_hp <= 0 or 
            self.score_player >= 10 or self.score_ai >= 10):
            return True
        
        return False
    
    def draw(self, screen):
        """Dibuja el juego en la pantalla"""
        screen.fill(BLACK)
        
        # Línea central
        pygame.draw.aaline(screen, DARK_GREEN, (WIDTH//2, 0), (WIDTH//2, HEIGHT))
        
        # Paletas
        pygame.draw.rect(screen, GREEN, self.player_paddle)
        pygame.draw.rect(screen, CYAN, self.ai_paddle)
        
        # Pelota
        pygame.draw.ellipse(screen, YELLOW, self.ball)
        
        # Marcador
        score_text = self.font_score.render(
            f"{self.score_player}  :  {self.score_ai}", 
            True, WHITE
        )
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))
        
        # Barras de HP
        self.draw_hp_bars(screen)
        
        # Controles
        controls = self.font_small.render("[W/S] Mover  |  [ESC] Menú", True, DARK_GREEN)
        screen.blit(controls, (WIDTH//2 - controls.get_width()//2, HEIGHT - 30))
    
    def draw_hp_bars(self, screen):
        """Dibuja las barras de HP en el juego"""
        hp_width = 150
        hp_height = 15
        
        # HP Jugador (izquierda)
        pygame.draw.rect(screen, WHITE, (50, 70, hp_width + 4, hp_height + 4))
        pygame.draw.rect(screen, BLACK, (52, 72, hp_width, hp_height))
        hp_color = GREEN if self.player_hp > 50 else YELLOW if self.player_hp > 25 else RED
        pygame.draw.rect(screen, hp_color, (52, 72, int(hp_width * self.player_hp / 100), hp_height))
        
        player_text = self.font_small.render("PLAYER", True, WHITE)
        screen.blit(player_text, (52, 50))
        
        # HP IA (derecha)
        pygame.draw.rect(screen, WHITE, (WIDTH - 50 - hp_width - 4, 70, hp_width + 4, hp_height + 4))
        pygame.draw.rect(screen, BLACK, (WIDTH - 50 - hp_width - 2, 72, hp_width, hp_height))
        hp_color = GREEN if self.ai_hp > 50 else YELLOW if self.ai_hp > 25 else RED
        pygame.draw.rect(screen, hp_color, (WIDTH - 50 - hp_width - 2, 72, 
                                           int(hp_width * self.ai_hp / 100), hp_height))
        
        ai_text = self.font_small.render("OPPONENT", True, WHITE)
        screen.blit(ai_text, (WIDTH - 50 - hp_width - 2, 50))