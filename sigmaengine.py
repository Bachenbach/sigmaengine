import pygame
import numpy as np
from typing import Tuple, List, Dict, Optional, Any
import math
import time

class SigmaEngine:
    def __init__(self, width: int = 800, height: int = 600, title: str = "SigmaEngine Game"):
        pygame.init()
        pygame.mixer.init()
        
        self.width = width
        self.height = height
        self.title = title
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        
        self.running = False
        self.clock = pygame.time.Clock()
        self.target_fps = 60
        self.delta_time = 0
        
        # Core systems
        self.input_manager = InputManager()
        self.resource_manager = ResourceManager()
        
        # Scene management
        self.current_scene = None
        self.scenes: Dict[str, Scene] = {}
        
    def run(self):
        self.running = True
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            self.delta_time = current_time - last_time
            last_time = current_time
            
            self._handle_events()
            self._update()
            self._render()
            
            self.clock.tick(self.target_fps)
            
    def _handle_events(self):
        self.input_manager.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.input_manager.handle_event(event)
            if self.current_scene:
                self.current_scene.handle_event(event)
                
    def _update(self):
        if self.current_scene:
            self.current_scene.update(self.delta_time)
            
    def _render(self):
        self.screen.fill((0, 0, 0))
        if self.current_scene:
            self.current_scene.render(self.screen)
        pygame.display.flip()
        
    def add_scene(self, name: str, scene: 'Scene'):
        self.scenes[name] = scene
        scene.engine = self
        
    def set_current_scene(self, name: str):
        if name in self.scenes:
            if self.current_scene:
                self.current_scene.on_exit()
            self.current_scene = self.scenes[name]
            self.current_scene.on_enter()

class ResourceManager:
    def __init__(self):
        self.textures: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        
    def load_texture(self, name: str, path: str) -> pygame.Surface:
        texture = pygame.image.load(path).convert_alpha()
        self.textures[name] = texture
        return texture
        
    def load_sound(self, name: str, path: str) -> pygame.mixer.Sound:
        sound = pygame.mixer.Sound(path)
        self.sounds[name] = sound
        return sound
        
    def load_font(self, name: str, path: str, size: int) -> pygame.font.Font:
        font = pygame.font.Font(path, size)
        self.fonts[name] = font
        return font

