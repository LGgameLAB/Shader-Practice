import sys
from array import array


from settings import *
from tween import Tween

import pygame
import moderngl

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
display = pygame.Surface((WIDTH, HEIGHT))
ctx = moderngl.create_context()

clock = pygame.time.Clock()

img = pygame.image.load('trump.jpg')

quad_buffer = ctx.buffer(data=array('f', [
    # position (x, y), uv coords (x, y)
    -1.0, 1.0, 0.0, 0.0,  # topleft
    1.0, 1.0, 1.0, 0.0,   # topright
    -1.0, -1.0, 0.0, 1.0, # bottomleft
    1.0, -1.0, 1.0, 1.0,  # bottomright
]))


class ShaderPass:
    vert_shader = '''
    #version 330 core

    in vec2 vert;
    in vec2 texcoord;
    out vec2 uvs;

    void main() {
        uvs = texcoord;
        gl_Position = vec4(vert, 0.0, 1.0);
    }
    '''

    def __init__(self, frag_path="swizzle.frag", properties={}):
        self.properties = properties

        with open(frag_path, "r") as file:
            self.frag_shader = file.read()
        
        self.program = ctx.program(vertex_shader=self.vert_shader, fragment_shader=self.frag_shader)
        self.fbo = ctx.framebuffer(color_attachments=[ctx.texture((WIDTH, HEIGHT), 4)])
        self.render_object = ctx.vertex_array(self.program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])

    def update(self, t=0):
        # Load our properties into the shader
        for k,v in self.properties.items():
            self.program[k] = v

        # Update time if necessary
        if "time" in self.properties:
            self.program["time"] = t


def surf_to_texture(surf):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
    tex.swizzle = 'BGRA'
    tex.write(surf.get_view('1'))
    return tex


def render_pass(shader_pass, texture):
    """Render a pass using the given framebuffer, input texture, and shader program"""
    shader_pass.fbo.use()
    ctx.clear()
    texture.use(0)
    shader_pass.program['tex'] = 0
    shader_pass.render_object.render(mode=moderngl.TRIANGLE_STRIP)

class Warp(ShaderPass):

    def __init__(self):
        super().__init__("warp.frag", {"size": 20, "spin": 2,"center": (40, 40)})

    def update(self, t=0):
        super().update(t)
        
        x, y = pygame.mouse.get_pos()
        self.program["center"].value = (x/WIDTH, y/HEIGHT)

shaders = [
    Warp(),
    ShaderPass("darkness.frag", {"size": 0.5, "center": (0.5, 0.5)})
]

if len(shaders)%2:
    shaders.append(ShaderPass("blank.frag"))

t = 0
while True:
    display.fill((0, 0, 0))
    display.blit(img, (0,0))

    x, y = pygame.mouse.get_pos()
    # pygame.draw.rect(display, (200, 0, 0), (x, y, 40, 40)) 
    t += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Convert pygame surface to texture
    frame_tex = surf_to_texture(display)

    shaders[0].properties["size"] -= 0.1
    shaders[0].properties["spin"] += 0.1
    # Update Shaders
    for s in shaders:
        s.update(t)

    # Apply shader passes
    render_pass(shaders[0], frame_tex)
    for i in range(1, len(shaders)):
        # Use previous shaders color attachment to stack effects
        render_pass(shaders[i], shaders[i-1].fbo.color_attachments[0])

    # Render final output to screen
    ctx.screen.use()
    ctx.clear()
    shaders[-1].fbo.color_attachments[0].use(0)
    shaders[-1].render_object.render(mode=moderngl.TRIANGLE_STRIP)

    pygame.display.flip()
    frame_tex.release()
    clock.tick(60)

