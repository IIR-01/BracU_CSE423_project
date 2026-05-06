import random
from OpenGL.GL import*
from OpenGL.GLUT import*
from OpenGL.GLU import*

fovY= 65
tick= 0
plane_pos= [0.0,0.0,180.0]
plane_speed= 2.4
roll_deg= 0.0
camera_offset= [0,-320,100]
game_paused= False
boss_active= False
boss_health= 20
boss_pos= [0.0,0.0,180.0]
boss_target_pos= [0.0,180.0]
boss_timer= 0
boss_fire_timer= 0
consecutive_kills= 0
triple_shot_timer= 0
floating_texts= []
first_person= False

CAMERA_FIXED_Z= 280
CAMERA_LOOK_Z= 180 


obstacles= []
OBSTACLE_HIT_RADIUS= 55

exhaust_particles= []
explosion_particles= []
bullets= []
enemy_bullets= []
enemies= []

BULLET_SPEED= 16
MAX_BULLET_AGE= 100
FIRE_RATE= 4
fire_cooldown= 0
auto_fire_active= False

powerups= []
POWERUP_RADIUS= 28
POWERUP_FPS= 60
auto_fire_timer= 0
shield_timer= 0
double_pts_timer= 0
POWERUP_SPAWN_INT= 600
powerup_spawn_cnt= 0

ENEMY_SPEED= 0.64
ENEMY_SCALE= 0.32
PLAYER_SCALE= 0.45
SPAWN_INTERVAL= 100
spawn_timer= 0
MAX_ENEMIES= 4
ENEMY_BULLET_SPEED= 7
ENEMY_FIRE_RATE= 140

ENEMY_RADII= {0:20,1:28,2:30} 
PLAYER_HIT_RADIUS= 20

score= 0
last_life_score= 0
lives= 5
invincible_timer= 0
INVINCIBLE_FRAMES= 90
game_over= False
game_over_printed= False

GROUND_Z=  0
CEIL_Z= 360
WALL_X= 600

BOUND_X= 500
BOUND_ZL=  45
BOUND_ZH= 315

TILE_G= 180
TILE_W= 120
ALTITUDE_LEVELS= [75,180,285]
altitude_level= 1

wave= 1
game_won= False

WAVE_CONFIG= {
    1:{'speed':0.64,'interval':80, 'levels':[1],    'next_score':25},
    2:{'speed':0.80,'interval':60, 'levels':[0,1,2],'next_score':50},
    3:{'speed':2.20,'interval':45, 'levels':[0,1,2],'next_score':80},
    4:{'speed':2.50,'interval':40, 'levels':[0,1,2],'next_score':100},
}

def reset_game():
    global tick,roll_deg,score,last_life_score,lives,altitude_level,wave,game_won
    global invincible_timer,game_over,game_over_printed,spawn_timer,fire_cooldown,auto_fire_active
    global auto_fire_timer,shield_timer,double_pts_timer,powerup_spawn_cnt,game_paused
    global boss_active,boss_health,boss_pos,boss_target_pos,boss_timer,boss_fire_timer
    global consecutive_kills,triple_shot_timer
    tick= spawn_timer= fire_cooldown= powerup_spawn_cnt= 0
    roll_deg= 0.0
    altitude_level= 1
    wave= 1
    game_won= False
    score= 0
    last_life_score= 0
    lives= 5
    consecutive_kills= 0
    invincible_timer= 0
    game_over= False
    game_over_printed= False
    auto_fire_active= False
    game_paused= False
    auto_fire_timer= shield_timer= double_pts_timer= triple_shot_timer= 0
    boss_active= False
    boss_health= 20
    boss_timer= 0
    boss_fire_timer= 0
    plane_pos[:]= [0.0,0.0,ALTITUDE_LEVELS[1]]
    enemies.clear()
    bullets.clear()
    enemy_bullets.clear()
    exhaust_particles.clear()
    explosion_particles.clear()
    powerups.clear()
    floating_texts.clear()
    _init_obstacles()


OBSTACLE_HIT_RADIUS= 55
OBS_BOX_W= 100
OBS_BOX_D= 80
OBS_BATCH_SIZE= 2
OBS_BATCH_GAP= 1200


def _make_obs_batch(y_start):
    X_LIMIT= BOUND_X- 60
    batch= []
    for i in range(OBS_BATCH_SIZE):
        y= y_start+ i* 500+ random.uniform(-80,80)
        cx= random.choice([-1,1])* random.uniform(130,X_LIMIT- 20)
        h= random.uniform(150,CEIL_Z)
        batch.append([cx,y,h])
    return batch


def _init_obstacles():
    obstacles.clear()
    for b in _make_obs_batch(plane_pos[1]+ 800):
        obstacles.append(b)
    for b in _make_obs_batch(plane_pos[1]+ 800+ OBS_BATCH_SIZE* 500+ OBS_BATCH_GAP):
        obstacles.append(b)


