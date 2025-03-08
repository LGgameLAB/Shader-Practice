import sys
from array import array

import pygame
import moderngl

pygame.init()

screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
display = pygame.Surface((800, 600))
ctx = moderngl.create_context()

clock = pygame.time.Clock()

img = pygame.image.load('img.png')

quad_buffer = ctx.buffer(data=array('f', [
    # position (x, y), uv coords (x, y)
    -1.0, 1.0, 0.0, 0.0,  # topleft
    1.0, 1.0, 1.0, 0.0,   # topright
    -1.0, -1.0, 0.0, 1.0, # bottomleft
    1.0, -1.0, 1.0, 1.0,  # bottomright
]))


class ShaderPass:
    def __init__(self, frag_path="swizzle.frag", vert_path=False):
        if vert_path:
            pass

    
        self.vert_shader = '''
        #version 330 core

        in vec2 vert;
        in vec2 texcoord;
        out vec2 uvs;

        void main() {
            uvs = texcoord;
            gl_Position = vec4(vert, 0.0, 1.0);
        }

        '''
        frag_shader_passes = {
                # "exposure": 1,
                # "bloomStrength": 1.5
        }
        self.frag_shader = ""

        with open(frag_path, "r") as file:
            self.frag_shader = file.read()
        
        self.program = ctx.program(vertex_shader=self.vert_shader, fragment_shader=self.frag_shader)
        self.fbo = ctx.framebuffer(color_attachments=[ctx.texture((800, 600), 4)])
        self.render_object = ctx.vertex_array(self.program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])



    def update(self, t=0):
        self.program["time"] = t


def surf_to_texture(surf):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
    tex.swizzle = 'BGRA'
    tex.write(surf.get_view('1'))
    return tex

t = 0

# Create framebuffer and texture for rendering passes
fbo1 = ctx.framebuffer(color_attachments=[ctx.texture((800, 600), 4)])
fbo2 = ctx.framebuffer(color_attachments=[ctx.texture((800, 600), 4)])

def render_pass(shader_pass, texture):
    """Render a pass using the given framebuffer, input texture, and shader program"""
    shader_pass.fbo.use()
    ctx.clear()
    texture.use(0)
    shader_pass.program['tex'] = 0
    shader_pass.render_object.render(mode=moderngl.TRIANGLE_STRIP)

shaders = [
    ShaderPass("test.frag"),
    ShaderPass("swizzle.frag")
    # ShaderPass("test.frag"),
    # ShaderPass("blank.frag")
]


render_object = ctx.vertex_array(shaders[0].program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])
while True:
    display.fill((0, 0, 0))
    display.blit(img, pygame.mouse.get_pos())

    t += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Convert pygame surface to texture
    frame_tex = surf_to_texture(display)

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
    clock.tick(60)

