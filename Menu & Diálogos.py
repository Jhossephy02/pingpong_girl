# ============================================================================
# main.py - RETRO PONG CHAMPIONSHIP
# ============================================================================
"""
RETRO PONG CHAMPIONSHIP - Archivo Principal
Juego profesional de Ping Pong con menú completo, sistema de diálogos estilo FNF,
barras de HP estilo Pokémon y múltiples dificultades.

Estructura del proyecto:
- main.py: Punto de entrada y menús principales
- src/game.py: Lógica del juego
- src/characters.py: Personajes y diálogos
- src/ai.py: Inteligencia artificial
- assets/: Recursos (sonidos e imágenes)
"""

import pygame
import sys
import os
from src.game import Game
from src.characters import Character

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

# Configuración
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 128, 0)

class PongGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Retro Pong Championship")
        self.clock = pygame.time.Clock()
        
        # Fuentes
        self.font_title = pygame.font.SysFont("Courier New", 60, bold=True)
        self.font_menu = pygame.font.SysFont("Courier New", 30)
        self.font_small = pygame.font.SysFont("Courier New", 20)
        self.font_dialogue = pygame.font.SysFont("Courier New", 18)
        
        # Estado del juego
        self.state = "MENU"  # MENU, SETTINGS, DIFFICULTY, DIALOGUE, GAME, GAME_OVER
        self.selected_option = 0
        self.selected_difficulty = 1
        
        # Configuración
        self.music_volume = 50
        self.sfx_volume = 50
        self.language = "ES"
        
        # Juego
        self.game = None
        self.character = None
        
        # Diálogo
        self.dialogue_index = 0
        self.dialogue_char_index = 0
        self.dialogue_timer = 0
        
        # Cargar sonidos
        self.load_sounds()
        
        # Textos
        self.texts = {
            "ES": {
                "title": "RETRO PONG",
                "subtitle": "Championship Edition",
                "start": "INICIAR",
                "settings": "AJUSTES",
                "exit": "SALIR",
                "music": "Música",
                "sfx": "Efectos",
                "language": "Idioma",
                "back": "Volver",
                "difficulty": "Selecciona Dificultad",
                "easy": "FÁCIL",
                "normal": "NORMAL",
                "hard": "DIFÍCIL",
                "god": "DIOS",
                "player": "Jugador",
                "opponent": "Oponente",
                "victory": "¡VICTORIA!",
                "defeat": "¡DERROTA!",
                "final_score": "Puntuación Final",
                "menu": "[ESPACIO] Menú Principal"
            },
            "EN": {
                "title": "RETRO PONG",
                "subtitle": "Championship Edition",
                "start": "START",
                "settings": "SETTINGS",
                "exit": "EXIT",
                "music": "Music",
                "sfx": "Sound FX",
                "language": "Language",
                "back": "Back",
                "difficulty": "Select Difficulty",
                "easy": "EASY",
                "normal": "NORMAL",
                "hard": "HARD",
                "god": "GOD",
                "player": "Player",
                "opponent": "Opponent",
                "victory": "VICTORY!",
                "defeat": "DEFEAT!",
                "final_score": "Final Score",
                "menu": "[SPACE] Main Menu"
            }
        }
    
    def load_sounds(self):
        """Carga los sonidos del juego"""
        try:
            self.sound_bounce = pygame.mixer.Sound("assets/sounds/bounce.mp3")
            self.sound_hit = pygame.mixer.Sound("assets/sounds/hit.mp3")
            self.sound_score = pygame.mixer.Sound("assets/sounds/score.mp3")
        except:
            print("⚠️ No se pudieron cargar los sonidos. El juego continuará sin audio.")
            self.sound_bounce = None
            self.sound_hit = None
            self.sound_score = None
    
    def play_sound(self, sound):
        """Reproduce un sonido con el volumen configurado"""
        if sound:
            sound.set_volume(self.sfx_volume / 100)
            sound.play()
    
    def get_text(self, key):
        """Obtiene texto en el idioma actual"""
        return self.texts[self.language].get(key, key)
    
    def draw_menu(self):
        """Dibuja el menú principal"""
        self.screen.fill(BLACK)
        
        # Título
        title = self.font_title.render(self.get_text("title"), True, CYAN)
        subtitle = self.font_small.render(self.get_text("subtitle"), True, GREEN)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        self.screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 150))
        
        # Opciones
        menu_options = [
            self.get_text("start"),
            self.get_text("settings"),
            self.get_text("exit")
        ]
        
        for i, option in enumerate(menu_options):
            color = YELLOW if i == self.selected_option else WHITE
            prefix = "> " if i == self.selected_option else "  "
            text = self.font_menu.render(prefix + option, True, color)
            self.screen.blit(text, (WIDTH//2 - 100, 250 + i * 60))
        
        # Decoración
        for i in range(0, WIDTH, 40):
            pygame.draw.circle(self.screen, DARK_GREEN, (i, HEIGHT - 20), 3)
    
    def draw_settings(self):
        """Dibuja el menú de ajustes"""
        self.screen.fill(BLACK)
        
        title = self.font_menu.render(self.get_text("settings"), True, CYAN)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Música
        music_text = self.font_small.render(f"{self.get_text('music')}: {self.music_volume}%", True, WHITE)
        self.screen.blit(music_text, (150, 150))
        pygame.draw.rect(self.screen, GRAY, (150, 180, 400, 20))
        pygame.draw.rect(self.screen, GREEN, (150, 180, int(400 * self.music_volume / 100), 20))
        
        # SFX
        sfx_text = self.font_small.render(f"{self.get_text('sfx')}: {self.sfx_volume}%", True, WHITE)
        self.screen.blit(sfx_text, (150, 250))
        pygame.draw.rect(self.screen, GRAY, (150, 280, 400, 20))
        pygame.draw.rect(self.screen, GREEN, (150, 280, int(400 * self.sfx_volume / 100), 20))
        
        # Idioma
        lang_text = self.font_small.render(f"{self.get_text('language')}: {self.language}", True, WHITE)
        self.screen.blit(lang_text, (150, 350))
        
        # Indicador
        options_y = [170, 270, 350]
        pygame.draw.polygon(self.screen, YELLOW, [
            (130, options_y[self.selected_option]),
            (130, options_y[self.selected_option] + 20),
            (140, options_y[self.selected_option] + 10)
        ])
        
        # Volver
        back_text = self.font_small.render(f"[ESC] {self.get_text('back')}", True, GRAY)
        self.screen.blit(back_text, (WIDTH//2 - back_text.get_width()//2, HEIGHT - 50))
    
    def draw_difficulty(self):
        """Dibuja la selección de dificultad"""
        self.screen.fill(BLACK)
        
        title = self.font_menu.render(self.get_text("difficulty"), True, CYAN)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        
        difficulties = [
            self.get_text("easy"),
            self.get_text("normal"),
            self.get_text("hard"),
            self.get_text("god")
        ]
        colors = [GREEN, YELLOW, ORANGE, RED]
        
        for i, diff in enumerate(difficulties):
            color = colors[i] if i == self.selected_difficulty else WHITE
            size = 35 if i == self.selected_difficulty else 25
            diff_font = pygame.font.SysFont("Courier New", size, bold=(i == self.selected_difficulty))
            text = diff_font.render(diff, True, color)
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, 200 + i * 80))
            
            if i == self.selected_difficulty:
                pygame.draw.rect(self.screen, color, 
                               (WIDTH//2 - text.get_width()//2 - 10,
                                200 + i * 80 - 5,
                                text.get_width() + 20,
                                size + 10), 2)
    
    def draw_dialogue(self):
        """Dibuja el diálogo con barras de HP estilo Pokémon"""
        self.screen.fill(BLACK)
        
        # Barras de HP
        bar_width = 300
        bar_height = 30
        
        # HP Jugador (izquierda)
        pygame.draw.rect(self.screen, WHITE, (50, 50, bar_width + 10, bar_height + 10))
        pygame.draw.rect(self.screen, BLACK, (55, 55, bar_width, bar_height))
        hp_color = GREEN if self.game.player_hp > 50 else YELLOW if self.game.player_hp > 25 else RED
        pygame.draw.rect(self.screen, hp_color, (55, 55, int(bar_width * self.game.player_hp / 100), bar_height))
        player_text = self.font_small.render(self.get_text("player"), True, WHITE)
        self.screen.blit(player_text, (55, 25))
        
        # HP Oponente (derecha)
        pygame.draw.rect(self.screen, WHITE, (WIDTH - 50 - bar_width - 10, 50, bar_width + 10, bar_height + 10))
        pygame.draw.rect(self.screen, BLACK, (WIDTH - 50 - bar_width - 5, 55, bar_width, bar_height))
        hp_color = GREEN if self.character.hp > 50 else YELLOW if self.character.hp > 25 else RED
        pygame.draw.rect(self.screen, hp_color, (WIDTH - 50 - bar_width - 5, 55, int(bar_width * self.character.hp / 100), bar_height))
        opponent_text = self.font_small.render(self.get_text("opponent"), True, WHITE)
        self.screen.blit(opponent_text, (WIDTH - 50 - bar_width - 5, 25))
        
        # Imagen del personaje (si existe)
        if self.character.image:
            img_rect = self.character.image.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            self.screen.blit(self.character.image, img_rect)
        
        # Caja de diálogo estilo Pokémon
        dialogue_box = pygame.Rect(50, HEIGHT - 180, WIDTH - 100, 130)
        pygame.draw.rect(self.screen, WHITE, dialogue_box)
        pygame.draw.rect(self.screen, BLACK, (dialogue_box.x + 5, dialogue_box.y + 5,
                                              dialogue_box.width - 10, dialogue_box.height - 10))
        
        # Texto con efecto typewriter
        current_dialogue = self.character.dialogues[self.dialogue_index]
        displayed_text = current_dialogue[:self.dialogue_char_index]
        
        # Dividir en líneas
        words = displayed_text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if self.font_dialogue.size(test_line)[0] < dialogue_box.width - 40:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        # Dibujar líneas
        for i, line in enumerate(lines[:4]):
            text_surf = self.font_dialogue.render(line, True, WHITE)
            self.screen.blit(text_surf, (dialogue_box.x + 20, dialogue_box.y + 20 + i * 25))
        
        # Indicador de continuar
        if self.dialogue_char_index >= len(current_dialogue):
            arrow = self.font_small.render("▼", True, YELLOW)
            self.screen.blit(arrow, (dialogue_box.right - 30, dialogue_box.bottom - 30))
            hint = self.font_small.render("[ESPACIO]", True, GRAY)
            self.screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))
    
    def draw_game_over(self):
        """Dibuja la pantalla de game over"""
        self.screen.fill(BLACK)
        
        winner_text = self.get_text("victory") if self.game.score_player > self.game.score_ai else self.get_text("defeat")
        color = GREEN if self.game.score_player > self.game.score_ai else RED
        
        title = self.font_title.render(winner_text, True, color)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        
        final_score = self.font_menu.render(
            f"{self.get_text('final_score')}: {self.game.score_player} - {self.game.score_ai}",
            True, WHITE
        )
        self.screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, 250))
        
        hint = self.font_small.render(self.get_text("menu"), True, GRAY)
        self.screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 100))
    
    def handle_menu_input(self, event):
        """Maneja input del menú principal"""
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % 3
            self.play_sound(self.sound_hit)
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % 3
            self.play_sound(self.sound_hit)
        elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
            self.play_sound(self.sound_hit)
            if self.selected_option == 0:  # Iniciar
                self.state = "DIFFICULTY"
                self.selected_difficulty = 1
            elif self.selected_option == 1:  # Ajustes
                self.state = "SETTINGS"
                self.selected_option = 0
            elif self.selected_option == 2:  # Salir
                return False
        return True
    
    def handle_settings_input(self, event):
        """Maneja input de ajustes"""
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % 3
            self.play_sound(self.sound_hit)
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % 3
            self.play_sound(self.sound_hit)
        elif event.key == pygame.K_LEFT:
            if self.selected_option == 0:
                self.music_volume = max(0, self.music_volume - 10)
            elif self.selected_option == 1:
                self.sfx_volume = max(0, self.sfx_volume - 10)
            elif self.selected_option == 2:
                self.language = "EN" if self.language == "ES" else "ES"
            self.play_sound(self.sound_hit)
        elif event.key == pygame.K_RIGHT:
            if self.selected_option == 0:
                self.music_volume = min(100, self.music_volume + 10)
            elif self.selected_option == 1:
                self.sfx_volume = min(100, self.sfx_volume + 10)
            elif self.selected_option == 2:
                self.language = "EN" if self.language == "ES" else "ES"
            self.play_sound(self.sound_hit)
        elif event.key == pygame.K_ESCAPE:
            self.state = "MENU"
            self.selected_option = 0
            self.play_sound(self.sound_hit)
    
    def handle_difficulty_input(self, event):
        """Maneja input de selección de dificultad"""
        if event.key == pygame.K_UP:
            self.selected_difficulty = (self.selected_difficulty - 1) % 4
            self.play_sound(self.sound_hit)
        elif event.key == pygame.K_DOWN:
            self.selected_difficulty = (self.selected_difficulty + 1) % 4
            self.play_sound(self.sound_hit)
        elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
            self.state = "DIALOGUE"
            self.dialogue_index = 0
            self.dialogue_char_index = 0
            self.dialogue_timer = 0
            
            # Crear personaje y juego
            self.character = Character(self.selected_difficulty)
            self.game = Game(self.selected_difficulty)
            self.play_sound(self.sound_hit)
        elif event.key == pygame.K_ESCAPE:
            self.state = "MENU"
            self.selected_option = 0
            self.play_sound(self.sound_hit)
    
    def handle_dialogue_input(self, event):
        """Maneja input del diálogo"""
        if event.key == pygame.K_SPACE:
            if self.dialogue_char_index >= len(self.character.dialogues[self.dialogue_index]):
                self.dialogue_index += 1
                if self.dialogue_index >= len(self.character.dialogues):
                    self.state = "GAME"
                else:
                    self.dialogue_char_index = 0
                    self.dialogue_timer = 0
            else:
                self.dialogue_char_index = len(self.character.dialogues[self.dialogue_index])
            self.play_sound(self.sound_hit)
    
    def update_dialogue(self):
        """Actualiza el efecto typewriter del diálogo"""
        self.dialogue_timer += 1
        if self.dialogue_timer > 2:
            if self.dialogue_char_index < len(self.character.dialogues[self.dialogue_index]):
                self.dialogue_char_index += 1
                self.dialogue_timer = 0
                # Sonido FNF aleatorio
                if pygame.time.get_ticks() % 3 == 0:
                    self.play_sound(self.sound_bounce)
    
    def run(self):
        """Loop principal del juego"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if self.state == "MENU":
                        running = self.handle_menu_input(event)
                    elif self.state == "SETTINGS":
                        self.handle_settings_input(event)
                    elif self.state == "DIFFICULTY":
                        self.handle_difficulty_input(event)
                    elif self.state == "DIALOGUE":
                        self.handle_dialogue_input(event)
                    elif self.state == "GAME":
                        if event.key == pygame.K_ESCAPE:
                            self.state = "MENU"
                            self.selected_option = 0
                    elif self.state == "GAME_OVER":
                        if event.key == pygame.K_SPACE:
                            self.state = "MENU"
                            self.selected_option = 0
                            self.play_sound(self.sound_hit)
            
            # Actualizar según estado
            if self.state == "DIALOGUE":
                self.update_dialogue()
            elif self.state == "GAME":
                game_over = self.game.update()
                if game_over:
                    self.state = "GAME_OVER"
                    self.character.hp = self.game.ai_hp
            
            # Dibujar según estado
            if self.state == "MENU":
                self.draw_menu()
            elif self.state == "SETTINGS":
                self.draw_settings()
            elif self.state == "DIFFICULTY":
                self.draw_difficulty()
            elif self.state == "DIALOGUE":
                self.draw_dialogue()
            elif self.state == "GAME":
                self.game.draw(self.screen)
            elif self.state == "GAME_OVER":
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PongGame()
    game.run()