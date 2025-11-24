import pygame
import sys
import random
import os

pygame.init()

# Tamaño de la ventana
WIDTH, HEIGHT = 1000, 800  # Aumentado para la intersección
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador de tráfico")
  
clock = pygame.time.Clock()
FPS = 60  # cuadros por segundo

# Colores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 100, 255)
GRAY = (100, 180, 100)  # Verde césped
DARK_GRAY = (60, 60, 60)  # Carretera

# Calcular centro para la intersección
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2
ROAD_WIDTH = 270  # Ancho de cada carretera

# Definir carriles para cada dirección (centrados)
# Carril horizontal (Este-Oeste)
LANES_EAST = [CENTER_Y - 135 + 10, CENTER_Y - 135 + 45, CENTER_Y - 135 + 80, CENTER_Y - 135 + 115]   # Carriles hacia el Este
LANES_WEST = [CENTER_Y + 15, CENTER_Y + 50, CENTER_Y + 85, CENTER_Y + 120]   # Carriles hacia el Oeste

# Carril vertical (Norte-Sur)
LANES_SOUTH = [CENTER_X - 135 + 10, CENTER_X - 135 + 45, CENTER_X - 135 + 80, CENTER_X - 135 + 115]  # Carriles hacia el Sur
LANES_NORTH = [CENTER_X + 15, CENTER_X + 50, CENTER_X + 85, CENTER_X + 120]  # Carriles hacia el Norte

# Cargar imágenes de coches
car_images = []
recursos_path = os.path.join(os.path.dirname(__file__), 'recursos')

# Intentar cargar imágenes, si no existen usar rectángulos de colores
try:
    for i in range(1, 5):  # carro1.png a carro4.png
        img_path = os.path.join(recursos_path, f'carro{i}.png')
        if os.path.exists(img_path):
            img = pygame.image.load(img_path)
            img = pygame.transform.scale(img, (50, 30))  # redimensionar
            car_images.append(img)
    
    if not car_images:
        print("No se encontraron imágenes, usando colores por defecto")
        car_images = None
except:
    print("Error al cargar imágenes, usando colores por defecto")
    car_images = None

# Cargar imágenes del tránsito
transito_images = {}
try:
    transito_images['default'] = pygame.image.load(os.path.join(recursos_path, 'transito.png'))
    transito_images['south'] = pygame.image.load(os.path.join(recursos_path, 'transitoSur.png'))
    transito_images['north'] = pygame.image.load(os.path.join(recursos_path, 'transitoNorte.png'))
    transito_images['west'] = pygame.image.load(os.path.join(recursos_path, 'transitoOeste.png'))
    transito_images['east'] = pygame.image.load(os.path.join(recursos_path, 'transitoEste.png'))
    
    # Redimensionar imágenes del tránsito
    for key in transito_images:
        transito_images[key] = pygame.transform.scale(transito_images[key], (80, 80))
    
    print("Imágenes del tránsito cargadas correctamente")
except Exception as e:
    print(f"Error al cargar imágenes del tránsito: {e}")
    transito_images = None
