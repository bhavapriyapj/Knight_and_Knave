import sys
import random
import pygame

# 1. INITIALIZATION & AUDIO SETUP
pygame.init()
try:
    pygame.mixer.init()
    AUDIO_ENABLED = True
except Exception:
    AUDIO_ENABLED = False

WIDTH, HEIGHT = 950, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Knight & Knave | Mobile Quest")
clock = pygame.time.Clock()

# COLOR PALETTE (Matching CSS Theme)
BG_DARK        = (8, 12, 20)       # #080c14
GOLD_BRIGHT    = (255, 215, 0)     # #ffd700
GOLD_BORDER    = (243, 194, 82)    # #f3c252
WOOD_DARK      = (58, 30, 8)       # #3a1e08
WOOD_MID       = (92, 53, 17)      # #5c3511
WOOD_LIGHT     = (140, 82, 31)     # #8c521f
STONE_BG       = (29, 37, 48)      # #1d2530
STONE_BORDER   = (59, 73, 94)      # #3b495e

JEWEL_PURPLE   = (176, 38, 255)    # #b026ff
JEWEL_GREEN    = (90, 219, 40)     # #5adb28
JEWEL_BLUE     = (0, 191, 255)     # #00bfff
JEWEL_ORANGE   = (255, 152, 0)     # #ff9800

TEXT_LIGHT     = (255, 255, 255)
GRAY_TEXT      = (176, 190, 197)   # #b0bec5
KNAVE_RED      = (229, 57, 53)     # #e53935

# FONTS
FONT_TITLE = pygame.font.SysFont("Georgia", 38, bold=True)
FONT_SUB = pygame.font.SysFont("Arial", 20, bold=True)
FONT_REG = pygame.font.SysFont("Arial", 16)
FONT_SM = pygame.font.SysFont("Arial", 13, bold=True)
FONT_BADGE = pygame.font.SysFont("Georgia", 11, bold=True)

# AUDIO SYNTHESIZER
def play_sound(sound_type):
    if not AUDIO_ENABLED or not audio_toggle:
        return
    try:
        sample_rate = 22050
        if sound_type == "click":
            duration, freq = 0.05, 400
        elif sound_type == "success":
            duration, freq = 0.3, 600
        elif sound_type == "error":
            duration, freq = 0.35, 180
        else:
            return

        n_samples = int(sample_rate * duration)
        buffer = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            val = int(32767 * 0.3 * pygame.math.sin(2 * 3.14159 * freq * t))
            buffer.extend(val.to_bytes(2, byteorder='little', signed=True))
        
        sound = pygame.mixer.Sound(buffer=bytes(buffer))
        sound.play()
    except Exception:
        pass

