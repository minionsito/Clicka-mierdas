import pygame, sys, random, time, os

pygame.init()

def resource_path(relative_path):
    # Esto permite acceder a assets tanto en .py como en .exe
    try:
        # PyInstaller crea una carpeta temporal `_MEIPASS`
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ---------- Ventana ----------
WIDTH, HEIGHT = 1000, 560
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Caca clicker - by Minion")

# ---------- Reloj ----------
clock = pygame.time.Clock()   # <<--- definir antes de usarlo

# ---------- Colores ----------
WHITE=(255,255,255); BLACK=(0,0,0)
BROWN=(150,100,0); GRAY=(200,200,200); DG=(100,100,100)
GREEN=(0,180,0); SKY=(135,206,250); GRASS=(34,139,34)
GOLD=(255,215,0)

# ---------- Fuentes ----------
font = pygame.font.SysFont(None, 40)
font_small = pygame.font.SysFont(None, 24)
font_tiny = pygame.font.SysFont(None, 20)

def fade_logo():
    logo = pygame.image.load(resource_path("assets/alubia.png")).convert_alpha()

    # Escalar para que quepa en pantalla
    scale_w = WIDTH / logo.get_width()
    scale_h = HEIGHT / logo.get_height()
    scale = min(scale_w, scale_h)
    logo = pygame.transform.smoothscale(logo, (int(logo.get_width()*scale), int(logo.get_height()*scale)))

    # Centrar
    logo_rect = logo.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))  # <-- aquí puedes moverlo un poco arriba

    clock = pygame.time.Clock()
    alpha = 0
    fade_in = True
    display_time = 1500
    hold_timer = 0

    running = True
    while running:
        dt = clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0,0,0))

        # Fade in / hold / fade out
        if fade_in:
            alpha += 300 * (dt / 1000)
            if alpha >= 255:
                alpha = 255
                fade_in = False
        elif hold_timer < display_time:
            hold_timer += dt
        else:
            alpha -= 300 * (dt / 1000)
            if alpha <= 0:
                running = False
                alpha = 0

        screen.fill((0,0,0))
        screen.blit(logo, logo_rect)
        overlay.set_alpha(int(255 - alpha))
        screen.blit(overlay, (0,0))
        pygame.display.flip()


# ---------- Menú principal ----------
def main_menu():
    options = ["Jugar", "Créditos", "Salir"]
    selected = 0
    running_menu = True
    while running_menu:
        screen.fill(SKY)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP: selected = (selected-1) % len(options)
                if e.key == pygame.K_DOWN: selected = (selected+1) % len(options)
                if e.key == pygame.K_RETURN:
                    if options[selected] == "Jugar":
                        running_menu = False
                    elif options[selected] == "Créditos":
                        show_credits()
                    elif options[selected] == "Salir":
                        pygame.quit(); sys.exit()

        for i, opt in enumerate(options):
            color = GREEN if i==selected else BLACK
            txt = font.render(opt, True, color)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 + i*60))

        pygame.display.flip()
        clock.tick(60)

# ---------- Créditos ----------
def show_credits():
    showing = True
    while showing:
        screen.fill(SKY)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                showing = False
        credits_text = [
            "Caca Clicker 2025",
            "Desarrollado por Minion",
            "Powered by Alubia Games",
            "",
            "Presiona ESC para volver"
        ]
        for i, line in enumerate(credits_text):
            txt = font_small.render(line, True, BLACK)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 100 + i*40))
        pygame.display.flip()
        clock.tick(60)

# ---------- LLAMADAS ----------
fade_logo()  # << tu logo
main_menu()                       # << muestra el menú antes de arrancar el juego


# ---------- Estado base ----------
count = 0                    # cacas actuales
total_clicked = 0            # cacas hechas a mano (para logros)
cpc_base = 1                 # cacas por click base
click_mult = 1.0             # multiplicador temporal (eventos/buffs)
cps_mult = 1.0               # multiplicador temporal para CPS