# Clase Coche
class Car:
    def __init__(self, x, y, speed, direction):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 30
        self.speed = speed  # píxeles por segundo
        self.direction = direction  # "EAST", "WEST", "NORTH", "SOUTH"
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.stopped = False
        
        # Asignar imagen aleatoria si están disponibles
        if car_images:
            self.image = random.choice(car_images)
            # Rotar imagen según dirección
            if self.direction == "WEST":
                self.image = pygame.transform.flip(self.image, True, False)
            elif self.direction == "NORTH":
                self.image = pygame.transform.rotate(self.image, 90)
            elif self.direction == "SOUTH":
                self.image = pygame.transform.rotate(self.image, -90)
        else:
            self.image = None
    
    def update(self, dt, traffic_lights, cars):
        if not self.stopped:
            if self.direction == "EAST":
                self.x += self.speed * dt
            elif self.direction == "WEST":
                self.x -= self.speed * dt
            elif self.direction == "SOUTH":
                self.y += self.speed * dt
            elif self.direction == "NORTH":
                self.y -= self.speed * dt
        
        # Si el coche sale de la pantalla, reiniciar posición
        if self.direction == "EAST" and self.x > WIDTH:
            self.x = -self.width - random.randint(50, 200)
            self.reset_appearance()
        elif self.direction == "WEST" and self.x < -self.width:
            self.x = WIDTH + random.randint(50, 200)
            self.reset_appearance()
        elif self.direction == "SOUTH" and self.y > HEIGHT:
            self.y = -self.height - random.randint(50, 200)
            self.reset_appearance()
        elif self.direction == "NORTH" and self.y < -self.height:
            self.y = HEIGHT + random.randint(50, 200)
            self.reset_appearance()
        
        # Verificar semáforo
        self.check_traffic_light(traffic_lights)
        
        # Verificar colisión con otros coches
        self.check_collision(cars)
    
    def reset_appearance(self):
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        if car_images:
            self.image = random.choice(car_images)
            if self.direction == "WEST":
                self.image = pygame.transform.flip(self.image, True, False)
            elif self.direction == "NORTH":
                self.image = pygame.transform.rotate(self.image, 90)
            elif self.direction == "SOUTH":
                self.image = pygame.transform.rotate(self.image, -90)
    
    def check_traffic_light(self, traffic_lights):
        # Seleccionar semáforo según dirección
        traffic_light = None
        distance_to_light = 0
        
        if self.direction == "EAST":
            traffic_light = traffic_lights[0]  # Semáforo Este
            distance_to_light = traffic_light.x - (self.x + self.width)
        elif self.direction == "WEST":
            traffic_light = traffic_lights[1]  # Semáforo Oeste
            distance_to_light = self.x - traffic_light.x
        elif self.direction == "SOUTH":
            traffic_light = traffic_lights[2]  # Semáforo Sur
            distance_to_light = traffic_light.y - (self.y + self.height)
        elif self.direction == "NORTH":
            traffic_light = traffic_lights[3]  # Semáforo Norte
            distance_to_light = self.y - traffic_light.y
        
        if traffic_light:
            if traffic_light.state in ["RED", "YELLOW"]:
                if -10 < distance_to_light < 150:
                    self.stopped = True
                    return
            
            if traffic_light.state == "GREEN":
                self.stopped = False
    
    def check_collision(self, cars):
        # Verificar si hay un coche delante muy cerca en la misma dirección
        for other_car in cars:
            if other_car != self and other_car.direction == self.direction:
                if self.direction in ["EAST", "WEST"]:
                    if abs(self.y - other_car.y) < 10:  # mismo carril
                        if self.direction == "EAST":
                            distance = other_car.x - (self.x + self.width)
                        else:
                            distance = self.x - (other_car.x + other_car.width)
                        
                        if 0 < distance < 60:
                            self.stopped = True
                            return
                else:  # NORTH o SOUTH
                    if abs(self.x - other_car.x) < 10:  # mismo carril
                        if self.direction == "SOUTH":
                            distance = other_car.y - (self.y + self.height)
                        else:
                            distance = self.y - (other_car.y + other_car.height)
                        
                        if 0 < distance < 60:
                            self.stopped = True
                            return

    def draw(self, screen):
        if self.image:
            # Dibujar imagen
            screen.blit(self.image, (self.x, self.y))
        else:
            # Dibujar rectángulo con color
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            # Ventanas
            pygame.draw.rect(screen, BLUE, (self.x + 5, self.y + 5, 15, 10))
            pygame.draw.rect(screen, BLUE, (self.x + 30, self.y + 5, 15, 10))

