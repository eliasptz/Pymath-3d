import pygame
import math


# =========================
# 👤 PLAYER (camera)
# =========================
class Player:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

        self.yaw = 0    # links/rechts draaien
        self.pitch = 0  # op/neer kijken

        self.speed = 10
        self.rot_speed = 3

    def update(self, keys, dt):
    
        # beweging
        dx = math.cos(self.yaw)
        dz = math.sin(self.yaw)

        if keys[pygame.K_d]:
            self.x += dx * self.speed * dt
            self.z += dz * self.speed * dt

        if keys[pygame.K_q]:
            self.x -= dx * self.speed * dt
            self.z -= dz * self.speed * dt

        if keys[pygame.K_SPACE]:
            self.y += 30 * dt  

        if keys[pygame.K_LSHIFT]:
            self.y -= 30 * dt      

        if keys[pygame.K_z]:
            self.x -= dz * self.speed * dt
            self.z += dx * self.speed * dt

        if keys[pygame.K_s]:
            self.x += dz * self.speed * dt
            self.z -= dx * self.speed * dt
        # rotatie
        if keys[pygame.K_LEFT]:
            self.yaw += self.rot_speed * dt
        if keys[pygame.K_RIGHT]:
            self.yaw -= self.rot_speed * dt
        if keys[pygame.K_UP]:
            self.pitch += self.rot_speed * dt
        if keys[pygame.K_DOWN]:
            self.pitch -= self.rot_speed * dt    

