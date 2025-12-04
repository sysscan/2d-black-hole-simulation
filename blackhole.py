import pygame, math, random, sys
pygame.init()
w, h = 900, 900
screen = pygame.display.set_mode((w, h))
clock = pygame.time.Clock()
pygame.display.set_caption("Black Hole Simulation - Press L for Labels, H for Help")

center = (w // 2, h // 2)
black = (0, 0, 0)

G = 6.67430e-11
c = 299792458
M_solar = 1.989e30
M_bh = 10 * M_solar

rs = 2 * G * M_bh / (c * c)
rs_pixels = 90
scale = rs_pixels / rs

photon_sphere_radius = 1.5 * rs_pixels
isco_radius = 3 * rs_pixels
event_horizon_radius = rs_pixels

show_labels = False
show_help = False

font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 18)

stars = []
for _ in range(600):
    x = random.randint(0, w)
    y = random.randint(0, h)
    b = random.randint(150, 255)
    stars.append((x, y, (b, b, b)))

particles = []
for _ in range(1200):
    radius = random.uniform(isco_radius + 10, 350)
    angle = random.uniform(0, 2 * math.pi)
    v_kepler = math.sqrt(G * M_bh / (radius / scale))
    v_pixels = v_kepler * scale
    beta = v_pixels / (c * scale)
    gamma = 1 / math.sqrt(1 - beta * beta) if beta < 0.99 else 10
    particles.append({
        "r": radius,
        "angle": angle,
        "speed": v_pixels / radius,
        "beta": beta,
        "gamma": gamma,
        "trail": []
    })

jets = []
for _ in range(150):
    side = random.choice([-1, 1])
    distance = random.uniform(event_horizon_radius + 30, 450)
    spread = random.uniform(-0.15, 0.15)
    speed = random.uniform(0.3 * c * scale, 0.95 * c * scale)
    jets.append({
        "side": side,
        "distance": distance,
        "spread": spread,
        "speed": speed,
        "beta": speed / (c * scale)
    })

photon_ring = []
for _ in range(200):
    angle = random.uniform(0, 2 * math.pi)
    v_photon = c * scale / photon_sphere_radius
    speed = v_photon / photon_sphere_radius
    offset = random.uniform(-2, 2)
    photon_ring.append({
        "angle": angle,
        "speed": speed,
        "offset": offset
    })

hawking_particles = []
for _ in range(20):
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(event_horizon_radius + 2, event_horizon_radius + 8)
    speed = random.uniform(0.2, 0.8)
    life = random.randint(15, 40)
    hawking_particles.append({
        "angle": angle,
        "distance": distance,
        "speed": speed,
        "life": life,
        "max_life": life
    })

tidal_bodies = []
tidal_fragments = []
next_tidal_spawn = 0

time = 0


def temperature_to_color(temp):
    if temp <= 1000:
        r = int(255 * (temp / 1000))
        return (r, 0, 0)
    elif temp <= 3000:
        g = int(180 * ((temp - 1000) / 2000))
        return (255, g, 0)
    elif temp <= 6000:
        g = 180 + int(75 * ((temp - 3000) / 3000))
        b = int(200 * ((temp - 3000) / 3000))
        return (255, g, b)
    else:
        return (220, 220, 255)


def accretion_disk_temperature(radius):
    if radius < isco_radius:
        return 0
    r_m = radius / scale
    T = 2.2e7 * (M_solar / M_bh) ** 0.25 * (r_m / rs) ** -0.75
    return min(T, 15000)


def deflection_angle(r):
    if r <= event_horizon_radius:
        return math.pi
    return 2 * rs_pixels / r


def draw_lensed_background():
    for x, y, color in stars:
        dx = x - center[0]
        dy = y - center[1]
        r = math.hypot(dx, dy)

        if r < 420:
            if r <= event_horizon_radius:
                continue

            theta = math.atan2(dy, dx)
            alpha = deflection_angle(r)
            defl = alpha * (event_horizon_radius / r)

            new_theta = theta + defl
            magnification = 1 + 0.8 * (event_horizon_radius / r) ** 2

            nx = center[0] + math.cos(new_theta) * r * magnification
            ny = center[1] + math.sin(new_theta) * r * magnification

            if 0 <= nx < w and 0 <= ny < h:
                b = min(255, int(color[0] * magnification))
                pygame.draw.circle(screen, (b, b, b), (int(nx), int(ny)), 1)
        else:
            pygame.draw.circle(screen, color, (x, y), 1)