def draw_obstacles():

    global lives,invincible_timer,game_over,consecutive_kills

    if obstacles:
        max_y= max(o[1] for o in obstacles)
        if max_y- plane_pos[1]< 1400:
            for b in _make_obs_batch(max_y+ OBS_BATCH_GAP):
                obstacles.append(b)
        obstacles[:]= [o for o in obstacles if o[1]>= plane_pos[1]- 10]

    for obs in obstacles:
        cx,cy,box_h= obs
        cz= box_h/ 2.0
        if not game_over and invincible_timer<= 0 and shield_timer<= 0:
            dx= plane_pos[0]- cx
            dy= plane_pos[1]- cy
            if dx*dx+ dy*dy< (PLAYER_HIT_RADIUS+ OBSTACLE_HIT_RADIUS)** 2:
                if plane_pos[2]< box_h+ 20:
                    lives-= 1
                    consecutive_kills= 0
                    invincible_timer= INVINCIBLE_FRAMES
                    spawn_explosion(cx,cy,plane_pos[2])
                    if lives<= 0:
                        game_over= True

        glPushMatrix()
        glTranslatef(cx,cy,cz)

        glColor3f(0.08,0.32,0.30)
        glPushMatrix()
        glScalef(OBS_BOX_W/ 60.0,OBS_BOX_D/ 60.0,box_h/ 60.0)
        glutSolidCube(60)
        glPopMatrix()

        glColor3f(0.15,0.90,0.75)
        glPushMatrix()
        glTranslatef(0,0,box_h/ 2.0)
        glScalef((OBS_BOX_W+ 6)/ 60.0,(OBS_BOX_D+ 6)/ 60.0,4.0/ 60.0)
        glutSolidCube(60)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0,0,-box_h/ 2.0)
        glScalef((OBS_BOX_W+ 6)/ 60.0,(OBS_BOX_D+ 6)/ 60.0,4.0/ 60.0)
        glutSolidCube(60)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(-OBS_BOX_W/ 2.0,0,0)
        glScalef(4.0/ 60.0,(OBS_BOX_D+ 6)/ 60.0,(box_h+ 6)/ 60.0)
        glutSolidCube(60)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(OBS_BOX_W/ 2.0,0,0)
        glScalef(4.0/ 60.0,(OBS_BOX_D+ 6)/ 60.0,(box_h+ 6)/ 60.0)
        glutSolidCube(60)
        glPopMatrix()

        glPopMatrix()


def spawn_powerup():
    X_LIMIT= BOUND_X- 60
    px= random.uniform(-X_LIMIT,X_LIMIT)
    py= plane_pos[1]+ random.uniform(500,1000)
    pz= ALTITUDE_LEVELS[random.randint(0,2)]
    pt= random.randint(0,2)
    powerups.append([px,py,pz,pt])


def draw_powerups():
    global auto_fire_timer,shield_timer,double_pts_timer,auto_fire_active,triple_shot_timer
    alive= []
    for pu in powerups:
        px,py,pz,pt= pu
        dx= plane_pos[0]- px
        dy= plane_pos[1]- py
        dz= plane_pos[2]- pz
        if dx*dx+ dy*dy+ dz*dz< (PLAYER_HIT_RADIUS+ POWERUP_RADIUS)** 2:
            if pt== 0:
                auto_fire_timer= 15* POWERUP_FPS
                auto_fire_active= True
            elif pt== 1:
                triple_shot_timer= 10* POWERUP_FPS
            else:
                double_pts_timer= 8* POWERUP_FPS
            continue
        if py< plane_pos[1]- 300:
            continue
        glPushMatrix()
        glTranslatef(px,py,pz)
        glRotatef(90,1,0,0)
        if pt== 0:
            glColor3f(1.00,0.55,0.05)
        elif pt== 1:
            glColor3f(0.05,0.90,0.90)
        else:
            glColor3f(1.00,0.85,0.00)
        gluCylinder(gluNewQuadric(),POWERUP_RADIUS,POWERUP_RADIUS,22,14,3)
        gluSphere(gluNewQuadric(),POWERUP_RADIUS,14,10)
        glTranslatef(0,0,22)
        gluSphere(gluNewQuadric(),POWERUP_RADIUS,14,10)
        glTranslatef(0,0,-11)
        glColor3f(1.0,1.0,1.0)
        gluCylinder(gluNewQuadric(),POWERUP_RADIUS+ 5,POWERUP_RADIUS+ 5,5,14,1)
        glPopMatrix()
        alive.append(pu)
    powerups[:]= alive


def add_floating_text(x,y,z,text):
    floating_texts.append([x,y,z,text,0])

def draw_floating_texts():
    alive= []
    glColor3f(1.0,1.0,0.0)
    for ft in floating_texts:
        x,y,z,text,age= ft
        ft[2]+= 2.0
        ft[4]+= 1
        if ft[4]< 45:
            glPushMatrix()
            glTranslatef(x,y,z)
            glRasterPos2f(0,0)
            for ch in text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18,ord(ch))
            glPopMatrix()
            alive.append(ft)
    floating_texts[:]= alive

