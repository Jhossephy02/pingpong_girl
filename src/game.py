# ============================================================================
# src/game.py - Lógica del Juego de Ping Pong con Confianzómetro
# ============================================================================

import pygame
import random
from src.ai import move_ai
from src.characters import load_girl_sprites, get_girl_expression

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 128, 0)
ORANGE = (255, 165, 0)

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
        
        # Velocidades actuales
        self.current_ball_speed_x = self.ball_speed_x
        self.current_ball_speed_y = self.ball_speed_y
        
        # Puntajes
        self.score_player = 0
        self.score_ai = 0
        
        # HP
        self.player_hp = 100
        self.ai_hp = 100
        
        # 🔥 CONFIANZÓMETRO (0-100)
        self.confianza = 50  # Empieza neutral
        
        # Velocidad del jugador y AI
        self.player_speed = 7
        self.ai_speed = settings["ai_speed"]
        
        # Cargar sprites de la flaca
        try:
            self.girl_sprites = load_girl_sprites()
            self.current_girl_sprite = self.girl_sprites[0]  # neutral por defecto
            self.current_girl_line = "¡Vamos a jugar! 😏"
        except:
            print("⚠️ No se pudieron cargar los sprites. Usando placeholders.")
            self.girl_sprites = None
            self.current_girl_sprite = None
            self.current_girl_line = "¡Vamos!"
        
        # Control de cambio de expresión
        self.expression_timer = 0
        self.expression_duration = 180  # 3 segundos (60 FPS)
        
        # Fuentes
        self.font_score = pygame.font.SysFont("Courier New", 40, bold=True)
        self.font_small = pygame.font.SysFont("Courier New", 20)
        self.font_dialogue = pygame.font.SysFont("Courier New", 16)
        self.font_tiny = pygame.font.SysFont("Courier New", 14)
    
    def reset_ball(self):
        """Reinicia la posición de la pelota"""
        self.ball.center = (WIDTH//2, HEIGHT//2)
        settings = self.difficulty_settings[self.difficulty]
        self.ball_speed_x = settings["ball_speed"] * random.choice([-1, 1])
        self.ball_speed_y = settings["ball_speed"] * random.choice([-1, 1])
        self.current_ball_speed_x = self.ball_speed_x
        self.current_ball_speed_y = self.ball_speed_y
    
    def update_confianza(self, change):
        """Actualiza el confianzómetro y cambia la expresión si es necesario"""
        self.confianza = max(0, min(100, self.confianza + change))
        
        # Actualizar sprite y frase según confianza
        if self.girl_sprites:
            self.current_girl_sprite, self.current_girl_line = get_girl_expression(
                self.score_player, self.score_ai, self.girl_sprites
            )
            # Reiniciar timer para mostrar la nueva expresión
            self.expression_timer = self.expression_duration
    
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
        move_ai(self.ai_paddle, self.ball, self.ai_speed)
        
        # Asegurar que la paleta no salga de la pantalla
        if self.ai_paddle.top < 0:
            self.ai_paddle.top = 0
        if self.ai_paddle.bottom > HEIGHT:
            self.ai_paddle.bottom = HEIGHT
        
        # Movimiento de la pelota
        self.ball.x += self.current_ball_speed_x
        self.ball.y += self.current_ball_speed_y
        
        # Rebote en paredes superior e inferior
        if self.ball.top <= 0 or self.ball.bottom >= HEIGHT:
            self.current_ball_speed_y *= -1
        
        # Colisión con paletas
        if self.ball.colliderect(self.player_paddle):
            self.current_ball_speed_x = abs(self.current_ball_speed_x)
            # Jugador golpea: -5 confianza
            self.update_confianza(-5)
            # Aumentar ligeramente la velocidad
            self.current_ball_speed_x *= 1.05
            self.current_ball_speed_y *= 1.05
        
        elif self.ball.colliderect(self.ai_paddle):
            self.current_ball_speed_x = -abs(self.current_ball_speed_x)
            # IA golpea: +5 confianza
            self.update_confianza(+5)
            # Aumentar ligeramente la velocidad
            self.current_ball_speed_x *= 1.05
            self.current_ball_speed_y *= 1.05
        
        # Puntos
        if self.ball.left <= 0:
            # IA anota
            self.score_ai += 1
            self.ai_hp = max(0, self.ai_hp - 10)
            self.player_hp = max(0, self.player_hp - 15)
            # +25 confianza para la IA
            self.update_confianza(+25)
            self.reset_ball()
        
        if self.ball.right >= WIDTH:
            # Jugador anota
            self.score_player += 1
            self.ai_hp = max(0, self.ai_hp - 15)
            # -25 confianza para la IA
            self.update_confianza(-25)
            self.reset_ball()
        
        # Actualizar timer de expresión
        if self.expression_timer > 0:
            self.expression_timer -= 1
        
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
        
        # 🎨 Dibujar sprite de la flaca y diálogo
        self.draw_girl_portrait(screen)
        
        # 🔥 Dibujar CONFIANZÓMETRO
        self.draw_confianzometro(screen)
        
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
        
        player_text = self.font_small.render("TÚ", True, WHITE)
        screen.blit(player_text, (52, 50))
        
        # HP IA (derecha)
        pygame.draw.rect(screen, WHITE, (WIDTH - 50 - hp_width - 4, 70, hp_width + 4, hp_height + 4))
        pygame.draw.rect(screen, BLACK, (WIDTH - 50 - hp_width - 2, 72, hp_width, hp_height))
        hp_color = GREEN if self.ai_hp > 50 else YELLOW if self.ai_hp > 25 else RED
        pygame.draw.rect(screen, hp_color, (WIDTH - 50 - hp_width - 2, 72, 
                                           int(hp_width * self.ai_hp / 100), hp_height))
        
        ai_text = self.font_small.render("ELLA", True, WHITE)
        screen.blit(ai_text, (WIDTH - 50 - hp_width - 2, 50))
    
    def draw_girl_portrait(self, screen):
        """Dibuja el retrato de la flaca y su diálogo"""
        portrait_x = WIDTH - 200
        portrait_y = 120
        
        # Fondo del retrato (pixel art style)
        pygame.draw.rect(screen, WHITE, (portrait_x - 5, portrait_y - 5, 170, 170), 2)
        pygame.draw.rect(screen, BLACK, (portrait_x - 3, portrait_y - 3, 166, 166))
        
        # Sprite de la flaca
        if self.current_girl_sprite:
            screen.blit(self.current_girl_sprite, (portrait_x, portrait_y))
        else:
            # Placeholder si no hay sprite
            pygame.draw.circle(screen, (255, 200, 150), (portrait_x + 80, portrait_y + 80), 60)
            pygame.draw.circle(screen, BLACK, (portrait_x + 60, portrait_y + 70), 8)
            pygame.draw.circle(screen, BLACK, (portrait_x + 100, portrait_y + 70), 8)
            
            # Expresión según confianza
            if self.confianza >= 75:
                pygame.draw.arc(screen, BLACK, (portrait_x + 50, portrait_y + 80, 60, 30), 0, 3.14, 2)
            elif self.confianza <= 29:
                pygame.draw.arc(screen, BLACK, (portrait_x + 50, portrait_y + 95, 60, 30), 3.14, 6.28, 2)
            else:
                pygame.draw.line(screen, BLACK, (portrait_x + 55, portrait_y + 100), 
                               (portrait_x + 105, portrait_y + 100), 2)
        
        # Burbuja de diálogo (solo si el timer está activo)
        if self.expression_timer > 0 and self.current_girl_line:
            dialogue_box = pygame.Rect(WIDTH - 370, portrait_y + 170, 360, 80)
            
            # Borde neon
            pygame.draw.rect(screen, CYAN, dialogue_box, 2)
            pygame.draw.rect(screen, BLACK, (dialogue_box.x + 2, dialogue_box.y + 2, 
                                            dialogue_box.width - 4, dialogue_box.height - 4))
            
            # Texto (dividir en líneas)
            words = self.current_girl_line.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                if self.font_dialogue.size(test_line)[0] < dialogue_box.width - 20:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)
            
            for i, line in enumerate(lines[:3]):
                text_surf = self.font_dialogue.render(line, True, WHITE)
                screen.blit(text_surf, (dialogue_box.x + 10, dialogue_box.y + 10 + i * 22))
    
    def draw_confianzometro(self, screen):
        """Dibuja el Confianzómetro (barra de confianza de la IA)"""
        bar_x = WIDTH - 200
        bar_y = 310
        bar_width = 160
        bar_height = 20
        
        # Label
        label = self.font_small.render("CONFIANZA", True, WHITE)
        screen.blit(label, (bar_x, bar_y - 25))
        
        # Borde de la barra (pixel art style)
        pygame.draw.rect(screen, WHITE, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 2)
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
        
        # Color según nivel de confianza
        if self.confianza >= 75:
            bar_color = YELLOW  # Dominante
        elif self.confianza <= 29:
            bar_color = RED     # Enojada
        else:
            bar_color = GREEN   # Neutral
        
        # Relleno de la barra
        fill_width = int(bar_width * (self.confianza / 100))
        if fill_width > 0:
            pygame.draw.rect(screen, bar_color, (bar_x, bar_y, fill_width, bar_height))
        
        # Porcentaje
        percentage = self.font_tiny.render(f"{int(self.confianza)}%", True, WHITE)
        screen.blit(percentage, (bar_x + bar_width + 10, bar_y + 2))
        
        # Emoji según estado
        if self.confianza >= 75:
            emoji = "😈"
        elif self.confianza <= 29:
            emoji = "😡"
        else:
            emoji = "😏"
        
        emoji_surf = self.font_small.render(emoji, True, WHITE)
        screen.blit(emoji_surf, (bar_x + bar_width + 40, bar_y - 2))


def run_game():
    """Función para ejecutar el juego directamente (para compatibilidad con main.py actual)"""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Retro Pong Championship")
    clock = pygame.time.Clock()
    
    # Crear juego en dificultad normal
    game = Game(1)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        game_over = game.update()
        if game_over:
            # Mostrar pantalla de game over simple
            screen.fill(BLACK)
            if game.score_player > game.score_ai:
                text = pygame.font.SysFont("Courier New", 40).render("¡GANASTE!", True, GREEN)
            else:
                text = pygame.font.SysFont("Courier New", 40).render("¡PERDISTE!", True, RED)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False
        else:
            game.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()