# Cono de caca (click principal)
caca_radius = 70
caca_center = [WIDTH//3, HEIGHT//3]  # arriba en el cielo
caca_scale = 1.0
caca_scale_speed = 0

# ---------- Mejoras (suben CPC) ----------
# tip: cost crece suave para que sientas progreso
upgrades = [{"name": f"Caca Nivel {i+1}", "cost": 10*(i+1), "bonus": (i%4)+1} for i in range(30)]
upgrade_index = 0
UPG_VISIBLE = 7

# ---------- Herramientas (CPS) ----------
tools = [
    {"name":"Perro", "cost":50, "cps":1, "owned":0},
    {"name":"Gato", "cost":200, "cps":5, "owned":0},
    {"name":"Vaca", "cost":1000, "cps":20, "owned":0},
    {"name":"Burro", "cost":5000, "cps":55, "owned":0},
    {"name":"Cerdo", "cost":15000, "cps":150, "owned":0},
]
tool_index = 0
TOOL_VISIBLE = 7
special_unlocked = False   # para el combo Perrógato

# ---------- Logros ----------
achievements = set()
def try_achievements():
    if total_clicked >= 100: achievements.add("100 clics")
    if total_clicked >= 1000: achievements.add("1K clics")
    if total_clicked >= 10000: achievements.add("10K clics")
    if any(u["name"].startswith("Pirámide") for u in upgrades) and total_clicked >= 1:
        achievements.add("Primera pirámide (click)")
    if next((t for t in tools if t["name"]=="Perro"), None) and next(t for t in tools if t["name"]=="Perro")["owned"] >= 5:
        achievements.add("5 Perros")

# ---------- Eventos estilo Roblox ----------
EVENT_INTERVAL = 150.0   # cada 2:30 min
EVENT_DURATION = 120.0   # dura 2 min
last_event_time = time.time()
event_active = False
event_time_left = 0.0

# ---------- Caca dorada (random + durante eventos) ----------
gold_active = False
gold_pos = [0,0]
gold_timer = 0.0
gold_value = 200
gold_next_spawn = time.time() + random.uniform(20, 45)

def spawn_gold():
    global gold_active, gold_pos, gold_timer
    gold_active = True
    gold_pos = [random.randint(120, WIDTH-320), random.randint(80, HEIGHT-160)]
    gold_timer = 7.0  # segundos para hacer click

# ---------- Minijuego: caca dorada cayendo durante eventos ----------
fall_active = False
fall_pos = [0,0]
fall_speed = 0.0
fall_timer = 0.0

def start_fall_minigame():
    global fall_active, fall_pos, fall_speed, fall_timer
    fall_active = True
    fall_pos = [random.randint(160, WIDTH-360), -30]
    fall_speed = random.uniform(120, 180)  # px/seg
    fall_timer = 10.0  # dura 10s o hasta que toque suelo

# ---------- Fondo/Decoración ----------
clouds = [{"x": random.randint(0, WIDTH), "y": random.randint(30, 140), "speed": random.uniform(20, 40)} for _ in range(5)]
birds  = [{"x": random.randint(0, WIDTH), "y": random.randint(80, 180), "speed": random.uniform(50, 80)} for _ in range(3)]
day_phase = 0.0  # 0..1 (ciclo día-tarde-noche-día). Lo hago triangular suave.

# ---------- Utiles ----------
def cpc_current():
    return int(cpc_base * click_mult)

def total_cps():
    base = sum(t["cps"]*t["owned"] for t in tools)
    return base * cps_mult

def golpe_caca():
    global caca_scale, caca_scale_speed
    caca_scale = 1.2
    caca_scale_speed = -2.5  # volver rápido
def update_caca_anim(dt):
    global caca_scale, caca_scale_speed
    if caca_scale > 1.0:
        caca_scale += caca_scale_speed * dt
        if caca_scale <= 1.0:
            caca_scale = 1.0
            caca_scale_speed = 0

def draw_cone(center, r, color):
    pygame.draw.polygon(screen, color, [
        (center[0], center[1]-r),
        (center[0]-r, center[1]+r),
        (center[0]+r, center[1]+r)
    ])
    # pequeña “sombra” en el borde
    pygame.draw.lines(screen, (110,70,0), True, [
        (center[0], center[1]-r),
        (center[0]-r, center[1]+r),
        (center[0]+r, center[1]+r)
    ], 2)

def draw_gold_cone(pos, r=18):
    pygame.draw.polygon(screen, GOLD, [
        (pos[0], pos[1]-r),
        (pos[0]-r, pos[1]+r),
        (pos[0]+r, pos[1]+r)
    ])
    pygame.draw.lines(screen, (200,170,0), True, [
        (pos[0], pos[1]-r),
        (pos[0]-r, pos[1]+r),
        (pos[0]+r, pos[1]+r)
    ], 2)

def point_in_cone(px, py, cx, cy, r):
    # aproximamos por círculo circunscrito para click sencillo
    dx, dy = px-cx, py-cy
    return dx*dx + dy*dy <= r*r

# ---------- Bucle ----------
clock = pygame.time.Clock()
accum_cps = 0.0

running = True
while running:
    dt_ms = clock.tick(60)
    dt = dt_ms / 1000.0

    # --- Eventos pygame ---
    mx, my = pygame.mouse.get_pos()
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_w: upgrade_index = max(0, upgrade_index-1)
            if e.key == pygame.K_s: upgrade_index = min(max(0, len(upgrades)-UPG_VISIBLE), upgrade_index+1)
            if e.key == pygame.K_UP: tool_index = max(0, tool_index-1)
            if e.key == pygame.K_DOWN: tool_index = min(max(0, len(tools)-TOOL_VISIBLE), tool_index+1)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            # Click caca
            r = int(caca_radius * caca_scale)
            if point_in_cone(mx, my, caca_center[0], caca_center[1], r):
                gained = cpc_current()
                count += gained
                total_clicked += gained
                golpe_caca()
                try_achievements()

            # Click mejoras visibles
            for i in range(UPG_VISIBLE):
                idx = upgrade_index + i
                if idx >= len(upgrades): break
                rect = pygame.Rect(WIDTH-400+20, 60 + i*64, 200-40, 58)
                if rect.collidepoint(mx,my):
                    upg = upgrades[idx]
                    if count >= upg["cost"]:
                        count -= upg["cost"]
                        cpc_base += upg["bonus"]
                        # subir precio para siguiente (sensación progreso)
                        upg["cost"] = int(upg["cost"] * 1.6)

            # Click herramientas visibles
            for i in range(TOOL_VISIBLE):
                idx = tool_index + i
                if idx >= len(tools): break
                rect = pygame.Rect(WIDTH-200+20, 60 + i*64, 200-40, 58)
                if rect.collidepoint(mx,my):
                    tl = tools[idx]
                    if count >= tl["cost"]:
                        count -= tl["cost"]
                        tl["owned"] += 1
                        tl["cost"] = int(tl["cost"] * 1.5)

            # Click caca dorada
            if gold_active:
                if point_in_cone(mx, my, gold_pos[0], gold_pos[1], 22):
                    gold_active = False
                    # premio: gran cantidad + mini buff de click
                    count += gold_value
                    click_mult = 2.0
                    # pequeño temporizador de buff rápido
                    gold_timer = 3.0

            # Click minijuego: caca dorada cayendo
            if fall_active:
                if point_in_cone(mx, my, fall_pos[0], fall_pos[1], 22):
                    fall_active = False
                    count += 500
                    click_mult = 2.0
                    cps_mult = 2.0
                    fall_timer = 0.0

    # --- Lógica de eventos estilo Roblox ---
    now = time.time()
    if not event_active and (now - last_event_time) >= EVENT_INTERVAL:
        event_active = True
        event_time_left = EVENT_DURATION
        last_event_time = now
        click_mult = 2.0
        cps_mult = 2.0
        # arrancar minijuego al comienzo del evento
        start_fall_minigame()

    if event_active:
        event_time_left -= dt
        if event_time_left <= 0:
            event_active = False
            click_mult = 1.0
            cps_mult = 1.0
            fall_active = False
            fall_timer = 0.0

    # --- Spawns de caca dorada random (fuera y dentro de eventos) ---
    if not gold_active and time.time() >= gold_next_spawn:
        spawn_gold()
        gold_next_spawn = time.time() + random.uniform(25, 60)

    if gold_active:
        gold_timer -= dt
        if gold_timer <= 0:
            gold_active = False

    # --- Minijuego: caca dorada cayendo (solo en evento) ---
    if fall_active:
        fall_timer -= dt
        fall_pos[1] += fall_speed * dt
        if fall_pos[1] > HEIGHT-40 or fall_timer <= 0:
            fall_active = False

    # --- Desbloqueo de combo especial (Perrógato) ---
    if not special_unlocked:
        perro = next((t for t in tools if t["name"]=="Perro"), None)
        gato  = next((t for t in tools if t["name"]=="Gato"), None)
        if perro and gato and perro["owned"]>=5 and gato["owned"]>=3:
            tools.append({"name":"Perrógato", "cost":25000, "cps":500, "owned":0})
            special_unlocked = True

    # --- Generación automática por CPS ---
    accum_cps += total_cps() * dt
    if accum_cps >= 1.0:
        add_int = int(accum_cps)
        count += add_int
        accum_cps -= add_int

    # --- Anim/Decoración: nubes y pájaros, ciclo día ---
    for c in clouds:
        c["x"] += c["speed"]*dt
        if c["x"] > WIDTH+80:
            c["x"] = -120
            c["y"] = random.randint(30, 140)
    for b in birds:
        b["x"] -= b["speed"]*dt
        if b["x"] < -40:
            b["x"] = WIDTH + 60
            b["y"] = random.randint(80, 180)

    day_phase = (day_phase + dt/60.0) % 1.0  # ciclo ~1 min
    # aclara/oscurece cielo levemente
    sky_tint = int(20 * abs(0.5 - day_phase))
    sky_color = (max(0, SKY[0]-sky_tint), max(0, SKY[1]-sky_tint), min(255, SKY[2]+sky_tint))

    # --- Anim principal de la caca ---
    update_caca_anim(dt)

    # ============== DIBUJO ==============
    # Fondo
    screen.fill(sky_color)
    pygame.draw.rect(screen, GRASS, (0, HEIGHT//2, WIDTH, HEIGHT//2))

    # Nubes
    for c in clouds:
        pygame.draw.ellipse(screen, WHITE, (c["x"], c["y"], 120, 50))
        pygame.draw.ellipse(screen, WHITE, (c["x"]+30, c["y"]-10, 90, 45))
        pygame.draw.ellipse(screen, WHITE, (c["x"]+60, c["y"], 120, 50))
    # Pájaros (v invertida)
    for b in birds:
        pygame.draw.lines(screen, BLACK, False, [(b["x"], b["y"]), (b["x"]+10, b["y"]-8), (b["x"]+20, b["y"])], 2)

    # Caca principal (cono)
    draw_cone(caca_center, int(caca_radius*caca_scale), BROWN)

    # HUD superior: cacas, cpc y cps, evento
    hud = f"Cacas: {count}   CPC: {cpc_current()}   CPS: {int(total_cps())}"
    if event_active:
        hud += f"   EVENTO x2 ({int(event_time_left)}s)"
    text = font.render(hud, True, BLACK)
    screen.blit(text, (20, 16))

    # Menú Mejoras (izquierda derecha: columna 1)
    pygame.draw.rect(screen, GRAY, (WIDTH-400, 0, 200, HEIGHT))
    screen.blit(font.render("Mejoras", True, BLACK), (WIDTH-380, 10))
    for i in range(UPG_VISIBLE):
        idx = upgrade_index + i
        if idx >= len(upgrades): break
        upg = upgrades[idx]
        rect = pygame.Rect(WIDTH-400+20, 60 + i*64, 160, 54)
        pygame.draw.rect(screen, GREEN if count>=upg["cost"] else DG, rect, border_radius=8)
        screen.blit(font_small.render(upg["name"], True, WHITE), (rect.x+8, rect.y+6))
        screen.blit(font_tiny.render(f"{upg['cost']} cacas  (+{upg['bonus']} CPC)", True, WHITE), (rect.x+8, rect.y+30))
    # indicador de página
    page_u = f"{upgrade_index+1}-{min(upgrade_index+UPG_VISIBLE,len(upgrades))}/{len(upgrades)}"
    screen.blit(font_tiny.render(page_u, True, BLACK), (WIDTH-340, HEIGHT-24))

    # Menú Herramientas (columna 2)
    pygame.draw.rect(screen, GRAY, (WIDTH-200, 0, 200, HEIGHT))
    screen.blit(font.render("Herramientas", True, BLACK), (WIDTH-190, 10))
    for i in range(TOOL_VISIBLE):
        idx = tool_index + i
        if idx >= len(tools): break
        tl = tools[idx]
        rect = pygame.Rect(WIDTH-200+20, 60 + i*64, 160, 54)
        pygame.draw.rect(screen, GREEN if count>=tl["cost"] else DG, rect, border_radius=8)
        screen.blit(font_small.render(f"{tl['name']}  x{tl['owned']}", True, WHITE), (rect.x+8, rect.y+6))
        screen.blit(font_tiny.render(f"{tl['cost']} cacas  ({tl['cps']} CPS)", True, WHITE), (rect.x+8, rect.y+30))
    page_t = f"{tool_index+1}-{min(tool_index+TOOL_VISIBLE,len(tools))}/{len(tools)}"
    screen.blit(font_tiny.render(page_t, True, BLACK), (WIDTH-140, HEIGHT-24))

    # Caca dorada random
    if gold_active:
        draw_gold_cone(gold_pos, 20)
        screen.blit(font_tiny.render(f"{int(gold_timer)}s", True, BLACK), (gold_pos[0]-10, gold_pos[1]+26))

    # Minijuego: caca dorada cayendo (solo durante evento)
    if fall_active:
        draw_gold_cone(fall_pos, 20)
        screen.blit(font_tiny.render("¡Atrápala!", True, BLACK), (fall_pos[0]-30, fall_pos[1]+26))

    # Logros (mini badges en la esquina)
    if achievements:
        screen.blit(font_small.render("Logros:", True, BLACK), (20, HEIGHT-80))
        x = 100
        for a in sorted(list(achievements))[:6]:
            pygame.draw.rect(screen, GOLD, (x, HEIGHT-86, 20, 20))
            screen.blit(font_tiny.render("✔", True, BLACK), (x+5, HEIGHT-86))
            screen.blit(font_tiny.render(a, True, BLACK), (x+28, HEIGHT-82))
            x += 160

    pygame.display.flip()

pygame.quit()
sys.exit()