def draw_ergosphere():
    base = event_horizon_radius * 1.15
    for i in range(8):
        alpha = 26 - i * 3
        radius = int(base + i * 3)
        clr = (140 + i * 8, 90 + i * 4, 200 - i * 10)
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*clr, alpha), (radius, radius), radius, 1)
        screen.blit(surf, (center[0] - radius, center[1] - radius))


def draw_photon_sphere():
    ring_radius = int(photon_sphere_radius * 1.1)
    for p in photon_ring:
        angle = p["angle"]
        radius = ring_radius + p["offset"]
        x = center[0] + math.cos(angle) * radius
        y = center[1] + math.sin(angle) * radius
        b = int(200 + 35 * math.sin(angle * 4 + time * 0.08))
        size = 1 + int(math.sin(angle * 3) * 0.5)
        pygame.draw.circle(screen, (b, b, 230), (int(x), int(y)), size)
        p["angle"] += p["speed"]


def draw_hawking_radiation():
    for h in hawking_particles:
        angle = h["angle"]
        dist = h["distance"]
        x = center[0] + math.cos(angle) * dist
        y = center[1] + math.sin(angle) * dist
        fade = h["life"] / h["max_life"]
        b = int(70 * fade)
        if b > 6:
            pygame.draw.circle(screen, (b, b, b + 30), (int(x), int(y)), 1)
        h["distance"] += h["speed"]
        h["life"] -= 1
        if h["life"] <= 0:
            h["angle"] = random.uniform(0, 2 * math.pi)
            h["distance"] = random.uniform(event_horizon_radius + 2, event_horizon_radius + 8)
            h["life"] = h["max_life"]


def draw_relativistic_jets():
    for jet in jets:
        side = jet["side"]
        dist = jet["distance"]
        spread = jet["spread"]
        beta = jet["beta"]

        x = center[0] + spread * 18
        y = center[1] + side * dist

        fade = max(0, min(1, 1 - (dist - event_horizon_radius - 30) / 330))
        gamma = 1 / math.sqrt(1 - beta * beta) if beta < 0.99 else 10
        dop = gamma * (1 + beta)

        glow = fade * dop * 0.28

        color = (
            min(255, int(90 * glow)),
            min(255, int(140 * glow)),
            min(255, int(255 * glow)),
        )

        size = int(2 + fade * 1.5)
        pygame.draw.circle(screen, color, (int(x), int(y)), size)

        if fade > 0.2:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, int(30 * fade)), (8, 8), 8)
            screen.blit(s, (int(x) - 8, int(y) - 8))

        jet["distance"] += jet["speed"] * 0.016

        if jet["distance"] > 450:
            jet["distance"] = event_horizon_radius + 30
            jet["spread"] = random.uniform(-0.15, 0.15)


def draw_gravitational_lensing_rings():
    base = int(photon_sphere_radius * 1.1)
    for i in range(3):
        radius = base + i * 6
        b = 220 - i * 50
        pygame.draw.circle(screen, (b, b - 30, min(255, b + 40)), center, radius, 1)