# PUZZLE DATA STRUCTURE
LEVELS = [
    {
        "name": "EASY",
        "puzzles": [
            { "title": "Trial 1", "description": "A guard speaks.", "characters": [{ "name": "Arin", "statement": "2 + 2 = 4.", "answer": "knight" }], "hint": "2+2=4 is true.", "explanation": "Arin speaks truth, so Arin is a Knight." },
            { "title": "Trial 2", "description": "A guard speaks astronomy.", "characters": [{ "name": "Borin", "statement": "The Sun is a planet.", "answer": "knave" }], "hint": "The Sun is a star.", "explanation": "Borin lies, making him a Knave." },
            { "title": "Trial 3", "description": "Determine Caren's role.", "characters": [{ "name": "Caren", "statement": "I am a Knave.", "answer": "knave" }], "hint": "Knights can't say 'I am a Knave'.", "explanation": "Caren lies, so Caren is a Knave." }
        ]
    },
    {
        "name": "MEDIUM",
        "puzzles": [
            { "title": "Two Guards", "description": "Two linked guards.", "characters": [{ "name": "Arin", "statement": "Borin is a Knave.", "answer": "knave" }, { "name": "Borin", "statement": "Arin and I are different.", "answer": "knight" }], "hint": "Test Borin as Knight.", "explanation": "Arin is Knave, Borin is Knight." },
            { "title": "Royal Oath", "description": "Two guardians.", "characters": [{ "name": "Celia", "statement": "Daren is a Knight.", "answer": "knight" }, { "name": "Daren", "statement": "Celia and I match.", "answer": "knight" }], "hint": "Both can be Knights.", "explanation": "Both are Knights." },
            { "title": "Spy Infiltration", "description": "One is a Spy!", "characters": [{ "name": "Elara", "statement": "Finn is a Knight.", "answer": "spy" }, { "name": "Finn", "statement": "Elara is a Spy.", "answer": "knight" }], "hint": "Check Finn's statement.", "explanation": "Finn is Knight, Elara is Spy." }
        ]
    },
    {
        "name": "HARD",
        "puzzles": [
            { "title": "Triple Trial", "description": "Three guards stand.", "characters": [{ "name": "Arin", "statement": "Borin is a Knave.", "answer": "knave" }, { "name": "Borin", "statement": "Celia is a Knave.", "answer": "knight" }, { "name": "Celia", "statement": "Arin and Borin match.", "answer": "knave" }], "hint": "Arin & Borin are opposite.", "explanation": "Arin=Knave, Borin=Knight, Celia=Knave." },
            { "title": "Spy Court", "description": "1 Knight, 1 Knave, 1 Spy.", "characters": [{ "name": "Daren", "statement": "I am a Spy.", "answer": "spy" }, { "name": "Elara", "statement": "Daren tells truth.", "answer": "knave" }, { "name": "Finn", "statement": "I am a Knight.", "answer": "knight" }], "hint": "Only Spy claims to be Spy.", "explanation": "Daren=Spy, Elara=Knave, Finn=Knight." },
            { "title": "Ultimate Verdict", "description": "Circular claims.", "characters": [{ "name": "Gideon", "statement": "Hala is a Knight.", "answer": "knave" }, { "name": "Hala", "statement": "Ivar is a Knight.", "answer": "knave" }, { "name": "Ivar", "statement": "Gideon and Hala match.", "answer": "knave" }], "hint": "Test all as Knaves.", "explanation": "All three are Knaves!" }
        ]
    }
]

# GLOBAL GAME STATE
current_screen = "intro"  # intro, welcome, map, game, victory
audio_toggle = True
player_name = "Hero"
score = 0
level_index = 0
puzzle_index = 0
hint_used = False
solved = False
selections = []
unlocked_levels = [True, False, False]
achievements = {"noHint": False, "champion": False}

feedback_message = ""
feedback_color = TEXT_LIGHT
hint_visible = False
name_input_text = "Hero"

# BACKGROUND SNOW PARTICLES SYSTEM
particles = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 'r': random.uniform(0.5, 2.5), 'speed': random.uniform(0.2, 0.8)} for _ in range(40)]

def update_and_draw_particles():
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for p in particles:
        p['y'] += p['speed']
        if p['y'] > HEIGHT:
            p['y'] = 0
            p['x'] = random.randint(0, WIDTH)
        pygame.draw.circle(surface, (255, 215, 0, 80), (int(p['x']), int(p['y'])), int(p['r']))
    screen.blit(surface, (0, 0))

# HELPER UI DRAWING FUNCTIONS
def load_puzzle():
    global selections, hint_used, solved, feedback_message, hint_visible
    curr_level = LEVELS[level_index]
    curr_puzzle = curr_level["puzzles"][puzzle_index]
    selections = [None] * len(curr_puzzle["characters"])
    hint_used = False
    solved = False
    feedback_message = ""
    hint_visible = False