# Clase Semáforo
class TrafficLight:
    def __init__(self, x, y, orientation="vertical"):
        self.x = x
        self.y = y
        self.orientation = orientation  # "vertical" o "horizontal"
        self.state = "GREEN"  # GREEN, YELLOW, RED
        # Ya no necesitamos timer ni duraciones individuales
    
    def set_state(self, state):
        """Método para cambiar el estado desde el controlador"""
        self.state = state
    
    def draw(self, screen):
        if self.orientation == "vertical":
            # Poste del semáforo
            pygame.draw.rect(screen, DARK_GRAY, (self.x - 5, self.y, 10, 80))
            
            # Luces del semáforo
            color = RED if self.state == "RED" else (100, 0, 0)
            pygame.draw.circle(screen, color, (self.x, self.y + 15), 12)
            
            color = YELLOW if self.state == "YELLOW" else (100, 100, 0)
            pygame.draw.circle(screen, color, (self.x, self.y + 40), 12)
            
            color = GREEN if self.state == "GREEN" else (0, 100, 0)
            pygame.draw.circle(screen, color, (self.x, self.y + 65), 12)
        else:  # horizontal
            # Poste del semáforo
            pygame.draw.rect(screen, DARK_GRAY, (self.x, self.y - 5, 80, 10))
            
            # Luces del semáforo
            color = RED if self.state == "RED" else (100, 0, 0)
            pygame.draw.circle(screen, color, (self.x + 15, self.y), 12)
            
            color = YELLOW if self.state == "YELLOW" else (100, 100, 0)
            pygame.draw.circle(screen, color, (self.x + 40, self.y), 12)
            
            color = GREEN if self.state == "GREEN" else (0, 100, 0)
            pygame.draw.circle(screen, color, (self.x + 65, self.y), 12)

# Clase Tránsito (Policía de tráfico)
class TrafficOfficer:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.current_direction = "north"  # Empezar con norte (flecha arriba)
        self.width = 80
        self.height = 80
        
        if transito_images:
            self.image = transito_images['north']  # Imagen inicial
        else:
            self.image = None
    
    def set_direction(self, direction):
        """Cambiar la dirección del tránsito"""
        self.current_direction = direction
        if transito_images:
            self.image = transito_images[direction]
    
    def get_allowed_direction(self):
        """Retorna qué dirección de tráfico está permitida"""
        # El sprite indica hacia dónde pueden ir los carros
        direction_map = {
            'north': 'NORTH',  # Sprite norte = carros del SUR van hacia NORTE
            'south': 'SOUTH',  # Sprite sur = carros del NORTE van hacia SUR
            'east': 'EAST',    # Sprite este = carros del OESTE van hacia ESTE
            'west': 'WEST'     # Sprite oeste = carros del ESTE van hacia OESTE
        }
        return direction_map.get(self.current_direction, None)
    
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x - self.width // 2, self.y - self.height // 2))
        else:
            # Si no hay imagen, dibujar un círculo azul
            pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), 40)

# Clase para el contador inicial
class Countdown:
    def __init__(self):
        self.active = True
        self.counter = 3
        self.timer = 0
        self.font = pygame.font.Font(None, 120)
    
    def update(self, dt):
        if self.active:
            self.timer += dt
            if self.timer >= 1.0:
                self.counter -= 1
                self.timer = 0
                
                if self.counter < 0:
                    self.active = False
    
    def draw(self, screen):
        if self.active and self.counter > 0:
            # Fondo semi-transparente
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Dibujar número
            text = self.font.render(str(self.counter), True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)
        elif self.active and self.counter == 0:
            # Mostrar "¡GO!"
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            text = self.font.render("¡GO!", True, GREEN)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)

# Clase Controlador de Semáforos
class TrafficLightController:
    def __init__(self, lights_horizontal, lights_vertical, traffic_officer):
        """
        lights_horizontal: lista de semáforos Este y Oeste
        lights_vertical: lista de semáforos Norte y Sur
        traffic_officer: referencia al oficial de tránsito
        """
        self.lights_horizontal = lights_horizontal
        self.lights_vertical = lights_vertical
        self.traffic_officer = traffic_officer
        self.manual_mode = True  # Ahora está en modo manual (controlado por el oficial)
        
        # Inicializar todos en rojo excepto el permitido
        self.update_lights_from_officer()
    
    def update_lights_from_officer(self):
        """Actualizar semáforos basándose en la dirección del oficial"""
        allowed_direction = self.traffic_officer.get_allowed_direction()
        
        # Primero poner todos en rojo
        for light in self.lights_horizontal + self.lights_vertical:
            light.set_state("RED")
        
        # Luego poner en verde solo la dirección permitida
        if allowed_direction == "EAST":
            self.lights_horizontal[0].set_state("GREEN")  # traffic_light_east
        elif allowed_direction == "WEST":
            self.lights_horizontal[1].set_state("GREEN")  # traffic_light_west
        elif allowed_direction == "SOUTH":
            self.lights_vertical[0].set_state("GREEN")  # traffic_light_south
        elif allowed_direction == "NORTH":
            self.lights_vertical[1].set_state("GREEN")  # traffic_light_north
    
    def update(self, dt):
        """Actualizar los semáforos según el oficial de tránsito"""
        if self.manual_mode:
            self.update_lights_from_officer()