def draw_accretion_disk_doppler():
    inner = int(isco_radius * 1.05)
    outer = 360
    crescent_angle = -math.pi / 2  # brightest at bottom

    for radius in range(inner, outer, 4):
        v_kepler = math.sqrt(G * M_bh / (radius / scale))
        beta = min(0.99, v_kepler / c)
        gamma = 1 / math.sqrt(1 - beta * beta)

        temp = accretion_disk_temperature(radius)
        base_color = temperature_to_color(temp)

        phase = time * 0.002 * (isco_radius / radius) ** 1.5

        for deg in range(0, 360, 3):
            angle = math.radians(deg) + phase

            x = center[0] + math.cos(angle) * radius
            y = center[1] + math.sin(angle) * radius

            cos_los = math.cos(angle)
            dop = gamma * (1 + beta * cos_los)

            mult = dop ** 3 if cos_los > 0 else (1 / dop) ** 2

            crescent = max(0.0, math.cos(angle - crescent_angle))
            crescent = crescent ** 2
            if crescent < 0.05:
                continue
            mult *= (0.5 + 1.8 * crescent)

            r_c = min(255, int(base_color[0] * mult))
            g_c = min(255, int(base_color[1] * mult))
            b_c = min(255, int(base_color[2] * mult))

            size = 2 if radius < (inner + outer) // 2 else 1

            pygame.draw.circle(screen, (r_c, g_c, b_c), (int(x), int(y)), size)


def draw_blackhole_core():
    draw_ergosphere()
    draw_gravitational_lensing_rings()
    draw_photon_sphere()
    draw_hawking_radiation()

    glow_r = event_horizon_radius + 22
    for i in range(10):
        a = 40 - i * 4
        surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (200, 170, 120, a), (glow_r, glow_r), glow_r - i * 2)
        screen.blit(surf, (center[0] - glow_r, center[1] - glow_r))

    pygame.draw.circle(screen, black, center, event_horizon_radius)

    for i in range(18):
        shade = int(8 + (1 - i / 18) * 40)
        pygame.draw.circle(screen, (shade, shade, shade), center, event_horizon_radius + i, 1)


def draw_particles():
    for p in particles:
        r = p["r"]
        angle = p["angle"]

        if r < isco_radius:
            p["r"] = random.uniform(isco_radius + 20, 350)
            p["angle"] = random.uniform(0, 2 * math.pi)
            v_kepler = math.sqrt(G * M_bh / (p["r"] / scale))
            v_pixels = v_kepler * scale
            p["speed"] = v_pixels / p["r"]
            p["beta"] = v_pixels / (c * scale)
            p["gamma"] = 1 / math.sqrt(1 - p["beta"] * p["beta"]) if p["beta"] < 0.99 else 10
            p["trail"] = []
            continue

        x = center[0] + math.cos(angle) * r
        y = center[1] + math.sin(angle) * r

        temp = accretion_disk_temperature(r)
        base_color = temperature_to_color(temp)

        cos_los = math.cos(angle)
        dop = p["gamma"] * (1 + p["beta"] * cos_los)

        mult = dop ** 2.5 if cos_los > 0 else (1 / dop) ** 1.8

        color = (
            min(255, int(base_color[0] * mult)),
            min(255, int(base_color[1] * mult)),
            min(255, int(base_color[2] * mult)),
        )

        p["trail"].append((x, y, color))
        if len(p["trail"]) > 12:
            p["trail"].pop(0)

        for i, t in enumerate(p["trail"]):
            fade = (i + 1) / len(p["trail"])
            dim = (
                int(t[2][0] * fade * 0.6),
                int(t[2][1] * fade * 0.6),
                int(t[2][2] * fade * 0.6),
            )
            pygame.draw.circle(screen, dim, (int(t[0]), int(t[1])), 1)

        pygame.draw.circle(screen, color, (int(x), int(y)), 2)

        p["angle"] += p["speed"]

        visc = 0.0001 * (r / isco_radius) ** -2
        p["r"] -= visc * r


def spawn_tidal_body():
    spawn_r = random.uniform(480, 620)
    angle = random.uniform(0, 2 * math.pi)

    vr = -random.uniform(0.8, 1.6)
    vt = random.uniform(-0.3, 0.3)

    base_len = random.uniform(14, 24)
    base_wid = random.uniform(6, 10)

    color = random.choice([
        (240, 230, 210),
        (210, 220, 255),
        (255, 245, 200)
    ])

    tidal_bodies.append({
        "r": spawn_r,
        "angle": angle,
        "vr": vr,
        "vt": vt,
        "base_length": base_len,
        "base_width": base_wid,
        "color": color,
        "shredded": False
    })