def draw_fantasy_button(text, x, y, w, h, bg_color, border_color=GOLD_BRIGHT, font=FONT_SUB, text_color=TEXT_LIGHT):
    mouse_pos = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, w, h)
    is_hover = rect.collidepoint(mouse_pos)
    
    # Render Button Base & Border
    draw_col = tuple(min(255, int(c * 1.15)) for c in bg_color) if is_hover else bg_color
    pygame.draw.rect(screen, draw_col, rect, border_radius=12)
    pygame.draw.rect(screen, border_color, rect, width=3, border_radius=12)
    
    txt_surf = font.render(text, True, text_color)
    screen.blit(txt_surf, txt_surf.get_rect(center=rect.center))
    return rect

def draw_hud_footer():
    hud_rect = pygame.Rect(0, HEIGHT - 65, WIDTH, 65)
    pygame.draw.rect(screen, STONE_BG, hud_rect)
    pygame.draw.rect(screen, GOLD_BRIGHT, pygame.Rect(0, HEIGHT - 65, WIDTH, 3))
    
    # Slot 1: Player Name
    p_txt = FONT_SM.render(f"HERO: {player_name}", True, GOLD_BRIGHT)
    screen.blit(p_txt, (50, HEIGHT - 40))
    
    # Slot 2: Gems
    g_txt = FONT_SM.render(f"GEMS: {score}", True, JEWEL_BLUE)
    screen.blit(g_txt, (WIDTH // 2 - 40, HEIGHT - 40))
    
    # Slot 3: Rank
    rank_str = "ROYAL CHAMPION" if achievements["champion"] else "DETECTIVE"
    r_txt = FONT_SM.render(f"RANK: {rank_str}", True, GOLD_BRIGHT)
    screen.blit(r_txt, (WIDTH - 200, HEIGHT - 40))

# MAIN GAME LOOP
while True:
    screen.fill(BG_DARK)
    update_and_draw_particles()
    mouse_clicked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_clicked = True
                play_sound("click")
        elif event.type == pygame.KEYDOWN:
            if current_screen == "welcome":
                if event.key == pygame.K_RETURN:
                    if name_input_text.strip():
                        player_name = name_input_text.strip()
                    current_screen = "map"
                elif event.key == pygame.K_BACKSPACE:
                    name_input_text = name_input_text[:-1]
                else:
                    if len(name_input_text) < 15 and event.unicode.isprintable():
                        name_input_text += event.unicode

    # SCREEN 1: INTRO (Matching Screenshot 2 Interface)
    if current_screen == "intro":
        # Subtitle Badge
        badge_rect = pygame.Rect(WIDTH // 2 - 120, 160, 240, 26)
        pygame.draw.rect(screen, (255, 215, 0, 30), badge_rect, border_radius=13)
        pygame.draw.rect(screen, GOLD_BRIGHT, badge_rect, width=1, border_radius=13)
        badge_txt = FONT_BADGE.render("A FANTASY LOGIC ADVENTURE", True, GOLD_BRIGHT)
        screen.blit(badge_txt, badge_txt.get_rect(center=badge_rect.center))

        # Logo Title
        title_surf = FONT_TITLE.render("KNIGHT & KNAVE", True, TEXT_LIGHT)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 215)))

        # Menu Buttons
        btn_play = draw_fantasy_button("PLAY GAME", WIDTH // 2 - 140, 275, 280, 50, JEWEL_PURPLE, GOLD_BRIGHT, FONT_SUB)
        
        audio_str = f"AUDIO: {'ON' if audio_toggle else 'OFF'}"
        btn_audio = draw_fantasy_button(audio_str, WIDTH // 2 - 140, 340, 280, 45, JEWEL_BLUE, (128, 222, 234), FONT_REG)

        # Role Preview Cards (Knight, Knave, Spy)
        cards = [
            ("KNIGHT", "ALWAYS TRUTH", GOLD_BRIGHT, 410),
            ("KNAVE", "ALWAYS LIES", JEWEL_PURPLE, 470),
            ("SPY", "TRUTH OR LIE", JEWEL_ORANGE, 530)
        ]
        
        for name, desc, color, y_pos in cards:
            c_rect = pygame.Rect(WIDTH // 2 - 140, y_pos, 280, 50)
            pygame.draw.rect(screen, STONE_BG, c_rect, border_radius=10)
            pygame.draw.rect(screen, color, c_rect, width=2, border_radius=10)
            
            n_surf = FONT_SM.render(name, True, GOLD_BRIGHT)
            d_surf = FONT_SM.render(desc, True, GRAY_TEXT)
            screen.blit(n_surf, (c_rect.x + 20, c_rect.y + 10))
            screen.blit(d_surf, (c_rect.x + 20, c_rect.y + 28))

        if mouse_clicked:
            pos = pygame.mouse.get_pos()
            if btn_play.collidepoint(pos):
                current_screen = "welcome"
            elif btn_audio.collidepoint(pos):
                audio_toggle = not audio_toggle

    # SCREEN 2: PROFILE & ACHIEVEMENTS
    elif current_screen == "welcome":
        panel_rect = pygame.Rect(WIDTH // 2 - 200, 140, 400, 420)
        pygame.draw.rect(screen, WOOD_DARK, panel_rect, border_radius=16)
        pygame.draw.rect(screen, GOLD_BORDER, panel_rect, width=4, border_radius=16)

        header_rect = pygame.Rect(panel_rect.x, panel_rect.y, 400, 50)
        pygame.draw.rect(screen, WOOD_MID, header_rect, border_top_left_radius=16, border_top_right_radius=16)
        pygame.draw.rect(screen, GOLD_BORDER, header_rect, width=2, border_top_left_radius=16, border_top_right_radius=16)
        
        h_txt = FONT_SUB.render("HERO PROFILE", True, GOLD_BRIGHT)
        screen.blit(h_txt, h_txt.get_rect(center=header_rect.center))

        label_txt = FONT_REG.render("DETECTIVE NAME:", True, GOLD_BRIGHT)
        screen.blit(label_txt, (panel_rect.x + 30, panel_rect.y + 80))

        input_rect = pygame.Rect(panel_rect.x + 30, panel_rect.y + 110, 340, 45)
        pygame.draw.rect(screen, STONE_BG, input_rect, border_radius=8)
        pygame.draw.rect(screen, STONE_BORDER, input_rect, width=2, border_radius=8)
        
        in_txt = FONT_REG.render(name_input_text, True, TEXT_LIGHT)
        screen.blit(in_txt, (input_rect.x + 15, input_rect.y + 12))

        btn_submit = draw_fantasy_button("QUEST MAP ->", panel_rect.x + 30, panel_rect.y + 175, 340, 45, JEWEL_GREEN, (165, 214, 167), FONT_REG)

        # Achievements Panel
        ach_box = pygame.Rect(panel_rect.x + 30, panel_rect.y + 245, 340, 140)
        pygame.draw.rect(screen, STONE_BG, ach_box, border_radius=10)
        pygame.draw.rect(screen, STONE_BORDER, ach_box, width=2, border_radius=10)

        ach_title = FONT_SM.render("ACHIEVEMENTS", True, GOLD_BRIGHT)
        screen.blit(ach_title, (ach_box.x + 15, ach_box.y + 15))

        nh_str = "Pure Logic (No Hints)" if achievements["noHint"] else "Pure Logic (Locked)"
        ch_str = "Royal Champion" if achievements["champion"] else "Royal Champion (Locked)"
        
        screen.blit(FONT_SM.render(f"- {nh_str}", True, TEXT_LIGHT if achievements["noHint"] else GRAY_TEXT), (ach_box.x + 15, ach_box.y + 50))
        screen.blit(FONT_SM.render(f"- {ch_str}", True, TEXT_LIGHT if achievements["champion"] else GRAY_TEXT), (ach_box.x + 15, ach_box.y + 85))

        if mouse_clicked and btn_submit.collidepoint(pygame.mouse.get_pos()):
            if name_input_text.strip():
                player_name = name_input_text.strip()
            current_screen = "map"

    # SCREEN 3: MAP SCREEN
    elif current_screen == "map":
        title_surf = FONT_TITLE.render("KINGDOM MAP", True, GOLD_BRIGHT)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 100)))

        node_w = 260
        for i, lvl in enumerate(LEVELS):
            ny = 180 + i * 115
            n_rect = pygame.Rect(WIDTH // 2 - node_w // 2, ny, node_w, 85)
            
            unlocked = unlocked_levels[i]
            bg_col = WOOD_DARK if unlocked else STONE_BG
            
            pygame.draw.rect(screen, bg_col, n_rect, border_radius=14)
            pygame.draw.rect(screen, GOLD_BRIGHT if unlocked else STONE_BORDER, n_rect, width=3, border_radius=14)

            lbl_txt = FONT_SUB.render(f"{lvl['name']} REALM", True, GOLD_BRIGHT if unlocked else GRAY_TEXT)
            screen.blit(lbl_txt, lbl_txt.get_rect(center=n_rect.center))

            if mouse_clicked and unlocked and n_rect.collidepoint(pygame.mouse.get_pos()):
                level_index = i
                puzzle_index = 0
                load_puzzle()
                current_screen = "game"

        btn_prof = draw_fantasy_button("PROFILE", WIDTH // 2 - 100, 550, 200, 40, JEWEL_BLUE, (128, 222, 234), FONT_REG)
        if mouse_clicked and btn_prof.collidepoint(pygame.mouse.get_pos()):
            current_screen = "welcome"

    # SCREEN 4: GAMEPLAY SCREEN
    elif current_screen == "game":
        curr_level = LEVELS[level_index]
        curr_puzzle = curr_level["puzzles"][puzzle_index]

        # Top Bar Info
        screen.blit(FONT_SM.render(f"DIFFICULTY: {curr_level['name']}", True, GOLD_BRIGHT), (50, 25))
        screen.blit(FONT_SM.render(f"Progress: {puzzle_index + 1}/{len(curr_level['puzzles'])}", True, TEXT_LIGHT), (WIDTH - 180, 25))

        screen.blit(FONT_SUB.render(curr_puzzle["title"], True, TEXT_LIGHT), (50, 60))
        screen.blit(FONT_REG.render(curr_puzzle["description"], True, JEWEL_BLUE), (50, 90))

        # Characters Cards Render
        chars = curr_puzzle["characters"]
        card_w = (WIDTH - 100 - (len(chars) - 1) * 20) // len(chars)
        
        for c_idx, char in enumerate(chars):
            cx = 50 + c_idx * (card_w + 20)
            card_rect = pygame.Rect(cx, 130, card_w, 260)
            
            pygame.draw.rect(screen, STONE_BG, card_rect, border_radius=12)
            pygame.draw.rect(screen, STONE_BORDER, card_rect, width=3, border_radius=12)

            screen.blit(FONT_SUB.render(char["name"], True, GOLD_BRIGHT), (cx + 15, 145))
            screen.blit(FONT_SM.render(f'"{char["statement"]}"', True, TEXT_LIGHT), (cx + 15, 180))

            # Verdict Selection Buttons
            choices = ["knight", "knave", "spy"]
            for b_i, choice in enumerate(choices):
                btn_rect = pygame.Rect(cx + 15, 215 + b_i * 42, card_w - 30, 35)
                selected = (selections[c_idx] == choice)
                
                col = JEWEL_GREEN if (selected and choice == "knight") else (KNAVE_RED if (selected and choice == "knave") else (JEWEL_ORANGE if (selected and choice == "spy") else STONE_BG))
                
                pygame.draw.rect(screen, col, btn_rect, border_radius=6)
                pygame.draw.rect(screen, TEXT_LIGHT if selected else STONE_BORDER, btn_rect, width=2, border_radius=6)
                
                b_txt = FONT_SM.render(choice.capitalize(), True, TEXT_LIGHT)
                screen.blit(b_txt, b_txt.get_rect(center=btn_rect.center))

                if mouse_clicked and btn_rect.collidepoint(pygame.mouse.get_pos()):
                    selections[c_idx] = choice

        # Feedback & Hints Display
        if feedback_message:
            fb_surf = FONT_REG.render(feedback_message, True, feedback_color)
            screen.blit(fb_surf, fb_surf.get_rect(center=(WIDTH // 2, 420)))

        if hint_visible:
            hint_surf = FONT_SM.render(f"Hint: {curr_puzzle['hint']}", True, GOLD_BRIGHT)
            screen.blit(hint_surf, hint_surf.get_rect(center=(WIDTH // 2, 455)))

        # Controls
        hint_btn = draw_fantasy_button("Hint", 50, 500, 110, 42, STONE_BG, GOLD_BRIGHT, FONT_REG)
        reset_btn = draw_fantasy_button("Reset", 175, 500, 110, 42, STONE_BG, STONE_BORDER, FONT_REG)
        
        action_str = "Next Puzzle" if solved else "Check Logic"
        action_btn = draw_fantasy_button(action_str, WIDTH - 270, 500, 220, 42, JEWEL_GREEN if solved else JEWEL_PURPLE, GOLD_BRIGHT, FONT_REG)
        map_btn = draw_fantasy_button("Map", 50, 560, 110, 38, STONE_BG, STONE_BORDER, FONT_REG)

        if mouse_clicked:
            pos = pygame.mouse.get_pos()
            if hint_btn.collidepoint(pos):
                hint_used = True
                hint_visible = True
            elif reset_btn.collidepoint(pos):
                load_puzzle()
            elif map_btn.collidepoint(pos):
                current_screen = "map"
            elif action_btn.collidepoint(pos):
                if solved:
                    if puzzle_index < len(curr_level["puzzles"]) - 1:
                        puzzle_index += 1
                        load_puzzle()
                    else:
                        if level_index < len(LEVELS) - 1:
                            unlocked_levels[level_index + 1] = True
                            current_screen = "map"
                        else:
                            achievements["champion"] = True
                            current_screen = "victory"
                else:
                    if None in selections:
                        play_sound("error")
                        feedback_message = "Please assign a verdict to all characters!"
                        feedback_color = KNAVE_RED
                    else:
                        correct = True
                        for idx, char in enumerate(curr_puzzle["characters"]):
                            if selections[idx] != char["answer"]:
                                correct = False
                                break
                        if correct:
                            play_sound("success")
                            solved = True
                            score += 100
                            feedback_message = f"Correct Logic! {curr_puzzle['explanation']}"
                            feedback_color = JEWEL_GREEN

                            if not hint_used and level_index == 2 and puzzle_index == len(curr_level["puzzles"]) - 1:
                                achievements["noHint"] = True
                        else:
                            play_sound("error")
                            feedback_message = "Incorrect logic assessment. Try again!"
                            feedback_color = KNAVE_RED

        draw_hud_footer()

    # SCREEN 5: VICTORY SCREEN (Matching Screenshot 1 Interface)
    elif current_screen == "victory":
        title_surf = FONT_TITLE.render("ROYAL CHAMPION", True, GOLD_BRIGHT)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 220)))

        msg_surf = FONT_SUB.render(f"Congratulations, {player_name}!", True, TEXT_LIGHT)
        screen.blit(msg_surf, msg_surf.get_rect(center=(WIDTH // 2, 290)))

        score_surf = FONT_REG.render(f"Final Gems Earned: {score}", True, JEWEL_BLUE)
        screen.blit(score_surf, score_surf.get_rect(center=(WIDTH // 2, 340)))

        restart_btn = draw_fantasy_button("PLAY AGAIN", WIDTH // 2 - 110, 430, 220, 50, STONE_BG, GOLD_BORDER, FONT_SUB, GOLD_BRIGHT)
        if mouse_clicked and restart_btn.collidepoint(pygame.mouse.get_pos()):
            score = 0
            level_index = 0
            puzzle_index = 0
            unlocked_levels = [True, False, False]
            current_screen = "map"

    pygame.display.flip()
    clock.tick(60)