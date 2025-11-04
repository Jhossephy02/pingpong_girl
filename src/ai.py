# AI code here
def move_ai(ai_paddle, ball, ai_speed):
    if ball.centery > ai_paddle.centery:
        ai_paddle.y += ai_speed
    else:
        ai_paddle.y -= ai_speed