def shred_tidal_body(body):
    n_frag = random.randint(4, 7)

    for _ in range(n_frag):
        r = body["r"] + random.uniform(-10, 10)
        angle = body["angle"] + random.uniform(-0.25, 0.25)
        vr = body["vr"] * random.uniform(0.9, 1.3)
        vt = body["vt"] + random.uniform(-0.3, 0.3)
        base_len = body["base_length"] * random.uniform(0.5, 0.9)
        base_wid = body["base_width"] * random.uniform(0.4, 0.8)
        max_age = random.randint(240, 420)

        tidal_fragments.append({
            "r": r,
            "angle": angle,
            "vr": vr,
            "vt": vt,
            "base_length": base_len,
            "base_width": base_wid,
            "color": body["color"],
            "age": 0,
            "max_age": max_age
        })

    body["shredded"] = True


def update_tidal_bodies():
    global next_tidal_spawn

    if next_tidal_spawn <= 0 and len(tidal_bodies) < 3:
        spawn_tidal_body()
        next_tidal_spawn = random.randint(240, 540)
    else:
        next_tidal_spawn -= 1

    remove = []
    tidal_radius = 260

    for i, body in enumerate(tidal_bodies):
        r = body["r"]

        gravity = 0.0006 * (rs_pixels ** 2 / (r ** 2 + 1))
        body["vr"] -= gravity * (r / 400)

        body["r"] += body["vr"]
        body["angle"] += body["vt"] / max(40, body["r"])

        if r < tidal_radius and not body["shredded"]:
            shred_tidal_body(body)
            remove.append(i)
            continue

        if body["r"] <= event_horizon_radius * 0.95 or body["r"] > 700:
            remove.append(i)

    for i in reversed(remove):
        tidal_bodies.pop(i)


def update_tidal_fragments():
    remove = []

    for i, fr in enumerate(tidal_fragments):
        r = fr["r"]

        gravity = 0.0006 * (rs_pixels ** 2 / (r ** 2 + 1))
        fr["vr"] -= gravity * (r / 400)

        fr["r"] += fr["vr"]
        fr["angle"] += fr["vt"] / max(40, fr["r"])

        fr["age"] += 1

        if fr["r"] <= event_horizon_radius * 0.95 or fr["r"] > 700 or fr["age"] >= fr["max_age"]:
            remove.append(i)

    for i in reversed(remove):
        tidal_fragments.pop(i)


def apply_gravitational_redshift(color, r):
    if r <= 0:
        return color
    grav = (2 * event_horizon_radius - r) / (event_horizon_radius)
    grav = max(0.0, min(1.0, grav))

    overall = 1.0 - 0.4 * grav
    r_gain = 1.0
    g_gain = max(0.0, 1.0 - 0.8 * grav)
    b_gain = max(0.0, 1.0 - 1.2 * grav)

    r_c = min(255, int(color[0] * overall * r_gain))
    g_c = min(255, int(color[1] * overall * g_gain))
    b_c = min(255, int(color[2] * overall * b_gain))

    return (r_c, g_c, b_c)


def draw_tidal_bodies():
    for body in tidal_bodies:
        r = body["r"]
        angle = body["angle"]

        angle_screen = angle
        if event_horizon_radius < r < 420:
            alpha = deflection_angle(r) * 0.6
            angle_screen = angle + alpha

        x = center[0] + math.cos(angle_screen) * r
        y = center[1] + math.sin(angle_screen) * r

        stretch = max(0.0, min(1.0, (350 - r) / 300.0))
        length_f = 1 + 3 * stretch
        width_f = 1 - 0.5 * stretch

        length = max(8, body["base_length"] * length_f)
        width = max(2, body["base_width"] * width_f)

        bright = 1.0 + 1.2 * stretch
        col = (
            min(255, int(body["color"][0] * bright)),
            min(255, int(body["color"][1] * bright)),
            min(255, int(body["color"][2] * bright)),
        )

        col = apply_gravitational_redshift(col, r)

        surf = pygame.Surface((int(length), int(width)), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, col, (0, 0, int(length), int(width)))

        dx = center[0] - x
        dy = center[1] - y
        ang_deg = math.degrees(math.atan2(dy, dx))

        rot = pygame.transform.rotate(surf, ang_deg)
        rect = rot.get_rect(center=(int(x), int(y)))
        screen.blit(rot, rect)


