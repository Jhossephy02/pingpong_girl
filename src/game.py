# ============================================================================
# src/game.py - Pong con Caja de Diálogo Fija Abajo (Estilo Undertale)
# ============================================================================

import pygame
import random
from src.ai import move_ai
from src.characters import load_girl_sprites, get_expression_by_confianza

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 128, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_BLUE = (30, 30, 60)
BEIGE = (240, 224, 200)

# Configuración del juego
WIDTH, HEIGHT = 800, 600
GAME_AREA_HEIGHT = 450  # El juego ocupa solo la parte superior
DIALOGUE_BOX_HEIGHT = 150  # Altura de la caja de diálogo fija

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
        
        # Paletas (ajustadas para el área de juego más pequeña)
        self.player_paddle = pygame.Rect(30, GAME_AREA_HEIGHT//2 - PADDLE_HEIGHT//2, 
                                        PADDLE_WIDTH, PADDLE_HEIGHT)
        self.ai_paddle = pygame.Rect(WIDTH - 40, GAME_AREA_HEIGHT//2 - PADDLE_HEIGHT//2, 
                                     PADDLE_WIDTH, PADDLE_HEIGHT)
        
        # Pelota
        self.ball = pygame.Rect(WIDTH//2, GAME_AREA_HEIGHT//2, BALL_SIZE, BALL_SIZE)
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
        except Exception as e:
            print(f"⚠️ No se pudieron cargar los sprites: {e}")
            self.girl_sprites = None
            self.current_girl_sprite = None
            self.current_girl_line = "¡Vamos!"
        
        # Fuentes
        self.font_score = pygame.font.SysFont("Courier New", 40, bold=True)
        self.font_small = pygame.font.SysFont("Courier New", 18)
        self.font_dialogue = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_tiny = pygame.font.SysFont("Courier New", 12)
        
        # 🎮 Trail de la pelota
        self.ball_trail = []
        self.max_trail_length = 8
        
        # Timer para animación de texto
        self.text_animation_frame = 0
    
    def reset_ball(self):
        """Reinicia la posición de la pelota"""
        self.ball.center = (WIDTH//2, GAME_AREA_HEIGHT//2)
        settings = self.difficulty_settings[self.difficulty]
        self.ball_speed_x = settings["ball_speed"] * random.choice([-1, 1])
        self.ball_speed_y = settings["ball_speed"] * random.choice([-1, 1])
        self.current_ball_speed_x = self.ball_speed_x
        self.current_ball_speed_y = self.ball_speed_y
        self.ball_trail.clear()
    
    def update_confianza(self, change):
        """Actualiza el confianzómetro y cambia la expresión si es necesario"""
        old_confianza = self.confianza
        self.confianza = max(0, min(100, self.confianza + change))
        
        # Solo actualizar expresión si cambió de rango significativo
        old_state = self.get_confianza_state(old_confianza)
        new_state = self.get_confianza_state(self.confianza)
        
        if old_state != new_state and self.girl_sprites:
            self.current_girl_sprite, self.current_girl_line = get_expression_by_confianza(
                self.confianza, self.girl_sprites
            )
    
    def get_confianza_state(self, confianza):
        """Retorna el estado según la confianza (0=enojada, 1=neutral, 2=smug)"""
        if confianza >= 75:
            return 2  # Smug
        elif confianza <= 29:
            return 0  # Angry
        else:
            return 1  # Neutral
    
    def update(self):
        """
        Actualiza la lógica del juego
        Retorna True si el juego terminó
        """
        # Movimiento del jugador
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.player_paddle.top > 0:
            self.player_paddle.y -= self.player_speed
        if keys[pygame.K_s] and self.player_paddle.bottom < GAME_AREA_HEIGHT:
            self.player_paddle.y += self.player_speed
        
        # Movimiento de la IA
        move_ai(self.ai_paddle, self.ball, self.ai_speed)
        
        # Asegurar que las paletas no salgan del área de juego
        if self.player_paddle.top < 0:
            self.player_paddle.top = 0
        if self.player_paddle.bottom > GAME_AREA_HEIGHT:
            self.player_paddle.bottom = GAME_AREA_HEIGHT
        
        if self.ai_paddle.top < 0:
            self.ai_paddle.top = 0
        if self.ai_paddle.bottom > GAME_AREA_HEIGHT:
            self.ai_paddle.bottom = GAME_AREA_HEIGHT
        
        # 🎮 Guardar posición anterior para trail
        self.ball_trail.append((self.ball.x, self.ball.y))
        if len(self.ball_trail) > self.max_trail_length:
            self.ball_trail.pop(0)
        
        # Movimiento de la pelota
        self.ball.x += self.current_ball_speed_x
        self.ball.y += self.current_ball_speed_y
        
        # Rebote en paredes superior e inferior (solo en área de juego)
        if self.ball.top <= 0 or self.ball.bottom >= GAME_AREA_HEIGHT:
            self.current_ball_speed_y *= -1
            if self.ball.top <= 0:
                self.ball.top = 0
            if self.ball.bottom >= GAME_AREA_HEIGHT:
                self.ball.bottom = GAME_AREA_HEIGHT
        
        # Colisión con paletas
        if self.ball.colliderect(self.player_paddle):
            self.current_ball_speed_x = abs(self.current_ball_speed_x)
            # Jugador golpea: -5 confianza
            self.update_confianza(-5)
            # Aumentar ligeramente la velocidad
            self.current_ball_speed_x *= 1.05
            self.current_ball_speed_y *= 1.05
            # Efecto de rebote variado según dónde golpea
            hit_pos = (self.ball.centery - self.player_paddle.centery) / (PADDLE_HEIGHT / 2)
            self.current_ball_speed_y += hit_pos * 2
        
        elif self.ball.colliderect(self.ai_paddle):
            self.current_ball_speed_x = -abs(self.current_ball_speed_x)
            # IA golpea: +5 confianza
            self.update_confianza(+5)
            # Aumentar ligeramente la velocidad
            self.current_ball_speed_x *= 1.05
            self.current_ball_speed_y *= 1.05
            # Efecto de rebote variado
            hit_pos = (self.ball.centery - self.ai_paddle.centery) / (PADDLE_HEIGHT / 2)
            self.current_ball_speed_y += hit_pos * 2
        
        # Limitar velocidad máxima
        max_speed = 25
        if abs(self.current_ball_speed_x) > max_speed:
            self.current_ball_speed_x = max_speed if self.current_ball_speed_x > 0 else -max_speed
        if abs(self.current_ball_speed_y) > max_speed:
            self.current_ball_speed_y = max_speed if self.current_ball_speed_y > 0 else -max_speed
        
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
        
        # Actualizar animación de texto
        self.text_animation_frame += 1
        
        # Verificar fin del juego
        if (self.player_hp <= 0 or self.ai_hp <= 0 or 
            self.score_player >= 12 or self.score_ai >= 12):
            return True
        
        return False
    
    def draw(self, screen):
        """Dibuja el juego en la pantalla"""
        screen.fill(BLACK)
        
        # ========== ÁREA DE JUEGO (ARRIBA) ==========
        
        # Línea central punteada
        for y in range(0, GAME_AREA_HEIGHT, 20):
            pygame.draw.rect(screen, DARK_GREEN, (WIDTH//2 - 2, y, 4, 10))
        
        # 🎮 Trail de la pelota
        for i, (x, y) in enumerate(self.ball_trail):
            alpha = int(255 * (i / len(self.ball_trail)))
            size = int(BALL_SIZE * (i / len(self.ball_trail)))
            if size > 2:
                trail_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.ellipse(trail_surf, (*YELLOW, alpha), (0, 0, size, size))
                screen.blit(trail_surf, (x, y))
        
        # Paletas con efecto glow
        pygame.draw.rect(screen, GREEN, self.player_paddle)
        pygame.draw.rect(screen, GREEN, self.player_paddle.inflate(4, 4), 2)
        
        pygame.draw.rect(screen, CYAN, self.ai_paddle)
        pygame.draw.rect(screen, CYAN, self.ai_paddle.inflate(4, 4), 2)
        
        # Pelota
        pygame.draw.ellipse(screen, YELLOW, self.ball)
        pygame.draw.ellipse(screen, WHITE, self.ball.inflate(4, 4), 1)
        
        # Marcador con sombra
        score_text = self.font_score.render(
            f"{self.score_player}  :  {self.score_ai}", 
            True, WHITE
        )
        shadow = self.font_score.render(
            f"{self.score_player}  :  {self.score_ai}", 
            True, GRAY
        )
        screen.blit(shadow, (WIDTH//2 - score_text.get_width()//2 + 2, 22))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))
        
        # Barras de HP
        self.draw_hp_bars(screen)
        
        # Línea divisoria entre juego y caja de diálogo
        pygame.draw.line(screen, WHITE, (0, GAME_AREA_HEIGHT), (WIDTH, GAME_AREA_HEIGHT), 3)
        
        # ========== CAJA DE DIÁLOGO (ABAJO) - SIEMPRE VISIBLE ==========
        self.draw_undertale_dialogue_box(screen)
        
        # Controles (arriba a la derecha)
        controls = self.font_tiny.render("[W/S] Mover  [ESC] Menú", True, GRAY)
        screen.blit(controls, (WIDTH - controls.get_width() - 10, 10))
    
    def draw_hp_bars(self, screen):
        """Dibuja las barras de HP en el juego"""
        hp_width = 120
        hp_height = 12
        
        # HP Jugador (izquierda)
        pygame.draw.rect(screen, WHITE, (30, 70, hp_width + 4, hp_height + 4))
        pygame.draw.rect(screen, BLACK, (32, 72, hp_width, hp_height))
        hp_color = GREEN if self.player_hp > 50 else YELLOW if self.player_hp > 25 else RED
        pygame.draw.rect(screen, hp_color, (32, 72, int(hp_width * self.player_hp / 100), hp_height))
        
        player_text = self.font_small.render("TÚ", True, WHITE)
        screen.blit(player_text, (32, 52))
        
        # HP IA (derecha)
        pygame.draw.rect(screen, WHITE, (WIDTH - 30 - hp_width - 4, 70, hp_width + 4, hp_height + 4))
        pygame.draw.rect(screen, BLACK, (WIDTH - 30 - hp_width - 2, 72, hp_width, hp_height))
        hp_color = GREEN if self.ai_hp > 50 else YELLOW if self.ai_hp > 25 else RED
        pygame.draw.rect(screen, hp_color, (WIDTH - 30 - hp_width - 2, 72, 
                                           int(hp_width * self.ai_hp / 100), hp_height))
        
        ai_text = self.font_small.render("ELLA", True, WHITE)
        screen.blit(ai_text, (WIDTH - 30 - hp_width - 2, 52))
    
    def draw_undertale_dialogue_box(self, screen):
        """Dibuja la caja de diálogo fija abajo (estilo Undertale/Pokémon)"""
        
        box_y = GAME_AREA_HEIGHT
        box_height = HEIGHT - GAME_AREA_HEIGHT
        
        # Fondo de la caja
        pygame.draw.rect(screen, BLACK, (0, box_y, WIDTH, box_height))
        
        # Borde exterior blanco (estilo Pokémon GBA)
        border_margin = 15
        inner_box = pygame.Rect(border_margin, box_y + border_margin, 
                                WIDTH - border_margin * 2, box_height - border_margin * 2)
        
        pygame.draw.rect(screen, WHITE, inner_box, 0)
        pygame.draw.rect(screen, BLACK, (inner_box.x + 4, inner_box.y + 4, 
                                         inner_box.width - 8, inner_box.height - 8), 0)
        pygame.draw.rect(screen, BEIGE, (inner_box.x + 6, inner_box.y + 6, 
                                         inner_box.width - 12, inner_box.height - 12), 0)
        
        # === RETRATO DE LA FLACA (IZQUIERDA) ===
        portrait_size = 100
        portrait_x = inner_box.x + 10
        portrait_y = inner_box.y + (inner_box.height - portrait_size) // 2
        
        # Borde del retrato
        pygame.draw.rect(screen, BLACK, (portrait_x - 2, portrait_y - 2, 
                                        portrait_size + 4, portrait_size + 4), 0)
        pygame.draw.rect(screen, WHITE, (portrait_x - 2, portrait_y - 2, 
                                        portrait_size + 4, portrait_size + 4), 2)
        
        # Fondo del retrato
        pygame.draw.rect(screen, DARK_BLUE, (portrait_x, portrait_y, portrait_size, portrait_size), 0)
        
        # Sprite de la flaca
        if self.current_girl_sprite:
            scaled_sprite = pygame.transform.scale(self.current_girl_sprite, (portrait_size, portrait_size))
            screen.blit(scaled_sprite, (portrait_x, portrait_y))
        else:
            # Placeholder
            pygame.draw.circle(screen, (255, 200, 150), 
                             (portrait_x + portrait_size//2, portrait_y + portrait_size//2), 40)
            pygame.draw.circle(screen, BLACK, 
                             (portrait_x + portrait_size//2 - 15, portrait_y + portrait_size//2 - 10), 5)
            pygame.draw.circle(screen, BLACK, 
                             (portrait_x + portrait_size//2 + 15, portrait_y + portrait_size//2 - 10), 5)
        
        # === ÁREA DE TEXTO (DERECHA) ===
        text_x = portrait_x + portrait_size + 15
        text_y = inner_box.y + 15
        text_width = inner_box.width - portrait_size - 40
        
        # Dividir texto en líneas
        words = self.current_girl_line.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if self.font_dialogue.size(test_line)[0] < text_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        # Dibujar texto (máximo 2 líneas)
        for i, line in enumerate(lines[:2]):
            # Sombra
            shadow = self.font_dialogue.render(line, True, GRAY)
            screen.blit(shadow, (text_x + 1, text_y + 1 + i * 22))
            
            # Texto principal
            text_surf = self.font_dialogue.render(line, True, BLACK)
            screen.blit(text_surf, (text_x, text_y + i * 22))
        
        # === BARRA DE CONFIANZA (DEBAJO DEL TEXTO) ===
        conf_bar_x = text_x
        conf_bar_y = text_y + 55
        conf_bar_width = 150
        conf_bar_height = 12
        
        # Label
        conf_label = self.font_tiny.render("CONFIANZA", True, BLACK)
        screen.blit(conf_label, (conf_bar_x, conf_bar_y - 13))
        
        # Borde de la barra
        pygame.draw.rect(screen, BLACK, (conf_bar_x - 1, conf_bar_y - 1, 
                                        conf_bar_width + 2, conf_bar_height + 2), 2)
        pygame.draw.rect(screen, WHITE, (conf_bar_x, conf_bar_y, conf_bar_width, conf_bar_height))
        
        # Color según confianza
        if self.confianza >= 75:
            bar_color = ORANGE  # Dominante
        elif self.confianza <= 29:
            bar_color = RED     # Enojada
        else:
            bar_color = GREEN   # Neutral
        
        fill_width = int(conf_bar_width * (self.confianza / 100))
        if fill_width > 0:
            pygame.draw.rect(screen, bar_color, (conf_bar_x, conf_bar_y, fill_width, conf_bar_height))
        
        # Porcentaje
        percentage_text = self.font_tiny.render(f"{int(self.confianza)}%", True, BLACK)
        screen.blit(percentage_text, (conf_bar_x + conf_bar_width + 8, conf_bar_y + 1))
        
        # Emoji según estado
        emoji = self.get_confianza_emoji()
        emoji_surf = self.font_small.render(emoji, True, BLACK)
        screen.blit(emoji_surf, (conf_bar_x + conf_bar_width + 35, conf_bar_y - 3))
        
        # === INDICADOR DE ESTADO (ESQUINA INFERIOR DERECHA) ===
        state_text = self.get_state_text()
        state_color = self.get_state_color()
        state_surf = self.font_tiny.render(state_text, True, state_color)
        screen.blit(state_surf, (WIDTH - state_surf.get_width() - 20, HEIGHT - 20))
    
    def get_confianza_emoji(self):
        """Retorna el emoji según el nivel de confianza"""
        if self.confianza >= 75:
            return "😈"
        elif self.confianza <= 29:
            return "😡"
        else:
            return "😏"
    
    def get_state_text(self):
        """Retorna el texto de estado según confianza"""
        if self.confianza >= 75:
            return "* Dominante"
        elif self.confianza <= 29:
            return "* Enojada"
        else:
            return "* Neutral"
    
    def get_state_color(self):
        """Retorna el color del estado"""
        if self.confianza >= 75:
            return ORANGE
        elif self.confianza <= 29:
            return RED
        else:
            return GREEN


def run_game():
    """Función para ejecutar el juego directamente"""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Retro Pong Championship")
    clock = pygame.time.Clock()
    
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