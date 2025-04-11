from .engine import (
    Engine,
    Scene,
    GameObject,
    SpriteComponent,
    PhysicsComponent,
    Player,
    Platform,
    Coin,
    GameScene
)

# Version info
__version__ = "0.1.0"

# Define what can be imported with "from sigmaengine import *"
__all__ = [
    'Engine',
    'Scene',
    'GameObject',
    'SpriteComponent',
    'PhysicsComponent',
    'Player',
    'Platform',
    'Coin',
    'GameScene'
]