def draw_text(x,y,text,font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0,1000,0,800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x,y)
    for ch in text:
        glutBitmapCharacter(font,ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_environment():
    py= plane_pos[1]
    px= plane_pos[0]

    glBegin(GL_QUADS)

    gx0= int(px/ TILE_G)* TILE_G
    gy0= int(py/ TILE_G)* TILE_G
    for i in range(-2,16):
        for j in range(-8,9):
            tx= gx0+ j* TILE_G
            ty= gy0+ i* TILE_G
            if (int(tx/ TILE_G)+ int(ty/ TILE_G)) % 2== 0:
                glColor3f(0.24,0.24,0.28)
            else:
                glColor3f(0.16,0.16,0.19)
            glVertex3f(tx,ty,GROUND_Z)
            glVertex3f(tx+ TILE_G,ty,GROUND_Z)
            glVertex3f(tx+ TILE_G,ty+ TILE_G,GROUND_Z)
            glVertex3f(tx,ty+ TILE_G,GROUND_Z)

    for i in range(-2,16):
        for j in range(-8,9):
            tx= gx0+ j* TILE_G
            ty= gy0+ i* TILE_G
            if (int(tx/ TILE_G)+ int(ty/ TILE_G)) % 2== 0:
                glColor3f(0.08,0.08,0.16)
            else:
                glColor3f(0.06,0.06,0.12)
            glVertex3f(tx,ty,CEIL_Z)
            glVertex3f(tx+ TILE_G,ty,CEIL_Z)
            glVertex3f(tx+ TILE_G,ty+ TILE_G,CEIL_Z)
            glVertex3f(tx,ty+ TILE_G,CEIL_Z)

    WALL_COLORS= [
        ((0.10,0.10,0.30),(0.08,0.08,0.22)),
        ((0.28,0.10,0.40),(0.20,0.08,0.30)),
        ((0.10,0.35,0.40),(0.08,0.26,0.30)),]

    wy0= int(py/ TILE_W)* TILE_W
    for band in range(3):
        tz= GROUND_Z+ band* TILE_W
        ca,cb= WALL_COLORS[band]
        for j in range(-6,20):
            ty= wy0+ j* TILE_W

            checker= (band+ int(ty/ TILE_W)) % 2
            if checker== 0:
                glColor3f(*ca)
            else:
                glColor3f(*cb)

            glVertex3f(-WALL_X,ty,tz)
            glVertex3f(-WALL_X,ty+ TILE_W,tz)
            glVertex3f(-WALL_X,ty+ TILE_W,tz+ TILE_W)
            glVertex3f(-WALL_X,ty,tz+ TILE_W)

            glVertex3f(WALL_X,ty,tz)
            glVertex3f(WALL_X,ty+ TILE_W,tz)
            glVertex3f(WALL_X,ty+ TILE_W,tz+ TILE_W)
            glVertex3f(WALL_X,ty,tz+ TILE_W)

    glEnd()

    plane_z= plane_pos[2]
    for sx in [-WALL_X,WALL_X]:
        for zmark in [0,120,240,360]:
            diff= abs(plane_z- zmark)
            bright= max(0.0,1.0- diff/ 180.0)
            glPushMatrix()
            glColor3f(0.5+ bright* 0.5,0.5+ bright* 0.4,1.0)
            glTranslatef(sx,plane_pos[1]+ 100,zmark)
            gluSphere(gluNewQuadric(),6,8,6)
            glPopMatrix()


def spawn_exhaust():
    for side in [-1,1]:
        exhaust_particles.append([
            plane_pos[0]+ side* 70* PLAYER_SCALE+ random.uniform(-2,2),
            plane_pos[1]- 58* PLAYER_SCALE + random.uniform(-2,2),
            plane_pos[2]- 28* PLAYER_SCALE + random.uniform(-2,2),0])


def draw_exhaust():
    alive= []
    glPointSize(7)
    glBegin(GL_POINTS)
    for p in exhaust_particles:
        p[1]-= 2.0; p[2]-= 0.25; p[3]+= 1
        fade= 1.0- p[3]/ 32.0
        if fade> 0:
            glColor3f(1.0,fade* 0.45,0.0)
            glVertex3f(p[0],p[1],p[2])
            alive.append(p)
    glEnd()
    exhaust_particles[:]= alive


def spawn_explosion(ex,ey,ez):
    for _ in range(35):
        explosion_particles.append([ex,ey,ez,random.uniform(-10,10),random.uniform(-10,10),random.uniform(-10,10),0])


def draw_explosions():
    alive= []
    glPointSize(11)
    glBegin(GL_POINTS)
    for p in explosion_particles:
        p[0]+= p[3]; p[1]+= p[4]; p[2]+= p[5]; p[6]+= 1
        fade= 1.0- p[6]/ 30.0
        if fade> 0:
            glColor3f(1.0,max(0.0,fade* 0.7),0.0)
            glVertex3f(p[0],p[1],p[2])
            alive.append(p)
    glEnd()
    explosion_particles[:]= alive


def fire_bullet():
    bullets.append([plane_pos[0],plane_pos[1]+ 178,plane_pos[2],0,0])
    if triple_shot_timer> 0:
        bullets.append([plane_pos[0],plane_pos[1]+ 178,plane_pos[2],0,-2.5])
        bullets.append([plane_pos[0],plane_pos[1]+ 178,plane_pos[2],0,2.5])


def draw_bullets():
    alive= []
    for b in bullets:
        dx= b[4] if len(b)> 4 else 0
        b[0]+= dx; b[1]+= BULLET_SPEED; b[3]+= 1
        if b[3]< MAX_BULLET_AGE:
            glPushMatrix()
            glColor3f(1.0,1.0,1.0)
            glTranslatef(b[0],b[1],b[2])
            gluSphere(gluNewQuadric(),5,8,6)
            glPopMatrix()
            glPointSize(5)
            glBegin(GL_POINTS)
            glColor3f(1.0,1.0,1.0)
            glVertex3f(b[0],b[1]- 14,b[2])
            glColor3f(0.8,0.8,0.8)
            glVertex3f(b[0],b[1]- 26,b[2])
            glEnd()
            alive.append(b)
    bullets[:]= alive


def draw_enemy_scout():
    glPushMatrix()
    glColor3f(0.90,0.08,0.08)
    glScalef(0.28,1.85,0.28)
    glutSolidCube(45)
    glPopMatrix()
    for side in [-1,1]:
        glPushMatrix()
        glColor3f(0.75,0.05,0.05)
        glTranslatef(side* 48,-5,-4)
        glScalef(2.20,1.00,0.06)
        glutSolidCube(45)
        glPopMatrix()
    glPushMatrix()
    glColor3f(0.70,0.04,0.04)
    glTranslatef(0,-62,16)
    glScalef(0.06,0.50,0.70)
    glutSolidCube(45)
    glPopMatrix()
    glPushMatrix()
    glColor3f(0.25,0.25,0.28)
    glTranslatef(0,-40,-16)
    glRotatef(-90,1,0,0)
    gluCylinder(gluNewQuadric(),9,7,65,12,3)
    glPopMatrix()
    glPushMatrix()
    glColor3f(1.0,0.40,0.0)
    glTranslatef(0,25,-16)
    glRotatef(-90,1,0,0)
    gluCylinder(gluNewQuadric(),7,10,6,12,2)
    glPopMatrix()
    glPushMatrix()
    glColor3f(1.0,0.30,0.30)
    glTranslatef(0,55,12)
    gluSphere(gluNewQuadric(),11,12,10)
    glPopMatrix()
    glPushMatrix()
    glColor3f(0.60,0.02,0.02)
    glTranslatef(0,75,0)
    glRotatef(-90,1,0,0)
    gluCylinder(gluNewQuadric(),9,0,35,12,6)
    glPopMatrix()


def draw_enemy_saucer():
    glPushMatrix()
    glColor3f(0.55,0.10,0.90)
    glScalef(1.6,1.6,0.28)
    gluSphere(gluNewQuadric(),38,20,14)
    glPopMatrix()
    glPushMatrix()
    glColor3f(0.40,0.05,0.70)
    glTranslatef(0,0,-6)
    gluCylinder(gluNewQuadric(),38,38,5,24,2)
    glPopMatrix()
    glPushMatrix()
    glColor3f(0.80,0.60,1.00)
    glTranslatef(0,0,14)
    gluSphere(gluNewQuadric(),18,14,10)
    glPopMatrix()
    glPushMatrix()
    glColor3f(0.20,0.80,1.00)
    glTranslatef(0,0,-8)
    glRotatef(90,1,0,0)
    gluCylinder(gluNewQuadric(),10,6,14,12,2)
    glPopMatrix()
    for angle in [0,90,180,270]:
        glPushMatrix()
        glColor3f(0.38,0.05,0.65)
        glRotatef(angle,0,0,1)
        glTranslatef(36,0,-2)
        gluSphere(gluNewQuadric(),7,8,6)
        glPopMatrix()


def draw_enemy_bomber():
    glPushMatrix()
    glColor3f(0.28,0.35,0.10)
    glScalef(0.55,2.40,0.55)
    glutSolidCube(55)
    glPopMatrix()
    for side in [-1,1]:
        glPushMatrix()
        glColor3f(0.23,0.30,0.08)
        glTranslatef(side* 78,-4,-10)
        glScalef(2.80,1.50,0.12)
        glutSolidCube(55)
        glPopMatrix()
    for side in [-1,1]:
        glPushMatrix()
        glColor3f(0.20,0.27,0.07)
        glTranslatef(side* 52,-90,0)
        glScalef(1.60,0.65,0.10)
        glutSolidCube(55)
        glPopMatrix()
    glPushMatrix()
    glColor3f(0.20,0.27,0.07)
    glTranslatef(0,-88,30)
    glScalef(0.10,0.60,1.10)
    glutSolidCube(55)
    glPopMatrix()
    for side in [-1,1]:
        for offset in [40,80]:
            glPushMatrix()
            glColor3f(0.18,0.18,0.20)
            glTranslatef(side* offset,-35,-24)
            glRotatef(-90,1,0,0)
            gluCylinder(gluNewQuadric(),10,8,72,14,3)
            glPopMatrix()
            glPushMatrix()
            glColor3f(0.80,0.50,0.05)
            glTranslatef(side* offset,37,-24)
            glRotatef(-90,1,0,0)
            gluCylinder(gluNewQuadric(),8,11,6,14,2)
            glPopMatrix()
    glPushMatrix()
    glColor3f(0.20,0.70,0.20)
    glTranslatef(0,78,18)
    gluSphere(gluNewQuadric(),16,14,10)
    glPopMatrix()
    glPushMatrix()
    glColor3f(0.15,0.20,0.05)
    glTranslatef(0,96,0)
    glRotatef(-90,1,0,0)
    gluCylinder(gluNewQuadric(),13,2,28,14,5)
    glPopMatrix()


_DRAW_FN= {0:draw_enemy_scout,1:draw_enemy_saucer,2:draw_enemy_bomber}


def spawn_enemy_group():
    slots= MAX_ENEMIES- len(enemies)
    if slots<= 0:
        return
    count= random.randint(1,min(2,slots))
    X_LIMIT= BOUND_X- 60
    for _ in range(count):
        etype= random.randint(0,2)
        ex= plane_pos[0]+ random.uniform(-180,180)
        ex= max(-X_LIMIT,min(X_LIMIT,ex))
        ey= plane_pos[1]+ random.uniform(700,1300)
        ez= ALTITUDE_LEVELS[random.choice(WAVE_CONFIG[wave]['levels'])]
        too_close= False
        for obs in obstacles:
            odx= ex- obs[0]
            ody= ey- obs[1]
            if odx*odx+ ody*ody< 120* 120:
                too_close= True
                break
        if not too_close:
            dx= random.choice([-2.5,2.5]) if wave>= 4 else 0
            enemies.append([ex,ey,ez,etype,dx])


def update_and_draw_enemies():
    global score,last_life_score,lives,invincible_timer,game_over,spawn_timer,consecutive_kills
    alive_enemies= []
    alive_bullets= list(bullets)

    for e in enemies:
        ex,ey,ez,etype= e[:4]
        dx= e[4] if len(e)> 4 else 0
        ey-= WAVE_CONFIG[wave]['speed']

        ex+= dx
        if ex<-BOUND_X+ 60 or ex> BOUND_X- 60:
            dx=-dx
            ex+= dx

        ex= max(-BOUND_X,min(BOUND_X,ex))
        ez= max(BOUND_ZL,min(BOUND_ZH,ez))
        e[0],e[1],e[2]= ex,ey,ez
        if len(e)> 4:e[4]= dx

        if ey< plane_pos[1]- 10:
            spawn_timer= WAVE_CONFIG[wave]['interval']
            continue

        hit_r= ENEMY_RADII[etype]
        bullet_hit= False
        new_bullets= []

        for b in alive_bullets:
            dx,dy,dz= b[0]-ex,b[1]-ey,b[2]-ez
            if dx*dx+ dy*dy+ dz*dz< hit_r*hit_r and not bullet_hit:
                spawn_explosion(ex,ey,ez)
                pts= 2 if double_pts_timer> 0 else 1
                score+= pts
                add_floating_text(ex,ey,ez+ 20,f"+{pts}")
                consecutive_kills+= 1
                if consecutive_kills>= 10:
                    score+= 5
                    add_floating_text(ex,ey,ez+ 40,"COMBO+5!")
                    consecutive_kills= 0
                if score- last_life_score>= 30:
                    lives= min(5,lives+ 1)
                    last_life_score+= 30
                bullet_hit= True
            else:
                new_bullets.append(b)
        alive_bullets= new_bullets

        if bullet_hit:
            continue

        if not game_over and invincible_timer<= 0 and shield_timer<= 0:
            dx,dy,dz= plane_pos[0]-ex,plane_pos[1]-ey,plane_pos[2]-ez
            if dx*dx+ dy*dy+ dz*dz< (PLAYER_HIT_RADIUS+ hit_r)**2:
                lives-= 1
                consecutive_kills= 0
                invincible_timer= INVINCIBLE_FRAMES
                spawn_explosion(ex,ey,ez)
                if lives<= 0:
                    game_over= True
                continue

        if ey> plane_pos[1]:
            fdx= plane_pos[0]- ex
            fdy= plane_pos[1]- ey
            fdz= plane_pos[2]- ez
            close= (fdx*fdx+ fdy*fdy+ fdz*fdz)** 0.5< 400
            threshold= ENEMY_FIRE_RATE// 3 if close else ENEMY_FIRE_RATE
            if random.randint(0,threshold)== 0:
                fire_enemy_bullet(ex,ey,ez)



        glPushMatrix()
        glTranslatef(ex,ey,ez)
        glRotatef(180,0,0,1)
        glScalef(ENEMY_SCALE,ENEMY_SCALE,ENEMY_SCALE)
        _DRAW_FN[etype]()
        glPopMatrix()
        alive_enemies.append(e)

    enemies[:]= alive_enemies
    bullets[:]= alive_bullets


def fire_enemy_bullet(ex,ey,ez):
    dx= plane_pos[0]- ex
    dy= plane_pos[1]- ey
    dz= plane_pos[2]- ez
    dist= (dx*dx+ dy*dy+ dz*dz)** 0.5
    if dist> 0:
        spd= ENEMY_BULLET_SPEED* (2 if wave== 3 else 1)
        enemy_bullets.append([ex,ey,ez,(dx/ dist)* spd,(dy/ dist)* spd,(dz/ dist)* spd,0])


def draw_enemy_bullets():
    global lives,invincible_timer,game_over,consecutive_kills
    alive= []
    for b in enemy_bullets:
        b[0]+= b[3]; b[1]+= b[4]; b[2]+= b[5]; b[6]+= 1
        if b[6]>= MAX_BULLET_AGE or b[1]< plane_pos[1]- 10:
            continue
        if not game_over and invincible_timer<= 0 and shield_timer<= 0:
            dx= plane_pos[0]- b[0]
            dy= plane_pos[1]- b[1]
            dz= plane_pos[2]- b[2]
            if dx*dx+ dy*dy+ dz*dz< PLAYER_HIT_RADIUS** 2:
                lives-= 1
                consecutive_kills= 0
                invincible_timer= INVINCIBLE_FRAMES
                spawn_explosion(b[0],b[1],b[2])
                if lives<= 0:
                    game_over= True
                continue

        glPushMatrix()
        glColor3f(0.80,0.0,0.0)
        glTranslatef(b[0],b[1],b[2])
        if wave== 4:
            gluSphere(gluNewQuadric(),9,8,6)
        else:
            gluSphere(gluNewQuadric(),5,8,6)
        glPopMatrix()
        glPointSize(5)
        glBegin(GL_POINTS)
        glColor3f(0.5,0.0,0.0)
        glVertex3f(b[0]- b[3]* 0.7,b[1]- b[4]* 0.7,b[2]- b[5]* 0.7)
        glEnd()
        alive.append(b)
    enemy_bullets[:]= alive


def draw_boss():
    if not boss_active:return
    glPushMatrix()
    glTranslatef(boss_pos[0],boss_pos[1],boss_pos[2])
    
    glColor3f(0.9,0.1,0.1)
    gluSphere(gluNewQuadric(),60,16,16)
    
    glColor3f(0.2,0.2,0.2)
    glPushMatrix()
    glRotatef(tick* 3,0,1,0)
    glTranslatef(-120,0,0)
    glRotatef(90,0,1,0)
    gluCylinder(gluNewQuadric(),15,15,240,12,1)
    glPopMatrix()

    glPushMatrix()
    glRotatef(tick*-3,1,0,0)
    glTranslatef(0,-120,0)
    glRotatef(-90,1,0,0)
    gluCylinder(gluNewQuadric(),15,15,240,12,1)
    glPopMatrix()
    
    glPopMatrix()


def draw_shapes():
    draw_environment()
    draw_boss()

    if invincible_timer> 0 and (invincible_timer// 6) % 2== 0:
        pass
    elif not first_person:
        glPushMatrix()
        glTranslatef(plane_pos[0],plane_pos[1],plane_pos[2])
        glRotatef(roll_deg,0,1,0)
        glScalef(PLAYER_SCALE,PLAYER_SCALE,PLAYER_SCALE)

        glPushMatrix()
        glColor3f(0.82,0.82,0.90)
        glScalef(0.50,4.20,0.50)
        glutSolidCube(60)
        glPopMatrix()

        for side in [-1,1]:
            glPushMatrix()
            glColor3f(0.72,0.72,0.82)
            glTranslatef(side* 80,-20,-8)
            glRotatef(25* side,0,1,0)
            glScalef(3.00,1.20,0.08)
            glutSolidCube(60)
            glPopMatrix()

        for side in [-1,1]:
            glPushMatrix()
            glColor3f(0.72,0.72,0.82)
            glTranslatef(side* 40,80,-4)
            glRotatef(15* side,0,1,0)
            glScalef(1.20,0.80,0.08)
            glutSolidCube(60)
            glPopMatrix()

        for side in [-1,1]:
            glPushMatrix()
            glColor3f(0.65,0.65,0.75)
            glTranslatef(side* 48,-112,0)
            glScalef(1.35,0.70,0.08)
            glutSolidCube(60)
            glPopMatrix()

        glPushMatrix()
        glColor3f(0.65,0.65,0.75)
        glTranslatef(0,-110,28)
        glScalef(0.08,0.68,1.00)
        glutSolidCube(60)
        glPopMatrix()

        for side in [-1,1]:
            glPushMatrix()
            glColor3f(0.30,0.30,0.36)
            glTranslatef(side* 70,-58,-28)
            glRotatef(-90,1,0,0)
            gluCylinder(gluNewQuadric(),14,11,100,18,4)
            glPopMatrix()
            glPushMatrix()
            glColor3f(0.15,0.15,0.20)
            glTranslatef(side* 70,42,-28)
            glRotatef(-90,1,0,0)
            gluCylinder(gluNewQuadric(),14,14,5,18,1)
            glPopMatrix()
            glPushMatrix()
            glColor3f(0.60,0.22,0.05)
            glTranslatef(side* 70,-58,-28)
            glRotatef(90,1,0,0)
            gluCylinder(gluNewQuadric(),11,15,10,18,2)
            glPopMatrix()

        glPushMatrix()
        glColor3f(0.10,0.85,1.00)
        glTranslatef(0,92,20)
        gluSphere(gluNewQuadric(),20,18,14)
        glPopMatrix()

        glPushMatrix()
        glColor3f(0.88,0.18,0.08)
        glTranslatef(0,126,0)
        glRotatef(-90,1,0,0)
        gluCylinder(gluNewQuadric(),15,0,52,18,8)
        glPopMatrix()

        glPopMatrix()

    draw_exhaust()
    draw_bullets()
    update_and_draw_enemies()
    draw_enemy_bullets()
    draw_explosions()
    draw_obstacles()
    draw_powerups()
    draw_floating_texts()

def keyboardListener(key,x,y):
    global game_paused,first_person
    if key== b'c' or key== b'C':
        first_person= not first_person
    if key== b' ' and not game_over:
        game_paused= not game_paused
    if key in (b'r',b'R'):
        reset_game()


def specialKeyListener(key,x,y):
    global roll_deg,altitude_level
    if game_over:
        return
    STEP= 20
    X_LIMIT= BOUND_X- 60
    if key== GLUT_KEY_LEFT:
        plane_pos[0]= max(-X_LIMIT,plane_pos[0]- STEP)
        roll_deg= max(roll_deg- 8,-45)
    if key== GLUT_KEY_RIGHT:
        plane_pos[0]= min( X_LIMIT,plane_pos[0]+ STEP)
        roll_deg= min(roll_deg+ 8, 45)
    if key== GLUT_KEY_UP:
        altitude_level= min(2,altitude_level+ 1)
        plane_pos[2]= ALTITUDE_LEVELS[altitude_level]
    if key== GLUT_KEY_DOWN:
        altitude_level= max(0,altitude_level- 1)
        plane_pos[2]= ALTITUDE_LEVELS[altitude_level]
    glutPostRedisplay()


def mouseListener(button,state,x,y):
    if button== GLUT_LEFT_BUTTON and state== GLUT_DOWN and not game_over:
        fire_bullet()


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY,1.25,0.1,10000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if first_person:
        ex= plane_pos[0]
        ey= plane_pos[1]+ 160
        ez= plane_pos[2]+ 40
        gluLookAt(ex,ey,ez,
                  ex,ey+ 1000,ez,
                  0,0,1)
    else:
        ex= plane_pos[0]+ camera_offset[0]
        ey= plane_pos[1]+ camera_offset[1]
        ez= CAMERA_FIXED_Z
        gluLookAt(ex,ey,ez,
                  plane_pos[0],plane_pos[1]+ 180,CAMERA_LOOK_Z,
                  0,0,1)


def idle():
    global tick,fire_cooldown,roll_deg,spawn_timer,invincible_timer,wave,game_won,score,lives
    global auto_fire_timer,shield_timer,double_pts_timer,auto_fire_active,powerup_spawn_cnt,game_over_printed
    global boss_active,boss_health,boss_pos,boss_target_pos,boss_timer,boss_fire_timer,triple_shot_timer

    if game_paused:
        glutPostRedisplay()
        return

    tick      += 1
    if not boss_active:
        spawn_timer     += 1
        powerup_spawn_cnt+= 1

    if game_over and not game_over_printed:
        print(f"Game over! Final Score:{score}")
        game_over_printed= True

    if not game_over and not game_won:
        plane_pos[1]+= plane_speed

        if boss_active:
            bx,by,bz= boss_pos
            boss_pos[1]= plane_pos[1]+ 800.0
            tx,tz= boss_target_pos
            
            boss_pos[0]+= (tx- bx)* 0.15
            boss_pos[2]+= (tz- bz)* 0.15
            
            boss_timer+= 1
            if boss_timer> 120:
                boss_timer= 0
                for _ in range(10):
                    tx= random.uniform(-BOUND_X+ 100,BOUND_X- 100)
                    tz= random.choice(ALTITUDE_LEVELS)
                    too_close= False
                    for obs in obstacles:
                        if abs(tx- obs[0])< 120:
                            too_close= True
                            break
                    if not too_close:
                        break
                boss_target_pos[0]= tx
                boss_target_pos[1]= tz
            
            boss_fire_timer+= 1
            if boss_fire_timer> 30:
                boss_fire_timer= 0
                dx= plane_pos[0]- boss_pos[0]
                dy= plane_pos[1]- boss_pos[1]
                dz= plane_pos[2]- boss_pos[2]
                dist= (dx*dx+ dy*dy+ dz*dz)**0.5
                if dist> 0:
                    speed= 8.0
                    bx,by,bz= (dx/dist)*speed,(dy/dist)*speed,(dz/dist)*speed
                    enemy_bullets.append([boss_pos[0],boss_pos[1],boss_pos[2],bx,by,bz,0])
                    enemy_bullets.append([boss_pos[0],boss_pos[1],boss_pos[2],bx- 2.5,by,bz,0])
                    enemy_bullets.append([boss_pos[0],boss_pos[1],boss_pos[2],bx+ 2.5,by,bz,0])
            
            new_bullets= []
            for b in bullets:
                dx= boss_pos[0]- b[0]
                dy= boss_pos[1]- b[1]
                dz= boss_pos[2]- b[2]
                if dx*dx+ dy*dy+ dz*dz< 60*60:
                    spawn_explosion(b[0],b[1],b[2])
                    boss_health-= 1
                    if boss_health<= 0:
                        print("You killed the boss!")
                        add_floating_text(boss_pos[0],boss_pos[1],boss_pos[2]+ 30,"BOSS DEFEATED!")
                        game_won= True
                        boss_active= False
                        score+= 50
                else:
                    new_bullets.append(b)
            bullets[:]= new_bullets

        if roll_deg> 0:  roll_deg= max(0.0,roll_deg- 1.5)
        elif roll_deg< 0:roll_deg= min(0.0,roll_deg+ 1.5)

        if invincible_timer> 0:
            invincible_timer-= 1

        if auto_fire_timer> 0:
            auto_fire_timer-= 1
            auto_fire_active= True
        else:
            auto_fire_active= False
        if shield_timer> 0:
            shield_timer-= 1
        if double_pts_timer> 0:
            double_pts_timer-= 1
        if triple_shot_timer> 0:
            triple_shot_timer-= 1

        if score>= WAVE_CONFIG[wave]['next_score']:
            if wave< 4:
                wave += 1
                spawn_timer= WAVE_CONFIG[wave]['interval']
                shield_timer= 10* POWERUP_FPS
                enemies.clear()
                enemy_bullets.clear()
            elif wave== 4 and not boss_active:
                boss_active= True
                boss_health= 20
                boss_pos[:]= [0.0,plane_pos[1]+ 800.0,ALTITUDE_LEVELS[1]]
                boss_target_pos[:]= [0.0,ALTITUDE_LEVELS[1]]
                boss_timer= 0
                boss_fire_timer= 0
                enemies.clear()
                powerups.clear()
                auto_fire_timer= shield_timer= double_pts_timer= triple_shot_timer= 0
                auto_fire_active= False

        if not game_won and not boss_active:
            if spawn_timer>= WAVE_CONFIG[wave]['interval']:
                spawn_enemy_group()
                spawn_timer= 0

            spawn_exhaust()

            if auto_fire_active:
                fire_cooldown-= 1
                if fire_cooldown<= 0:
                    fire_bullet()
                    fire_cooldown= FIRE_RATE

            if powerup_spawn_cnt>= POWERUP_SPAWN_INT:
                spawn_powerup()
                powerup_spawn_cnt= 0

    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    if game_paused:
        draw_text(400,400,"Want a pause?")
        glutSwapBuffers()
        return

    glLoadIdentity()
    glViewport(0,0,1000,800)

    setupCamera()

    alt_label= ["LOW","MID","HIGH"][altitude_level]
    hearts= ("* "* lives).strip() if lives> 0 else "DEAD"
    cfg= WAVE_CONFIG[wave]
    need= max(0,cfg['next_score']- score)
    wave_label= {1:"Level 1  [MID lane only]",
                  2:"Level 2  [All lanes]",
                  3:"Level 3  [ELITE]",
                  4:"Level 4  [SWARM]"}[wave]

    if boss_active:
        wave_label= f"BOSS FIGHT [Health:{boss_health}]"
        need= 0

    pu_parts= []
    if auto_fire_active:  pu_parts.append(f"AUTO-FIRE {auto_fire_timer// POWERUP_FPS+ 1}s")
    if triple_shot_timer> 0:pu_parts.append(f"TRIPLE {triple_shot_timer// POWERUP_FPS+ 1}s")
    if shield_timer> 0:  pu_parts.append(f"SHIELD {shield_timer// POWERUP_FPS+ 1}s")
    if double_pts_timer> 0:pu_parts.append(f"2x PTS {double_pts_timer// POWERUP_FPS+ 1}s")
    pu_status= "  ["+ " | ".join(pu_parts)+ "]" if pu_parts else ""

    draw_text(10,770,f"SKY FORCE  |  {wave_label}")
    if boss_active:
        draw_text(10,742,f"Score:{score}  (Kill the boss to win)")
    else:
        draw_text(10,742,f"Score:{score}  ({need} more to advance)")
    draw_text(10,714,f"Lives:{hearts}{pu_status}")

    if game_over:
        draw_text(250,420,f"GAME OVER  |  Score:{score}  |  Press R to restart")
    elif game_won:
        draw_text(300,430,"Congratulations! You have won the game!!")

    draw_shapes()
    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000,800)
    glutInitWindowPosition(0,0)
    glutCreateWindow(b"3D SKY FORCE")

    glEnable(GL_DEPTH_TEST)
    _init_obstacles()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__== "__main__":
    main()
