import pygame,math

SHOWBOX = True
FULLS = True
IMGTOFRAC = pygame.image.load("apple.png")

class PivotSprite(pygame.sprite.Sprite):
    def __init__(self, img, screen, size=1, pos=(0,0), pivot=(0,0)):
        super().__init__()
        self.raw_image = pygame.image.frombuffer(img[0],img[1],'RGBA')
        self.angle = 0
        self.size = size
        self.pos = pos
        self.pivot = pivot
        self.screen = screen
        self.flip = False
        self.update()

    def update(self):
        self.image = pygame.transform.rotozoom(self.raw_image,self.angle,self.size)

        self.center = self.image.get_bounding_rect().center

        pivotrot = (math.cos(math.radians(self.angle))*self.pivot[0]+math.sin(math.radians(self.angle))*self.pivot[1]
                    ,math.sin(math.radians(self.angle))*self.pivot[1]+math.cos(math.radians(self.angle))*self.pivot[0])

        self.blit_pos = tuple(map(lambda x,y,z: x-y+z, self.pos, self.center, pivotrot))
        if self.flip:
            self.screen.blit(pygame.transform.flip(self.image, False, True), self.blit_pos)
        else:
            self.screen.blit(self.image,self.blit_pos)
        self.blit_rec = self.image.get_bounding_rect().move(self.blit_pos)
        if SHOWBOX:
            pygame.draw.rect(self.screen, (255,0,0), self.blit_rec, 5)

class DragGroup(pygame.sprite.OrderedUpdates):
    def __init__(self):
        super().__init__()
    def getClicked(self, coor):
        #should be called under pygame.MOUSEBUTTONDOWN event
        #returns the first sprite that touches the given coordinate
        #if an item is found, move it at the bottom of the list in the group as it is in focus now
        ret = None
        for item in reversed(self.sprites()):
            if item.blit_rec.collidepoint(coor):
                ret = item
                self.remove(item)
                self.add(item)
                break
        return ret
    def changeScreen(self, sur):
        for item in self.sprites():
            item.screen = sur

def main():
    global IMGTOFRAC

    if FULLS:
        screen = pygame.display.set_mode((0,0), pygame.RESIZABLE|pygame.SRCALPHA|pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((500,500), pygame.RESIZABLE|pygame.SRCALPHA)
    screen_alpha = pygame.surface.Surface(screen.get_size(), pygame.SRCALPHA, 32)
    screen_alpha.convert_alpha()
    clock = pygame.time.Clock()

    #source group
    sgroup = DragGroup()
    #fractal group
    fgroup = DragGroup()
    
    imbuf=(pygame.image.tostring(screen_alpha, 'RGBA'), screen_alpha.get_size())
    sbuf=(pygame.image.tostring(IMGTOFRAC, 'RGBA'), IMGTOFRAC.get_size())

    sgroup.add(PivotSprite(sbuf, screen_alpha, .6, (320,240)))

    fgroup.add(PivotSprite(imbuf, screen_alpha, .7, (120,240)))
    fgroup.add(PivotSprite(imbuf, screen_alpha, .6, (320,240)))

    fgroup.update()
    drag = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN and (
                                    (image:=fgroup.getClicked(event.pos)) != None or
                                    (image:=sgroup.getClicked(event.pos)) != None ):
                if event.button == 1:
                    drag = True
                    mouse_init = event.pos
                    orig_init = image.pos
                if event.button == 4:
                    image.size += .01
                elif event.button == 5:
                    image.size -= .01
            elif event.type == pygame.MOUSEMOTION and drag == True:
                image.pos = tuple(map(lambda x,y,z: x-y+z, orig_init ,mouse_init, event.pos))
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                drag = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    global SHOWBOX
                    if SHOWBOX == False:
                        SHOWBOX = True
                    else:
                        SHOWBOX = False
                if( (image:=fgroup.getClicked(pygame.mouse.get_pos())) != None or
                    (image:=sgroup.getClicked(pygame.mouse.get_pos())) != None):
                    if event.key == pygame.K_q:
                        image.angle += 6
                    if event.key == pygame.K_e:
                        image.angle -= 6
                    if event.key == pygame.K_f:
                        if image.flip:
                            image.flip = False
                        else:
                            image.flip = True

        if FULLS:
            #clean alpha surface (doesn't resize surface so we can get away with using only this in fullscreen init)
            screen_alpha.fill((0,0,0,0))
        else:
            #updates screen_alpha according to window size
            screen_alpha = pygame.surface.Surface(screen.get_size(), pygame.SRCALPHA, 32)
            screen_alpha.convert_alpha()
            sgroup.changeScreen(screen_alpha)
            fgroup.changeScreen(screen_alpha)

        #need to do draw a very opaque rectangle border so the alpha surface doesn't shrink
        #not a solution i would prefer but good enough
        pygame.draw.rect(screen_alpha,(0,0,0,1),pygame.Rect(0,0,screen.get_size()[0],screen.get_size()[1]),1)

        #blit groups to alpha surface
        fgroup.update()
        sgroup.update()

        #white bg and blit alpha
        screen.fill((255, 255, 255))
        screen.blit(screen_alpha,(0,0))

        #update fractal group raws with alpha image
        for it in fgroup.sprites():
            it.raw_image = pygame.image.frombuffer(
                pygame.image.tostring(screen_alpha, 'RGBA')
                ,screen_alpha.get_size(),'RGBA')

        pygame.display.flip()

        clock.tick(30)

if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()
