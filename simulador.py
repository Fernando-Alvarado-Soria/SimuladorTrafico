import pygame
import sys
import random
import os

pygame.init()

# Tamaño de la ventana
WIDTH, HEIGHT = 800, 600  # Aumentado de 400 a 600
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
GRAY = (50, 50, 50)
DARK_GRAY = (30, 30, 30)

# Definir carriles
LANES_RIGHT = [235, 285, 335]  # Carriles hacia la derecha (ida) - ajustados
LANES_LEFT = [380, 430, 480]   # Carriles hacia la izquierda (vuelta) - ajustados

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

# Clase Coche
class Car:
    def __init__(self, x, y, speed, direction="RIGHT"):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 30
        self.speed = speed  # píxeles por segundo
        self.direction = direction  # "RIGHT" o "LEFT"
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.stopped = False
        
        # Asignar imagen aleatoria si están disponibles
        if car_images:
            self.image = random.choice(car_images)
            # Voltear imagen si va hacia la izquierda
            if self.direction == "LEFT":
                self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.image = None
    
    def update(self, dt, traffic_lights, cars):
        if not self.stopped:
            if self.direction == "RIGHT":
                self.x += self.speed * dt
            else:
                self.x -= self.speed * dt
        
        # Si el coche sale de la pantalla, reiniciar posición
        if self.direction == "RIGHT" and self.x > WIDTH:
            self.x = -self.width - random.randint(50, 200)
            self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            if car_images:
                self.image = random.choice(car_images)
        elif self.direction == "LEFT" and self.x < -self.width:
            self.x = WIDTH + random.randint(50, 200)
            self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            if car_images:
                self.image = random.choice(car_images)
                self.image = pygame.transform.flip(self.image, True, False)
        
        # Verificar semáforo
        self.check_traffic_light(traffic_lights)
        
        # Verificar colisión con otros coches
        self.check_collision(cars)
    
    def check_traffic_light(self, traffic_lights):
        # Seleccionar semáforo según dirección
        if self.direction == "RIGHT":
            traffic_light = traffic_lights[0]  # Semáforo derecho
            distance_to_light = traffic_light.x - (self.x + self.width)
            
            if traffic_light.state in ["RED", "YELLOW"]:
                if -10 < distance_to_light < 150:
                    self.stopped = True
                    return
            
            if traffic_light.state == "GREEN":
                self.stopped = False
        else:  # LEFT
            traffic_light = traffic_lights[1]  # Semáforo izquierdo
            distance_to_light = self.x - traffic_light.x
            
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
                if abs(self.y - other_car.y) < 10:  # mismo carril
                    if self.direction == "RIGHT":
                        distance = other_car.x - (self.x + self.width)
                    else:
                        distance = self.x - (other_car.x + other_car.width)
                    
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
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = "GREEN"  # GREEN, YELLOW, RED
        self.timer = 0
        self.green_duration = 5  # segundos
        self.yellow_duration = 2
        self.red_duration = 5
    
    def update(self, dt):
        self.timer += dt
        
        if self.state == "GREEN" and self.timer >= self.green_duration:
            self.state = "YELLOW"
            self.timer = 0
        elif self.state == "YELLOW" and self.timer >= self.yellow_duration:
            self.state = "RED"
            self.timer = 0
        elif self.state == "RED" and self.timer >= self.red_duration:
            self.state = "GREEN"
            self.timer = 0
    
    def draw(self, screen):
        # Poste del semáforo
        pygame.draw.rect(screen, DARK_GRAY, (self.x - 5, self.y, 10, 80))
        
        # Luces del semáforo
        # Roja
        color = RED if self.state == "RED" else (100, 0, 0)
        pygame.draw.circle(screen, color, (self.x, self.y + 15), 12)
        
        # Amarilla
        color = YELLOW if self.state == "YELLOW" else (100, 100, 0)
        pygame.draw.circle(screen, color, (self.x, self.y + 40), 12)
        
        # Verde
        color = GREEN if self.state == "GREEN" else (0, 100, 0)
        pygame.draw.circle(screen, color, (self.x, self.y + 65), 12)

# Crear objetos - 2 semáforos
traffic_light_right = TrafficLight(600, 210)  # Semáforo para carriles derechos (arriba)
traffic_light_left = TrafficLight(200, 360)   # Semáforo para carriles izquierdos (abajo)
traffic_light_left.state = "RED"  # Empezar en rojo para variar
traffic_lights = [traffic_light_right, traffic_light_left]

# Crear más coches con posiciones y velocidades aleatorias
cars = []
num_cars = 20  # Número de coches en la simulación

for i in range(num_cars):
    # Mitad van a la derecha, mitad a la izquierda
    if i < num_cars // 2:
        x = random.randint(-400, WIDTH - 100)
        y = random.choice(LANES_RIGHT)
        direction = "RIGHT"
    else:
        x = random.randint(100, WIDTH + 400)
        y = random.choice(LANES_LEFT)
        direction = "LEFT"
    
    speed = random.randint(80, 150)
    cars.append(Car(x, y, speed, direction))

# Variables para spawn automático
spawn_timer = 0
spawn_interval = 1.5  # segundos entre spawns

running = True
while running:
    dt = clock.tick(FPS) / 1000  # segundos por cuadro (para tiempos)

    # 1. Manejar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Actualizar lógica
    for light in traffic_lights:
        light.update(dt)
    
    for car in cars:
        car.update(dt, traffic_lights, cars)
    
    # Spawn automático de nuevos coches
    spawn_timer += dt
    if spawn_timer >= spawn_interval and len(cars) < 30:  # máximo 30 coches
        # Spawn aleatorio en cualquier dirección
        if random.random() > 0.5:
            # Coche hacia la derecha
            lane = random.choice(LANES_RIGHT)
            new_car = Car(-60, lane, random.randint(80, 150), "RIGHT")
        else:
            # Coche hacia la izquierda
            lane = random.choice(LANES_LEFT)
            new_car = Car(WIDTH + 60, lane, random.randint(80, 150), "LEFT")
        
        cars.append(new_car)
        spawn_timer = 0

    # 3. Dibujar
    screen.fill(GRAY)  # fondo gris
    
    # Dibujar carretera completa (ida y vuelta) - centrada verticalmente
    pygame.draw.rect(screen, DARK_GRAY, (0, 220, WIDTH, 280))
    
    # Líneas divisorias de carriles - IDA (derecha)
    pygame.draw.rect(screen, WHITE, (0, 220, WIDTH, 2))
    for i in range(0, WIDTH, 40):
        pygame.draw.rect(screen, WHITE, (i, 268, 25, 2))
    for i in range(0, WIDTH, 40):
        pygame.draw.rect(screen, WHITE, (i, 318, 25, 2))
    
    # Línea central doble (separación de sentidos)
    pygame.draw.rect(screen, YELLOW, (0, 358, WIDTH, 3))
    pygame.draw.rect(screen, YELLOW, (0, 363, WIDTH, 3))
    
    # Líneas divisorias de carriles - VUELTA (izquierda)
    for i in range(0, WIDTH, 40):
        pygame.draw.rect(screen, WHITE, (i, 413, 25, 2))
    for i in range(0, WIDTH, 40):
        pygame.draw.rect(screen, WHITE, (i, 463, 25, 2))
    pygame.draw.rect(screen, WHITE, (0, 498, WIDTH, 2))
    
    # Dibujar semáforos
    for light in traffic_lights:
        light.draw(screen)
    
    # Dibujar coches
    for car in cars:
        car.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()