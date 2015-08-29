import math

import wx
import pygame

def fit_source(source, destination_size):
    inp_x, inp_y = source.get_size()
    inp_ratio = float(inp_x) / inp_y

    dest_x, dest_y = destination_size
    dest_ratio = float(dest_x) / dest_y

    if inp_ratio > dest_ratio:
        scale_ratio = float(dest_x) / inp_x
    else:
        scale_ratio = float(dest_y) / inp_y

    out_x = int(inp_x * scale_ratio)
    out_y = int(inp_y * scale_ratio)

    _im = pygame.transform.smoothscale(source, (out_x, out_y))

    left = (dest_x - out_x) / 2
    top = (dest_y - out_y) / 2

    im = pygame.surface.Surface(destination_size)
    im.fill(0xABABAB)
    im.blit(_im, (left, top))

    return(im)

def is_landscape(source):
    return(source.get_height() <= source.get_width())

def rotate(source, bool_landscape):
    if is_landscape(source) != bool_landscape:
        source = pygame.transform.rotate(source, 90)

    return(source)

def prepare_source(source, destination_size):
    ratio = float(destination_size[0]) / destination_size[1]
    if float(source.get_width()) / source.get_height() > ratio:
        target_width = int(math.ceil(float(source.get_height()) / (1.0/ratio)))
        surf_out = pygame.surface.Surface((target_width, source.get_height()))
        trim_amount = (source.get_width() - target_width) / 2
        surf_out.blit(source, (-trim_amount, 0))

    else:
        target_height = int(math.ceil(float(source.get_width()) / ratio))
        surf_out = pygame.surface.Surface((source.get_width(), target_height))
        trim_amount = (source.get_height() - target_height) / 2
        surf_out.blit(source, (0, -trim_amount))

    surf_out = pygame.transform.smoothscale(surf_out, destination_size)
    return(surf_out)

def show_pygame_surf_in_wxBitmap(source, destination):
    bitmap = wx.ImageFromData(source.get_width(), source.get_height(), pygame.image.tostring(source, "RGB")).ConvertToBitmap(24)
    destination.SetBitmap(bitmap)

def _chain_load_image_to_wxBitmap(fpath, destination): #Possibly lazy way to use a thread.
    im = fit_source(pygame.image.load(fpath), destination.GetSizeTuple())
    show_pygame_surf_in_wxBitmap(im, destination)