class InputManager:
    def __init__(self):
        self.keys_pressed = set()
        self.keys_down = set()
        self.keys_up = set()
        self.mouse_position = (0, 0)
        self.mouse_buttons_pressed = set()
        self.mouse_buttons_down = set()
        self.mouse_buttons_up = set()
        
    def update(self):
        self.keys_down.clear()
        self.keys_up.clear()
        self.mouse_buttons_down.clear()
        self.mouse_buttons_up.clear()
        self.mouse_position = pygame.mouse.get_pos()
        
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
            self.keys_down.add(event.key)
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
            self.keys_up.add(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_buttons_pressed.add(event.button)
            self.mouse_buttons_down.add(event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_buttons_pressed.discard(event.button)
            self.mouse_buttons_up.add(event.button)
            
    def is_key_pressed(self, key: int) -> bool:
        return key in self.keys_pressed
        
    def is_key_down(self, key: int) -> bool:
        return key in self.keys_down
        
    def is_key_up(self, key: int) -> bool:
        return key in self.keys_up

class Scene:
    def __init__(self):
        self.engine = None
        self.entities: List[Entity] = []
        
    def add_entity(self, entity: 'Entity'):
        self.entities.append(entity)
        entity.scene = self
        
    def remove_entity(self, entity: 'Entity'):
        if entity in self.entities:
            self.entities.remove(entity)
            
    def handle_event(self, event: pygame.event.Event):
        for entity in self.entities:
            entity.handle_event(event)
            
    def update(self, delta_time: float):
        for entity in self.entities:
            entity.update(delta_time)
            
    def render(self, screen: pygame.Surface):
        for entity in self.entities:
            entity.render(screen)
            
    def on_enter(self):
        pass
        
    def on_exit(self):
        pass

class Entity:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y
        self.scene = None
        self.width = 0
        self.height = 0
        self.rotation = 0
        self.scale = 1.0
        self.visible = True
        
    def handle_event(self, event: pygame.event.Event):
        pass
        
    def update(self, delta_time: float):
        pass
        
    def render(self, screen: pygame.Surface):
        pass
        
    @property
    def position(self) -> Tuple[float, float]:
        return (self.x, self.y)
        
    @position.setter
    def position(self, value: Tuple[float, float]):
        self.x, self.y = value

class Sprite(Entity):
    def __init__(self, x: float = 0, y: float = 0, texture_name: str = ""):
        super().__init__(x, y)
        self.texture_name = texture_name
        self.texture: Optional[pygame.Surface] = None
        self.src_rect: Optional[pygame.Rect] = None
        self.flip_x = False
        self.flip_y = False
        self.color_mod = (255, 255, 255)
        self.alpha = 255
        
    def load_texture(self):
        if self.scene and self.texture_name:
            self.texture = self.scene.engine.resource_manager.textures.get(self.texture_name)
            if self.texture:
                self.width = self.texture.get_width()
                self.height = self.texture.get_height()
                
    def render(self, screen: pygame.Surface):
        if not self.visible or not self.texture:
            return
            
        texture = self.texture
        if self.src_rect:
            texture = texture.subsurface(self.src_rect)
            
        if self.scale != 1.0 or self.rotation != 0:
            scaled_width = int(texture.get_width() * self.scale)
            scaled_height = int(texture.get_height() * self.scale)
            texture = pygame.transform.scale(texture, (scaled_width, scaled_height))
            
            if self.rotation != 0:
                texture = pygame.transform.rotate(texture, self.rotation)
                
        if self.flip_x or self.flip_y:
            texture = pygame.transform.flip(texture, self.flip_x, self.flip_y)
            
        texture.fill(self.color_mod, special_flags=pygame.BLEND_RGBA_MULT)
        texture.set_alpha(self.alpha)
        
        dest_rect = texture.get_rect()
        dest_rect.center = (int(self.x), int(self.y))
        
        screen.blit(texture, dest_rect)

# Add these classes to sigmaengine.py

class Animation:
    def __init__(self, sprite_sheet: str, frame_width: int, frame_height: int, 
                 frame_count: int, frame_duration: float):
        self.sprite_sheet = sprite_sheet
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame_count = frame_count
        self.frame_duration = frame_duration
        self.frames: List[pygame.Rect] = []
        self.current_frame = 0
        self.time_accumulated = 0
        self.is_playing = False
        self.is_looping = True
        
        # Calculate frame rectangles
        sheet_width = pygame.image.load(sprite_sheet).get_width()
        frames_per_row = sheet_width // frame_width
        
        for i in range(frame_count):
            x = (i % frames_per_row) * frame_width
            y = (i // frames_per_row) * frame_height
            self.frames.append(pygame.Rect(x, y, frame_width, frame_height))

class AnimatedSprite(Sprite):
    def __init__(self, x: float = 0, y: float = 0):
        super().__init__(x, y)
        self.animations: Dict[str, Animation] = {}
        self.current_animation: Optional[str] = None
        
    def add_animation(self, name: str, animation: Animation):
        self.animations[name] = animation
        if not self.current_animation:
            self.play_animation(name)
            
    def play_animation(self, name: str, loop: bool = True):
        if name in self.animations:
            self.current_animation = name
            self.animations[name].is_playing = True
            self.animations[name].is_looping = loop
            self.animations[name].current_frame = 0
            self.animations[name].time_accumulated = 0
            
    def update(self, delta_time: float):
        if not self.current_animation:
            return
            
        anim = self.animations[self.current_animation]
        if not anim.is_playing:
            return
            
        anim.time_accumulated += delta_time
        if anim.time_accumulated >= anim.frame_duration:
            anim.time_accumulated = 0
            anim.current_frame += 1
            
            if anim.current_frame >= anim.frame_count:
                if anim.is_looping:
                    anim.current_frame = 0
                else:
                    anim.is_playing = False
                    anim.current_frame = anim.frame_count - 1
                    
        self.src_rect = anim.frames[anim.current_frame]

# Add these classes to sigmaengine.py

class PhysicsBody:
    def __init__(self, entity: Entity):
        self.entity = entity
        self.velocity = [0.0, 0.0]
        self.acceleration = [0.0, 0.0]
        self.mass = 1.0
        self.gravity_scale = 1.0
        self.friction = 0.1
        self.restitution = 0.5
        self.is_static = False
        
    def apply_force(self, force_x: float, force_y: float):
        if not self.is_static:
            self.acceleration[0] += force_x / self.mass
            self.acceleration[1] += force_y / self.mass
            
    def update(self, delta_time: float):
        if self.is_static:
            return
            
        # Apply gravity
        self.acceleration[1] += 9.81 * self.gravity_scale
        
        # Update velocity
        self.velocity[0] += self.acceleration[0] * delta_time
        self.velocity[1] += self.acceleration[1] * delta_time
        
        # Apply friction
        self.velocity[0] *= (1.0 - self.friction)
        self.velocity[1] *= (1.0 - self.friction)
        
        # Update position
        self.entity.x += self.velocity[0] * delta_time
        self.entity.y += self.velocity[1] * delta_time
        
        # Reset acceleration
        self.acceleration = [0.0, 0.0]

class CollisionShape:
    def __init__(self, entity: Entity):
        self.entity = entity
        self.offset_x = 0
        self.offset_y = 0
        
    def get_bounds(self) -> pygame.Rect:
        raise NotImplementedError()
        
    def collides_with(self, other: 'CollisionShape') -> bool:
        raise NotImplementedError()

class BoxCollider(CollisionShape):
    def __init__(self, entity: Entity, width: float, height: float):
        super().__init__(entity)
        self.width = width
        self.height = height
        
    def get_bounds(self) -> pygame.Rect:
        return pygame.Rect(
            self.entity.x + self.offset_x - self.width/2,
            self.entity.y + self.offset_y - self.height/2,
            self.width,
            self.height
        )
        
    def collides_with(self, other: CollisionShape) -> bool:
        if isinstance(other, BoxCollider):
            return self.get_bounds().colliderect(other.get_bounds())
        return False

class CircleCollider(CollisionShape):
    def __init__(self, entity: Entity, radius: float):
        super().__init__(entity)
        self.radius = radius
        
    def get_bounds(self) -> pygame.Rect:
        return pygame.Rect(
            self.entity.x + self.offset_x - self.radius,
            self.entity.y + self.offset_y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
        
    def collides_with(self, other: CollisionShape) -> bool:
        if isinstance(other, CircleCollider):
            dx = self.entity.x - other.entity.x
            dy = self.entity.y - other.entity.y
            distance = math.sqrt(dx*dx + dy*dy)
            return distance < (self.radius + other.radius)
        return False

# Add these classes to sigmaengine.py

class UIElement(Entity):
    def __init__(self, x: float = 0, y: float = 0, width: float = 100, height: float = 50):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.parent = None
        self.children: List[UIElement] = []
        self.padding = 5
        self.background_color = (50, 50, 50)
        self.border_color = (100, 100, 100)
        self.enabled = True
        
    def add_child(self, child: 'UIElement'):
        self.children.append(child)
        child.parent = self
        
    def remove_child(self, child: 'UIElement'):
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            
    def get_absolute_position(self) -> Tuple[float, float]:
        x, y = self.x, self.y
        current = self.parent
        while current:
            x += current.x
            y += current.y
            current = current.parent
        return (x, y)
        
    def contains_point(self, point: Tuple[float, float]) -> bool:
        abs_x, abs_y = self.get_absolute_position()
        return (abs_x - self.width/2 <= point[0] <= abs_x + self.width/2 and
                abs_y - self.height/2 <= point[1] <= abs_y + self.height/2)

class Button(UIElement):
    def __init__(self, x: float = 0, y: float = 0, width: float = 100, height: float = 50,
                 text: str = "Button"):
        super().__init__(x, y, width, height)
        self.text = text
        self.font_size = 24
        self.text_color = (255, 255, 255)
        self.hover_color = (70, 70, 70)
        self.pressed_color = (30, 30, 30)
        self.is_hovered = False
        self.is_pressed = False
        self.on_click = None
        
    def handle_event(self, event: pygame.event.Event):
        if not self.enabled:
            return
            
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.contains_point(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.is_hovered and self.on_click:
                self.on_click()
            self.is_pressed = False
                
    def render(self, screen: pygame.Surface):
        if not self.visible:
            return
            
        # Draw button background
        color = self.background_color
        if self.is_pressed:
            color = self.pressed_color
        elif self.is_hovered:
            color = self.hover_color
            
        abs_x, abs_y = self.get_absolute_position()
        rect = pygame.Rect(abs_x - self.width/2, abs_y - self.height/2,
                         self.width, self.height)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, self.border_color, rect, 2)
        
        # Draw text
        font = pygame.font.Font(None, self.font_size)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(abs_x, abs_y))
        screen.blit(text_surface, text_rect)

class Label(UIElement):
    def __init__(self, x: float = 0, y: float = 0, text: str = "Label"):
        super().__init__(x, y)
        self.text = text
        self.font_size = 24
        self.text_color = (255, 255, 255)
        self.background_color = None
        
    def render(self, screen: pygame.Surface):
        if not self.visible:
            return
            
        font = pygame.font.Font(None, self.font_size)
        text_surface = font.render(self.text, True, self.text_color)
        self.width = text_surface.get_width()
        self.height = text_surface.get_height()
        
        abs_x, abs_y = self.get_absolute_position()
        if self.background_color:
            rect = pygame.Rect(abs_x - self.width/2, abs_y - self.height/2,
                             self.width, self.height)
            pygame.draw.rect(screen, self.background_color, rect)
            
        text_rect = text_surface.get_rect(center=(abs_x, abs_y))
        screen.blit(text_surface, text_rect)

class Panel(UIElement):
    def __init__(self, x: float = 0, y: float = 0, width: float = 200, height: float = 200):
        super().__init__(x, y, width, height)
        self.layout = None
        
    def render(self, screen: pygame.Surface):
        if not self.visible:
            return
            
        # Draw panel background
        abs_x, abs_y = self.get_absolute_position()
        rect = pygame.Rect(abs_x - self.width/2, abs_y - self.height/2,
                         self.width, self.height)
        pygame.draw.rect(screen, self.background_color, rect)
        pygame.draw.rect(screen, self.border_color, rect, 2)
        
        # Update layout if needed
        if self.layout:
            self.layout.update()
            
        # Render children
        for child in self.children:
            child.render(screen)

class Layout:
    def __init__(self, panel: Panel):
        self.panel = panel
        self.spacing = 5
        
    def update(self):
        pass

class VerticalLayout(Layout):
    def update(self):
        if not self.panel.children:
            return
            
        total_height = sum(child.height for child in self.panel.children)
        total_spacing = self.spacing * (len(self.panel.children) - 1)
        current_y = -total_height/2 - total_spacing/2
        
        for child in self.panel.children:
            child.x = 0
            child.y = current_y + child.height/2
            current_y += child.height + self.spacing

class HorizontalLayout(Layout):
    def update(self):
        if not self.panel.children:
            return
            
        total_width = sum(child.width for child in self.panel.children)
        total_spacing = self.spacing * (len(self.panel.children) - 1)
        current_x = -total_width/2 - total_spacing/2
        
        for child in self.panel.children:
            child.x = current_x + child.width/2
            child.y = 0
            current_x += child.width + self.spacing

