# ============================================================================
# src/game.py - Pong con Caja de Diálogo estilo Pokémon
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
        except Exception as e:
            print(f"⚠️ No se pudieron cargar los sprites: {e}")
            self.girl_sprites = None
            self.current_girl_sprite = None
            self.current_girl_line = "¡Vamos!"
        
        # Control de cambio de expresión
        self.expression_timer = 0
        self.expression_duration = 180  # 3 segundos (60 FPS)
        
        # Fuentes
        self.font_score = pygame.font.SysFont("Courier New", 40, bold=True)
        self.font_small = pygame.font.SysFont("Courier New", 20)
        self.font_dialogue = pygame.font.SysFont("Arial", 18, bold=True)  # Estilo Pokémon
        self.font_tiny = pygame.font.SysFont("Courier New", 14)
        
        # 🎮 Trail de la pelota (efecto visual)
        self.ball_trail = []
        self.max_trail_length = 8
    
    def reset_ball(self):
        """Reinicia la posición de la pelota"""
        self.ball.center = (WIDTH//2, HEIGHT//2)
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
            # Reiniciar timer para mostrar la nueva expresión
            self.expression_timer = self.expression_duration
    
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
        if keys[pygame.K_s] and self.player_paddle.bottom < HEIGHT:
            self.player_paddle.y += self.player_speed
        
        # Movimiento de la IA
        move_ai(self.ai_paddle, self.ball, self.ai_speed)
        
        # Asegurar que las paletas no salgan de la pantalla
        self.player_paddle.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        if self.ai_paddle.top < 0:
            self.ai_paddle.top = 0
        if self.ai_paddle.bottom > HEIGHT:
            self.ai_paddle.bottom = HEIGHT
        
        # 🎮 Guardar posición anterior para trail
        self.ball_trail.append((self.ball.x, self.ball.y))
        if len(self.ball_trail) > self.max_trail_length:
            self.ball_trail.pop(0)
        
        # Movimiento de la pelota
        self.ball.x += self.current_ball_speed_x
        self.ball.y += self.current_ball_speed_y
        
        # Rebote en paredes superior e inferior
        if self.ball.top <= 0 or self.ball.bottom >= HEIGHT:
            self.current_ball_speed_y *= -1
            self.ball.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        
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
        max_speed = 15
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
        
        # Línea central punteada
        for y in range(0, HEIGHT, 20):
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
        
        # 🎨 Caja de diálogo estilo Pokémon
        self.draw_pokemon_dialogue_box(screen)
        
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
    
    def draw_pokemon_dialogue_box(self, screen):
        """Dibuja la caja de diálogo estilo Pokémon GBA con imagen de la flaca"""
        
        # Solo mostrar si hay diálogo activo
        if self.expression_timer <= 0:
            return
        
        # Dimensiones de la caja (estilo Pokémon GBA)
        box_x = 30
        box_y = HEIGHT - 140
        box_width = WIDTH - 60
        box_height = 110
        
        # Imagen de la flaca (lado derecho, como rival de Pokémon)
        portrait_size = 90
        portrait_x = box_x + box_width - portrait_size - 15
        portrait_y = box_y + 10
        
        # === CAJA PRINCIPAL (estilo Pokémon) ===
        # Borde exterior blanco grueso
        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), 0)
        
        # Borde negro intermedio
        pygame.draw.rect(screen, BLACK, (box_x + 4, box_y + 4, box_width - 8, box_height - 8), 0)
        
        # Fondo beige interno (estilo GBA)
        pygame.draw.rect(screen, BEIGE, (box_x + 8, box_y + 8, box_width - 16, box_height - 16), 0)
        
        # === CONTENEDOR DE IMAGEN ===
        # Borde de la imagen (lado derecho)
        img_border_rect = pygame.Rect(portrait_x - 4, portrait_y - 4, portrait_size + 8, portrait_size + 8)
        pygame.draw.rect(screen, BLACK, img_border_rect, 0)
        pygame.draw.rect(screen, WHITE, img_border_rect, 3)
        
        # Fondo de la imagen
        pygame.draw.rect(screen, DARK_BLUE, (portrait_x, portrait_y, portrait_size, portrait_size), 0)
        
        # === IMAGEN DE LA FLACA ===
        if self.current_girl_sprite:
            # Escalar imagen para que quepa en el cuadro
            scaled_sprite = pygame.transform.scale(self.current_girl_sprite, (portrait_size, portrait_size))
            screen.blit(scaled_sprite, (portrait_x, portrait_y))
        else:
            # Placeholder si no hay sprite
            pygame.draw.circle(screen, (255, 200, 150), 
                             (portrait_x + portrait_size//2, portrait_y + portrait_size//2), 35)
            pygame.draw.circle(screen, BLACK, (portrait_x + portrait_size//2 - 12, portrait_y + portrait_size//2 - 8), 5)
            pygame.draw.circle(screen, BLACK, (portrait_x + portrait_size//2 + 12, portrait_y + portrait_size//2 - 8), 5)
        
        # === ÁREA DE TEXTO ===
        text_x = box_x + 20
        text_y = box_y + 20
        text_width = box_width - portrait_size - 50
        
        # Dividir texto en líneas que quepan
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
        
        # Dibujar texto (máximo 3 líneas)
        for i, line in enumerate(lines[:3]):
            # Sombra del texto
            shadow = self.font_dialogue.render(line, True, GRAY)
            screen.blit(shadow, (text_x + 2, text_y + 2 + i * 28))
            
            # Texto principal
            text_surf = self.font_dialogue.render(line, True, BLACK)
            screen.blit(text_surf, (text_x, text_y + i * 28))
        
        # === INDICADOR DE CONFIANZA (mini barra estilo Pokémon) ===
        conf_bar_x = text_x
        conf_bar_y = box_y + box_height - 25
        conf_bar_width = 100
        conf_bar_height = 10
        
        # Label
        conf_label = self.font_tiny.render("CONFIANZA", True, BLACK)
        screen.blit(conf_label, (conf_bar_x, conf_bar_y - 15))
        
        # Barra
        pygame.draw.rect(screen, BLACK, (conf_bar_x, conf_bar_y, conf_bar_width, conf_bar_height))
        
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
        screen.blit(percentage_text, (conf_bar_x + conf_bar_width + 5, conf_bar_y - 2))
        
        # === FLECHA PARPADEANTE (indicador de continuar) ===
        if pygame.time.get_ticks() % 1000 < 500:  # Parpadea cada medio segundo
            arrow_x = box_x + box_width - 25
            arrow_y = box_y + box_height - 20
            pygame.draw.polygon(screen, BLACK, [
                (arrow_x, arrow_y),
                (arrow_x + 10, arrow_y),
                (arrow_x + 5, arrow_y + 8)
            ])


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