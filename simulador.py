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
BLACK = (0, 0, 0)  # Negro para texto

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
    
    def get_rect(self):
        """Retorna el rectángulo de colisión del coche"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_in_intersection(self):
        """Verifica si el coche está dentro de la zona de intersección"""
        in_horizontal_zone = CENTER_Y - 135 < self.y < CENTER_Y + 135
        in_vertical_zone = CENTER_X - 135 < self.x < CENTER_X + 135
        return in_horizontal_zone and in_vertical_zone
    
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
        self.decision_timer = 0  # Temporizador para decisión automática
        self.decision_interval = 10.0  # 10 segundos sin decisión
        
        if transito_images:
            self.image = transito_images['north']  # Imagen inicial
        else:
            self.image = None
    
    def set_direction(self, direction):
        """Cambiar la dirección del tránsito"""
        self.current_direction = direction
        if transito_images:
            self.image = transito_images[direction]
        # Reiniciar el temporizador cuando el jugador toma una decisión
        self.decision_timer = 0
    
    def update(self, dt):
        """Actualizar el temporizador de decisión automática"""
        self.decision_timer += dt
        
        # Si pasan 10 segundos sin decisión, cambiar automáticamente
        if self.decision_timer >= self.decision_interval:
            self.auto_change_direction()
            self.decision_timer = 0
    
    def auto_change_direction(self):
        """Cambiar automáticamente a una dirección aleatoria"""
        directions = ['north', 'south', 'east', 'west']
        # Elegir una dirección diferente a la actual
        available_directions = [d for d in directions if d != self.current_direction]
        new_direction = random.choice(available_directions)
        
        self.current_direction = new_direction
        if transito_images:
            self.image = transito_images[new_direction]
        
        print(f"⚠️ Decisión automática: Cambiando a {new_direction.upper()}")
    
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

# Clase para el Game Over
class GameOver:
    def __init__(self):
        self.active = False
        self.font_big = pygame.font.Font(None, 100)
        self.font_small = pygame.font.Font(None, 40)
        self.timer = 0
        self.collision_pos = None
    
    def activate(self, pos_x, pos_y):
        """Activar Game Over en la posición de la colisión"""
        self.active = True
        self.timer = 0
        self.collision_pos = (pos_x, pos_y)
    
    def update(self, dt):
        if self.active:
            self.timer += dt
    
    def draw(self, screen):
        if self.active:
            # Fondo semi-transparente
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Pantalla de Game Over final
            text = self.font_big.render("GAME OVER", True, RED)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
            screen.blit(text, text_rect)
            
            text2 = self.font_small.render("¡Sin vidas restantes!", True, WHITE)
            text2_rect = text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
            screen.blit(text2, text2_rect)
            
            text3 = self.font_small.render("Presiona ESPACIO para jugar de nuevo", True, GREEN)
            text3_rect = text3.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
            screen.blit(text3, text3_rect)
            
            # Efecto visual en el punto de colisión
            if self.collision_pos and self.timer < 1.5:
                radius = int(30 + self.timer * 40)
                alpha = int(255 - (self.timer / 1.5) * 255)
                explosion_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(explosion_surf, (255, 0, 0, alpha), (radius, radius), radius)
                screen.blit(explosion_surf, (self.collision_pos[0] - radius, self.collision_pos[1] - radius))

# Clase para notificación de colisión temporal
class CollisionNotification:
    def __init__(self):
        self.active = False
        self.timer = 0
        self.duration = 2.0  # Duración de la notificación en segundos
        self.font_big = pygame.font.Font(None, 80)
        self.font_small = pygame.font.Font(None, 40)
        self.collision_pos = None
        self.lives_lost = 0
    
    def activate(self, pos_x, pos_y, lives_remaining):
        """Activar notificación de colisión"""
        self.active = True
        self.timer = 0
        self.collision_pos = (pos_x, pos_y)
        self.lives_lost = lives_remaining
    
    def update(self, dt):
        if self.active:
            self.timer += dt
            if self.timer >= self.duration:
                self.active = False
    
    def draw(self, screen):
        if self.active:
            # Efecto visual en el punto de colisión
            if self.timer < 1.5:
                radius = int(30 + self.timer * 40)
                alpha = int(255 - (self.timer / 1.5) * 255)
                explosion_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(explosion_surf, (255, 0, 0, alpha), (radius, radius), radius)
                if self.collision_pos:
                    screen.blit(explosion_surf, (self.collision_pos[0] - radius, self.collision_pos[1] - radius))
            
            # Mensaje flotante de colisión
            if self.timer < 1.5:
                y_offset = int(self.timer * 30)  # Movimiento hacia arriba
                alpha = int(255 - (self.timer / 1.5) * 200)
                
                # Crear superficie para el texto con transparencia
                text_surface = pygame.Surface((400, 150), pygame.SRCALPHA)
                
                # Texto "¡COLISIÓN!"
                text = self.font_big.render("¡COLISIÓN!", True, (255, 0, 0, alpha))
                text_rect = text.get_rect(center=(200, 50))
                text_surface.blit(text, text_rect)
                
                # Texto de vidas restantes
                lives_text = self.font_small.render(f"Vidas: {self.lives_lost}", True, (255, 255, 255, alpha))
                lives_rect = lives_text.get_rect(center=(200, 100))
                text_surface.blit(lives_text, lives_rect)
                
                # Dibujar en la pantalla
                if self.collision_pos:
                    screen.blit(text_surface, (self.collision_pos[0] - 200, self.collision_pos[1] - 75 - y_offset))

# Clase para mostrar las vidas
class LivesDisplay:
    def __init__(self):
        self.font = pygame.font.Font(None, 50)
        self.font_small = pygame.font.Font(None, 35)
        self.heart = "❤"
    
    def draw(self, screen, lives, decision_timer, decision_interval):
        """Dibuja las vidas y el temporizador de decisión en la esquina superior izquierda"""
        # Fondo semi-transparente para mejor visibilidad
        background = pygame.Surface((200, 100))
        background.set_alpha(150)
        background.fill(BLACK)
        screen.blit(background, (10, 10))
        
        # Texto "Vidas:"
        text = self.font.render("Vidas:", True, WHITE)
        screen.blit(text, (20, 20))
        
        # Dibujar corazones
        for i in range(lives):
            heart_text = self.font.render(self.heart, True, RED)
            screen.blit(heart_text, (120 + i * 30, 20))
        
        # Temporizador de decisión
        time_remaining = decision_interval - decision_timer
        timer_text = self.font_small.render(f"Decisión: {int(time_remaining)}s", True, YELLOW if time_remaining <= 3 else WHITE)
        screen.blit(timer_text, (20, 65))

# Función para detectar colisiones entre carriles
def check_cross_lane_collisions(cars):
    """Detecta colisiones entre vehículos de diferentes direcciones en la intersección"""
    for i, car1 in enumerate(cars):
        if not car1.is_in_intersection():
            continue
            
        for car2 in cars[i+1:]:
            if not car2.is_in_intersection():
                continue
            
            # Solo verificar colisión si van en direcciones perpendiculares
            if (car1.direction in ["EAST", "WEST"] and car2.direction in ["NORTH", "SOUTH"]) or \
               (car1.direction in ["NORTH", "SOUTH"] and car2.direction in ["EAST", "WEST"]):
                
                # Verificar colisión de rectángulos
                rect1 = car1.get_rect()
                rect2 = car2.get_rect()
                
                if rect1.colliderect(rect2):
                    # Calcular punto medio de la colisión
                    collision_x = (car1.x + car2.x) // 2 + 25
                    collision_y = (car1.y + car2.y) // 2 + 15
                    return True, collision_x, collision_y, car1, car2
    
    return False, 0, 0, None, None

# Función para reiniciar posición de un vehículo
def reset_car_position(car):
    """Reinicia la posición de un vehículo a su punto de origen según su dirección"""
    if car.direction == "EAST":
        car.x = random.randint(-200, -60)
        car.y = random.choice(LANES_EAST)
    elif car.direction == "WEST":
        car.x = random.randint(WIDTH + 60, WIDTH + 200)
        car.y = random.choice(LANES_WEST)
    elif car.direction == "SOUTH":
        car.x = random.choice(LANES_SOUTH)
        car.y = random.randint(-200, -60)
    else:  # NORTH
        car.x = random.choice(LANES_NORTH)
        car.y = random.randint(HEIGHT + 60, HEIGHT + 200)
    
    car.stopped = False
    car.reset_appearance()

# Función para reiniciar el juego
def reset_game():
    """Reinicia todos los elementos del juego"""
    global cars, spawn_timer, countdown, game_over, lives, difficulty_timer, current_max_cars, min_speed, max_speed
    
    # Reiniciar posiciones de todos los coches existentes
    cars.clear()
    
    # Crear 10 coches iniciales (antes 8)
    num_cars = 10
    for i in range(num_cars):
        direction_index = i % 4
        
        if direction_index == 0:  # EAST
            x = random.randint(-400, -60)
            y = random.choice(LANES_EAST)
            direction = "EAST"
        elif direction_index == 1:  # WEST
            x = random.randint(WIDTH + 60, WIDTH + 400)
            y = random.choice(LANES_WEST)
            direction = "WEST"
        elif direction_index == 2:  # SOUTH
            x = random.choice(LANES_SOUTH)
            y = random.randint(-400, -60)
            direction = "SOUTH"
        else:  # NORTH
            x = random.choice(LANES_NORTH)
            y = random.randint(HEIGHT + 60, HEIGHT + 400)
            direction = "NORTH"
        
        speed = random.randint(90, 160)  # Usar las nuevas velocidades iniciales
        cars.append(Car(x, y, speed, direction))
    
    # Reiniciar timers y dificultad
    spawn_timer = 0
    difficulty_timer = 0
    current_max_cars = 15
    min_speed = 90
    max_speed = 160
    
    # Reiniciar contador (solo si es game over completo)
    if lives <= 0:
        countdown = Countdown()
        lives = 3
    
    # Reiniciar game over
    game_over = GameOver()
    
    # Reiniciar oficial de tránsito
    traffic_officer.set_direction('north')
    traffic_officer.decision_timer = 0

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

# Crear Game Over
game_over = GameOver()

# Crear notificación de colisión
collision_notification = CollisionNotification()

# Crear display de vidas
lives_display = LivesDisplay()

# Sistema de vidas
lives = 3

# Sistema de dificultad progresiva
difficulty_timer = 0
difficulty_interval = 20.0  # Aumentar dificultad cada 20 segundos (antes 30)
current_max_cars = 15  # Empezar con 15 carros máximo
max_cars_limit = 60  # Límite absoluto de carros (antes 50)
cars_increment = 30  # Cuántos carros agregar cada vez (antes 5)
min_speed = 150  # Velocidad mínima inicial (antes 80)
max_speed = 360  # Velocidad máxima inicial (antes 150)
speed_increment = 20  # Cuánto aumentar la velocidad cada 20 segundos (antes 15)
max_speed_limit = 300  # Límite máximo de velocidad (antes 250)

# Crear coches

cars = []
num_cars = 10  # Empezar con 10 coches (antes 8)

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
    
    speed = random.randint(90, 160)  # Usar las nuevas velocidades iniciales
    cars.append(Car(x, y, speed, direction))

# Variables para spawn automático
spawn_timer = 0
spawn_interval = 1.2  # segundos entre spawns (antes 1.5, más rápido)

running = True
while running:
    dt = clock.tick(FPS) / 1000

    # 1. Manejar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Controles del tránsito (solo cuando el conteo terminó y no hay game over)
        if event.type == pygame.KEYDOWN and not countdown.active and not game_over.active:
            if event.key == pygame.K_UP:
                traffic_officer.set_direction('south')
            elif event.key == pygame.K_DOWN:
                traffic_officer.set_direction('north')
            elif event.key == pygame.K_LEFT:
                traffic_officer.set_direction('west')
            elif event.key == pygame.K_RIGHT:
                traffic_officer.set_direction('east')
        
        # Reiniciar juego después de Game Over (solo si perdiste todas las vidas)
        if event.type == pygame.KEYDOWN and game_over.active:
            if event.key == pygame.K_SPACE:
                reset_game()

    # 2. Actualizar lógica
    countdown.update(dt)
    game_over.update(dt)
    collision_notification.update(dt)
    
    # Solo actualizar el juego después del conteo y si no hay game over
    if not countdown.active and not game_over.active:
        traffic_controller.update(dt)
        
        # Actualizar temporizador de decisión del oficial
        traffic_officer.update(dt)
        
        # Actualizar dificultad cada 20 segundos
        difficulty_timer += dt
        if difficulty_timer >= difficulty_interval:
            difficulty_timer = 0
            
            # Aumentar cantidad máxima de carros
            if current_max_cars < max_cars_limit:
                current_max_cars += cars_increment
            
            # Aumentar velocidad de los carros
            if max_speed < max_speed_limit:
                min_speed += speed_increment
                max_speed += speed_increment
            
            print(f"¡Dificultad aumentada!")
            print(f"  - Máximo de carros: {current_max_cars}")
            print(f"  - Rango de velocidad: {min_speed}-{max_speed} px/s")
        
        for car in cars:
            car.update(dt, traffic_lights, cars)
        
        # Verificar colisiones entre carriles (solo si no hay notificación activa)
        if not collision_notification.active:
            collision_detected, col_x, col_y, car1, car2 = check_cross_lane_collisions(cars)
            if collision_detected:
                # Reiniciar posición de los vehículos colisionados inmediatamente
                reset_car_position(car1)
                reset_car_position(car2)
                
                # Perder una vida
                lives -= 1
                
                # Verificar si se acabaron las vidas
                if lives <= 0:
                    # Game Over completo
                    game_over.activate(col_x, col_y)
                else:
                    # Solo mostrar notificación de colisión
                    collision_notification.activate(col_x, col_y, lives)
        
        # Spawn automático de nuevos coches (usando velocidades actuales)
        spawn_timer += dt
        if spawn_timer >= spawn_interval and len(cars) < current_max_cars:
            direction_choice = random.choice(["EAST", "WEST", "NORTH", "SOUTH"])
            
            # Usar velocidades actuales según la dificultad
            car_speed = random.randint(min_speed, max_speed)
            
            if direction_choice == "EAST":
                lane = random.choice(LANES_EAST)
                new_car = Car(-60, lane, car_speed, "EAST")
            elif direction_choice == "WEST":
                lane = random.choice(LANES_WEST)
                new_car = Car(WIDTH + 60, lane, car_speed, "WEST")
            elif direction_choice == "SOUTH":
                lane = random.choice(LANES_SOUTH)
                new_car = Car(lane, -60, car_speed, "SOUTH")
            else:  # NORTH
                lane = random.choice(LANES_NORTH)
                new_car = Car(lane, HEIGHT + 60, car_speed, "NORTH")
            
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
    
    # Dibujar vidas y temporizador (si no hay countdown ni game over)
    if not countdown.active and not game_over.active:
        lives_display.draw(screen, lives, traffic_officer.decision_timer, traffic_officer.decision_interval)
    
    # Dibujar notificación de colisión
    collision_notification.draw(screen)
    
    # Dibujar contador si está activo
    countdown.draw(screen)
    
    # Dibujar Game Over si está activo
    game_over.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()