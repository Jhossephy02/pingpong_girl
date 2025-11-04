# ============================================================================
# src/ai.py - Inteligencia Artificial del Oponente
# ============================================================================

WIDTH, HEIGHT = 800, 600

def move_ai(ai_paddle, ball, ai_speed):
    """
    Mueve la paleta de la IA para seguir la pelota
    
    Args:
        ai_paddle: Rectángulo de la paleta de la IA
        ball: Rectángulo de la pelota
        ai_speed: Velocidad de movimiento de la IA
    """
    # Calcular diferencia entre el centro de la pelota y la paleta
    target_y = ball.centery
    paddle_center_y = ai_paddle.centery
    
    # Calcular distancia
    distance = target_y - paddle_center_y
    
    # Zona muerta para evitar vibración
    dead_zone = 10
    
    # Mover la paleta
    if distance > dead_zone:
        ai_paddle.y += ai_speed
    elif distance < -dead_zone:
        ai_paddle.y -= ai_speed


class AI:
    """
    Clase de IA más avanzada (opcional, para uso futuro)
    Mantiene compatibilidad con el sistema anterior
    """
    
    def __init__(self, paddle, speed, reaction):
        """
        Inicializa la IA
        
        Args:
            paddle: Rectángulo de la paleta de la IA
            speed: Velocidad de movimiento
            reaction: Factor de reacción (0.0 a 1.0)
        """
        self.paddle = paddle
        self.speed = speed
        self.reaction = reaction
    
    def move(self, ball):
        """
        Mueve la paleta de la IA para seguir la pelota con factor de reacción
        
        Args:
            ball: Rectángulo de la pelota
        """
        # Calcular la diferencia entre el centro de la pelota y la paleta
        target_y = ball.centery
        paddle_center_y = self.paddle.centery
        
        # Calcular la distancia
        distance = target_y - paddle_center_y
        
        # Aplicar factor de reacción
        # En dificultades bajas, la IA será más lenta para reaccionar
        effective_distance = distance * self.reaction
        
        # Zona muerta para evitar vibración
        dead_zone = 10
        
        # Mover la paleta
        if abs(effective_distance) > dead_zone:
            if effective_distance > 0 and self.paddle.bottom < HEIGHT:
                self.paddle.y += self.speed
            elif effective_distance < 0 and self.paddle.top > 0:
                self.paddle.y -= self.speed
        
        # Asegurar que la paleta no salga de la pantalla
        if self.paddle.top < 0:
            self.paddle.top = 0
        if self.paddle.bottom > HEIGHT:
            self.paddle.bottom = HEIGHT
    
    def predict_ball_position(self, ball, ball_speed_y):
        """
        Predice la posición futura de la pelota (para IAs muy avanzadas)
        
        Args:
            ball: Rectángulo de la pelota
            ball_speed_y: Velocidad vertical de la pelota
        
        Returns:
            float: Posición Y predicha
        """
        # Calcular cuántos frames hasta que la pelota llegue a la paleta
        distance_to_paddle = abs(ball.x - self.paddle.x)
        
        if distance_to_paddle > 0:
            # Estimar posición Y futura
            frames_to_reach = distance_to_paddle / 10
            predicted_y = ball.y + (ball_speed_y * frames_to_reach)
            
            # Considerar rebotes en paredes
            while predicted_y < 0 or predicted_y > HEIGHT:
                if predicted_y < 0:
                    predicted_y = -predicted_y
                if predicted_y > HEIGHT:
                    predicted_y = 2 * HEIGHT - predicted_y
            
            return predicted_y
        
        return ball.centery