traffic_light_east = TrafficLight(CENTER_X - 80, CENTER_Y - 135, "vertical")
traffic_light_west = TrafficLight(CENTER_X + 80, CENTER_Y + 135 - 10, "vertical")
traffic_light_south = TrafficLight(CENTER_X - 205, CENTER_Y - 70, "horizontal")
traffic_light_north = TrafficLight(CENTER_X + 205 - 80, CENTER_Y + 65, "horizontal")

traffic_lights = [traffic_light_east, traffic_light_west, traffic_light_south, traffic_light_north]

# Crear oficial de tránsito PRIMERO (en el centro de la intersección)
traffic_officer = TrafficOfficer(CENTER_X, CENTER_Y)

# Crear controlador de semáforos DESPUÉS (ahora traffic_officer ya existe)
traffic_controller = TrafficLightController(
    lights_horizontal=[traffic_light_east, traffic_light_west],
    lights_vertical=[traffic_light_south, traffic_light_north],
    traffic_officer=traffic_officer
)

# Crear contador inicial
countdown = Countdown()

# Crear coches

cars = []
num_cars = 24  # 6 coches por dirección

for i in range(num_cars):
    direction_index = i % 4
    
    if direction_index == 0:  # EAST
        x = random.randint(-400, WIDTH - 100)
        y = random.choice(LANES_EAST)
        direction = "EAST"
    elif direction_index == 1:  # WEST
        x = random.randint(100, WIDTH + 400)
        y = random.choice(LANES_WEST)
        direction = "WEST"
    elif direction_index == 2:  # SOUTH
        x = random.choice(LANES_SOUTH)
        y = random.randint(-400, HEIGHT - 100)
        direction = "SOUTH"
    else:  # NORTH
        x = random.choice(LANES_NORTH)
        y = random.randint(100, HEIGHT + 400)
        direction = "NORTH"
    
    speed = random.randint(80, 150)
    cars.append(Car(x, y, speed, direction))

# Variables para spawn automático
spawn_timer = 0
spawn_interval = 1.5  # segundos entre spawns

