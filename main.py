import pygame
import cv2
import mediapipe as mp
import numpy as np
from src.game import Game

pygame.init()

ANCHO, ALTO = 800, 600
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Pong Flaquita - Puño Arriba / Palma Abajo")

# ======== MEDIAPIPE HANDS =========
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
reloj = pygame.time.Clock()

juego = Game(1)  # dificultad normal

def detectar_gesto(hand):
    """
    Detecta:
    - Puño ✊ (todos los dedos cerrados) → UP
    - Palma abierta 🖐️ (todos extendidos) → DOWN
    """
    # Lista de puntas de dedos
    tips = [4, 8, 12, 16, 20]

    dedos_arriba = 0
    for tip in tips[1:]:  # Ignorar el pulgar para evitar errores
        # Si la punta está más arriba que la articulación base -> dedo extendido
        if hand.landmark[tip].y < hand.landmark[tip - 2].y:
            dedos_arriba += 1

    # Si todos los dedos están cerrados → Puño
    if dedos_arriba == 0:
        return "UP"
    # Si 3+ dedos arriba → Palma abierta
    elif dedos_arriba >= 3:
        return "DOWN"
    else:
        return "STOP"  # quieto


ejecutando = True
while ejecutando:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ejecutando = False
    
    ret, frame = cap.read()
    movimiento = 0

    if ret:
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            gesto = detectar_gesto(hand)

            # Mostrar gesto en pantalla (debug)
            cv2.putText(frame, f"{gesto}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            if gesto == "UP":
                movimiento = -7   # SUBE
            elif gesto == "DOWN":
                movimiento = 7    # BAJA
            else:
                movimiento = 0    # QUIETO

            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        # Aplicar movimiento al jugador
        juego.mover_paleta_cabeza(movimiento)

    juego.update()
    juego.draw(ventana)

    # Mostrar cámara pequeña
    if ret:
        cam_small = cv2.resize(frame, (200, 140))
        cam_small = cv2.cvtColor(cam_small, cv2.COLOR_BGR2RGB)
        cam_surface = pygame.surfarray.make_surface(np.rot90(cam_small))
        ventana.blit(cam_surface, (ANCHO - 220, 10))

    pygame.display.flip()
    reloj.tick(60)

cap.release()
pygame.quit()