def draw_tidal_fragments():
    for fr in tidal_fragments:
        r = fr["r"]
        angle = fr["angle"]

        angle_screen = angle
        if event_horizon_radius < r < 420:
            alpha = deflection_angle(r) * 0.6
            angle_screen = angle + alpha

        x = center[0] + math.cos(angle_screen) * r
        y = center[1] + math.sin(angle_screen) * r

        stretch = max(0.0, min(1.0, (350 - r) / 300.0))
        length_f = 1 + 2.5 * stretch
        width_f = 1 - 0.6 * stretch

        length = max(6, fr["base_length"] * length_f)
        width = max(2, fr["base_width"] * width_f)

        age_fade = max(0.2, 1.0 - fr["age"] / fr["max_age"])

        base_col = fr["color"]
        col = (
            min(255, int(base_col[0] * age_fade)),
            min(255, int(base_col[1] * age_fade)),
            min(255, int(base_col[2] * age_fade)),
        )

        col = apply_gravitational_redshift(col, r)

        surf = pygame.Surface((int(length), int(width)), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, col, (0, 0, int(length), int(width)))

        dx = center[0] - x
        dy = center[1] - y
        ang_deg = math.degrees(math.atan2(dy, dx))

        rot = pygame.transform.rotate(surf, ang_deg)
        rect = rot.get_rect(center=(int(x), int(y)))
        screen.blit(rot, rect)


def draw_labels():
    labels = [
        ("Event Horizon (r=2GM/c²)", (120, -20), event_horizon_radius),
        ("Photon Sphere (r=3GM/c²)", (140, 50), photon_sphere_radius),
        ("ISCO", (100, 80), isco_radius),
    ]

    for text, offset, rad in labels:
        pos = (center[0] + offset[0], center[1] + offset[1])
        end = (center[0] + rad, center[1])

        s = small_font.render(text, True, (255, 255, 200))
        screen.blit(s, pos)
        pygame.draw.line(screen, (255, 255, 200), pos, end, 1)
        pygame.draw.circle(screen, (255, 255, 200), end, 3)


def draw_help():
    surf = pygame.Surface((300, 220), pygame.SRCALPHA)
    pygame.draw.rect(surf, (0, 0, 0, 200), (0, 0, 300, 220))
    pygame.draw.rect(surf, (100, 100, 150), (0, 0, 300, 220), 2)

    lines = [
        "CONTROLS", "",
        "L - Toggle Labels",
        "H - Toggle Help",
        "ESC - Exit", "",
        "Arrow Keys - Move Camera", "",
        "Watch for:",
        "- Doppler Beaming",
        "- Light Bending",
        "- Spaghettification"
    ]

    y = 10
    for line in lines:
        if line == "CONTROLS":
            text_surf = font.render(line, True, (255, 255, 120))
        else:
            text_surf = small_font.render(line, True, (200, 200, 200))
        surf.blit(text_surf, (10, y))
        y += 20

    screen.blit(surf, (10, 10))


running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_l:
                show_labels = not show_labels
            elif e.key == pygame.K_h:
                show_help = not show_help
            elif e.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif e.key == pygame.K_LEFT:
                center = (center[0] - 15, center[1])
            elif e.key == pygame.K_RIGHT:
                center = (center[0] + 15, center[1])
            elif e.key == pygame.K_UP:
                center = (center[0], center[1] - 15)
            elif e.key == pygame.K_DOWN:
                center = (center[0], center[1] + 15)

    screen.fill(black)

    draw_lensed_background()

    update_tidal_bodies()
    update_tidal_fragments()
    draw_tidal_fragments()
    draw_tidal_bodies()

    draw_relativistic_jets()
    draw_accretion_disk_doppler()
    draw_blackhole_core()
    draw_particles()

    if show_labels:
        draw_labels()
    if show_help:
        draw_help()

    pygame.display.flip()
    clock.tick(60)
    time += 1
