import pygame
import math
from player import Player
import math
import numpy as np




WIDTH, HEIGHT = 800, 600
FOV = 200  # field of view (hoe groot het lijkt)

pygame.init()
pygame.display.set_caption("3d renderer")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
render_surface = pygame.Surface((200, 150))
clock = pygame.time.Clock()

def dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def cross(a, b):
        return (
            a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0]
        )

def load_obj(filename):
    vertices = []
    triangles = []
    normals = []

    with open(filename, "r") as f:
        for line in f:
            if line.startswith("v "):
                x, y, z = map(float, line.split()[1:])
                scale = 1
                vertices.append((x * scale, y * scale, z * scale))

            elif line.startswith("vn "):
                vn = tuple(map(float, line.split()[1:]))
                normals.append(vn)

            elif line.startswith("f "):
                parts = line.split()[1:]
                indices = [int(p.split("/")[0]) - 1 for p in parts]

    

                v1 = vertices[indices[0]]
                v2 = vertices[indices[1]]
                v3 = vertices[indices[2]]

                triangles.append(Triangle(v1, v2, v3, normals))  # ✅ class!

    return triangles

def project(v, player):
    x, y, z = v

    # =========================
    # 1. CAMERA TRANSLATION
    # =========================
    x -= player.x
    y -= player.y
    z -= player.z

    # =========================
    # 2. YAW ROTATION (links/rechts)
    # =========================
    sin_y = math.sin(-player.yaw)
    cos_y = math.cos(-player.yaw)

    x, z = (
        x * cos_y - z * sin_y,
        x * sin_y + z * cos_y
    )

    # =========================
    # 3. PITCH ROTATION (op/neer)
    # =========================
    sin_p = math.sin(-player.pitch)
    cos_p = math.cos(-player.pitch)

    y, z = (
        y * cos_p - z * sin_p,
        y * sin_p + z * cos_p
    )

    # =========================
    # 4. CLIP (achter camera weg)
    # =========================
    if z <= 0.1:
        z = 0.1

    

    # =========================
    # 5. PERSPECTIVE
    # =========================
    f = 1000/ z 

    x2d = x * f + 400
    y2d = -y * f + 300

    return (x2d, y2d, z)

class sunlicht:
    def __init__(self, dir):
        self.dir = dir


class Triangle:
    def __init__(self, v1, v2, v3, normal):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        #self.v_normals = normal1
        self.distance = v1[0], v2[0], v3[0]
        self.normal = self.get_normal(self.v1, self.v2, self.v3)
       

    def get_vertices(self):
        return [self.v1, self.v2, self.v3]
    

    def get_normal(self, a, b, c):

        ab = (b[0]-a[0], b[1]-a[1], b[2]-a[2])
        ac = (c[0]-a[0], c[1]-a[1], c[2]-a[2])
        
        n = cross(ab, ac)
        
        # normaliseren
        length = (n[0]**2 + n[1]**2 + n[2]**2) ** 0.5
        if length == 0:
            return (0, 0, 0)
        
        return (n[0]/length, n[1]/length, n[2]/length)

# =========================
# 🎮 SCENE
# =========================
player = Player(0, 0, -2)

triangles = load_obj("Wereld/first_obj.obj")

sun = sunlicht((0, 1, 1))

zdata = np.full((200, 150), float("inf"))

def edge(a, b, p):
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])

teller = 0

# =========================
# 🔁 GAME LOOP
# =========================
running = True
while running:

    pixels = pygame.PixelArray(render_surface)
    clock.tick(120)
    render_surface.fill((0, 0, 0))
    zdata.fill(float("inf"))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    teller += 1
    if teller == 1000:
        print("t1000")    
    dt = clock.tick(120) / 1000

    keys = pygame.key.get_pressed()
    player.update(keys, dt)



    
    for tri in triangles:



        v1, v2, v3 = tri.get_vertices()

        v = tri.get_vertices()[0]
        flat_n = tri.normal

    
        
        
        brightness = max(0, dot(flat_n, sun.dir))

        c = int(50 * brightness)
        c += 150
        color = (c, c, c)

        
        

        
        

        # =========================
        # PROJECT TRIANGLE
        # =========================
        pts = []
        pts_verte = 0

        for v in [v1, v2, v3]:
            p = project(v, player)
        
            
            if p is None:
                pts = []
                break
            pts.append(p)
        v1, v2, v3 = pts
        z = (v1[2] + v2[2] + v3[2]) / 3

        min_x = min(v1[0], v2[0], v3[0])
        max_x = max(v1[0], v2[0], v3[0])

        min_y = min(v1[1], v2[1], v3[1])
        max_y = max(v1[1], v2[1], v3[1])

        min_x = int(min_x)
        max_x = int(max_x)
        min_y = int(min_y)
        max_y = int(max_y)
        min_x = max(0, min_x)
        max_x = min(199, max_x)

        min_y = max(0, min_y)
        max_y = min(149, max_y)

        


        for x in range(min_x, max_x):
            for y in range(min_y, max_y):
                p = (x, y)
                w0 = edge(v1, v2, p)
                w1 = edge(v2, v3, p)
                w2 = edge(v3, v1, p)

                area = edge(v1, v2, v3)

                alpha = w1 / area
                beta = w2 / area
                gamma = w0 / area

                z = alpha*v1[2] + beta*v2[2] + gamma*v3[2]
                
                if (w0 >= 0 and w1 >= 0 and w2 >= 0) or \
                    (w0 <= 0 and w1 <= 0 and w2 <= 0):
                        if z < zdata[x, y]:
                            zdata[x, y] = z
                            pixels[x, y] = color

        


    scaled = pygame.transform.scale(render_surface, screen.get_size())
    screen.blit(scaled, (0, 0))

    pygame.display.flip()
    del pixels

pygame.quit()