running = True
while running:
    dt = clock.tick(FPS) / 1000

    # 1. Manejar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Controles del tránsito (solo cuando el conteo terminó)
        if event.type == pygame.KEYDOWN and not countdown.active:
            if event.key == pygame.K_UP:
                traffic_officer.set_direction('south')  # Flecha arriba = sprite sur = carros norte pasan
            elif event.key == pygame.K_DOWN:
                traffic_officer.set_direction('north')  # Flecha abajo = sprite norte = carros sur pasan
            elif event.key == pygame.K_LEFT:
                traffic_officer.set_direction('west')   # Flecha izq = sprite oeste = carros este pasan
            elif event.key == pygame.K_RIGHT:
                traffic_officer.set_direction('east')   # Flecha der = sprite este = carros oeste pasan

    # 2. Actualizar lógica
    countdown.update(dt)
    
    # Solo actualizar el juego después del conteo
    if not countdown.active:
        traffic_controller.update(dt)
        
        for car in cars:
            car.update(dt, traffic_lights, cars)
        
        # Spawn automático de nuevos coches
        spawn_timer += dt
        if spawn_timer >= spawn_interval and len(cars) < 40:
            direction_choice = random.choice(["EAST", "WEST", "NORTH", "SOUTH"])
            
            if direction_choice == "EAST":
                lane = random.choice(LANES_EAST)
                new_car = Car(-60, lane, random.randint(80, 150), "EAST")
            elif direction_choice == "WEST":
                lane = random.choice(LANES_WEST)
                new_car = Car(WIDTH + 60, lane, random.randint(80, 150), "WEST")
            elif direction_choice == "SOUTH":
                lane = random.choice(LANES_SOUTH)
                new_car = Car(lane, -60, random.randint(80, 150), "SOUTH")
            else:  # NORTH
                lane = random.choice(LANES_NORTH)
                new_car = Car(lane, HEIGHT + 60, random.randint(80, 150), "NORTH")
            
            cars.append(new_car)
            spawn_timer = 0

    # 3. Dibujar
    screen.fill(GRAY)
    
    # Dibujar intersección en cruz (centrada)
    pygame.draw.rect(screen, DARK_GRAY, (0, CENTER_Y - 135, WIDTH, ROAD_WIDTH))
    pygame.draw.rect(screen, DARK_GRAY, (CENTER_X - 135, 0, ROAD_WIDTH, HEIGHT))
    
    # Líneas blancas horizontales - carriles Este
    for i in range(0, WIDTH, 40):
        pygame.draw.rect(screen, WHITE, (i, CENTER_Y - 95, 25, 2))
    for i in range(0, WIDTH, 40):
        pygame.draw.rect(screen, WHITE, (i, CENTER_Y - 60, 25, 2))
    for i in range(0, WIDTH, 40):
        pygame.draw.rect(screen, WHITE, (i, CENTER_Y - 25, 25, 2))
    
    pygame.draw.rect(screen, YELLOW, (0, CENTER_Y - 3, WIDTH, 3))
    pygame.draw.rect(screen, YELLOW, (0, CENTER_Y + 3, WIDTH, 3))
    
    for i in range(0, WIDTH, 40):
        pygame.draw.rect(screen, WHITE, (i, CENTER_Y + 45, 25, 2))
    for i in range(0, WIDTH, 40):
        pygame.draw.rect(screen, WHITE, (i, CENTER_Y + 80, 25, 2))
    for i in range(0, WIDTH, 40):
        pygame.draw.rect(screen, WHITE, (i, CENTER_Y + 115, 25, 2))
    
    for i in range(0, HEIGHT, 40):
        pygame.draw.rect(screen, WHITE, (CENTER_X - 95, i, 2, 25))
    for i in range(0, HEIGHT, 40):
        pygame.draw.rect(screen, WHITE, (CENTER_X - 60, i, 2, 25))
    for i in range(0, HEIGHT, 40):
        pygame.draw.rect(screen, WHITE, (CENTER_X - 25, i, 2, 25))
    
    pygame.draw.rect(screen, YELLOW, (CENTER_X - 3, 0, 3, HEIGHT))
    pygame.draw.rect(screen, YELLOW, (CENTER_X + 3, 0, 3, HEIGHT))
    
    for i in range(0, HEIGHT, 40):
        pygame.draw.rect(screen, WHITE, (CENTER_X + 45, i, 2, 25))
    for i in range(0, HEIGHT, 40):
        pygame.draw.rect(screen, WHITE, (CENTER_X + 80, i, 2, 25))
    for i in range(0, HEIGHT, 40):
        pygame.draw.rect(screen, WHITE, (CENTER_X + 115, i, 2, 25))
    
    # Paso de peatones
    for i in range(CENTER_X - 125, CENTER_X + 125, 15):
        pygame.draw.rect(screen, WHITE, (i, CENTER_Y - 140, 10, 30))
    for i in range(CENTER_X - 125, CENTER_X + 125, 15):
        pygame.draw.rect(screen, WHITE, (i, CENTER_Y + 130, 10, 30))
    for i in range(CENTER_Y - 125, CENTER_Y + 125, 15):
        pygame.draw.rect(screen, WHITE, (CENTER_X - 140, i, 30, 10))
    for i in range(CENTER_Y - 125, CENTER_Y + 125, 15):
        pygame.draw.rect(screen, WHITE, (CENTER_X + 130, i, 30, 10))
    
    # Dibujar semáforos
    for light in traffic_lights:
        light.draw(screen)
    
    # Dibujar coches
    for car in cars:
        car.draw(screen)
    
    # Dibujar oficial de tránsito
    traffic_officer.draw(screen)
    
    # Dibujar contador si está activo
    countdown.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()