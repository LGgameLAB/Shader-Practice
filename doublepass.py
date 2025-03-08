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

frag_shader_file = "swizzle.frag"
frag_shader_passes = {
        # "exposure": 1,
        # "bloomStrength": 1.5
}
frag_shader = ""

with open(frag_shader_file, "r") as file:
    frag_shader = file.read()

program = ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)

with open("test.frag", "r") as file:
    frag_shader = file.read()

program2 = ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
render_object = ctx.vertex_array(program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])
render_object2 = ctx.vertex_array(program2, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])

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

def render_pass(fbo, texture, program):
    """Render a pass using the given framebuffer, input texture, and shader program"""
    fbo.use()
    ctx.clear()
    texture.use(0)
    program['tex'] = 0
    render_object.render(mode=moderngl.TRIANGLE_STRIP)

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

    # Apply first shader pass
    render_pass(fbo1, frame_tex, program)

    # Apply second shader pass using output from first pass
    render_pass(fbo2, fbo1.color_attachments[0], program2)  # Use a different shader here

    # Render final output to screen
    ctx.screen.use()
    # ctx.clear()
    fbo2.color_attachments[0].use(0)
    program2['tex'] = 0
    render_object2.render(mode=moderngl.TRIANGLE_STRIP)

    pygame.display.flip()
    frame_tex.release()
    clock.tick(60)

