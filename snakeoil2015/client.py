#!/usr/bin/python
import sys
import math
import def_param
import snakeoil

target_speed = 0
lap = 0
prev_distance_from_start = 1
learn_final = False
opHistory = list()
trackHistory = [0]
TRACKHISTORYMAX = 50
secType = 0
secBegin = 0
secMagnitude = 0
secWidth = 0
sangs = [-45, -19, -12, -7, -4, -2.5, -1.7, -1, -.5, 0, .5, 1, 1.7, 2.5, 4, 7, 12, 19, 45]
sangsrad = [(math.pi * X / 180.0) for X in sangs]
badness = 0


class Track():
    def __init__(self):
        self.laplength = 0
        self.width = 0
        self.sectionList = list()
        self.usable_model = False

    def __repr__(self):
        o = 'TrackList:\n'
        o += '\n'.join([repr(x) for x in self.sectionList])
        o += "\nLap Length: %s\n" % self.laplength
        return o

    def post_process_track(self):
        ws = [round(s.width) for s in self.sectionList]
        ws = filter(lambda O: O, ws)  # ??????
        ws.sort()
        self.width = ws[len(ws) / 2]  # width del track: width al centro !?
        cleanedlist = list()
        TooShortToBeASect = 6
        for n, s in enumerate(self.sectionList):
            if s.dist > TooShortToBeASect:
                if cleanedlist and not s.direction and not cleanedlist[-1].direction:
                    cleanedlist[-1].end = s.end
                else:
                    cleanedlist.append(s)
            else:
                if cleanedlist:
                    prevS = cleanedlist[-1]
                    prevS.end = s.apex
                    prevS.dist = prevS.end - prevS.start
                    prevS.apex = prevS.dist / 2 + prevS.start
                if len(self.sectionList) - 1 >= n + 1:
                    nextS = self.sectionList[n + 1]
                    nextS.start = s.apex
                    nextS.dist = nextS.end - nextS.start
                    nextS.apex = nextS.dist / 2 + nextS.start
                else:
                    prevS.end = self.laplength
                    prevS.dist = prevS.end - prevS.start
                    prevS.apex = prevS.dist / 2 + prevS.start
        self.sectionList = cleanedlist
        self.usable_model = True

    def write_track(self, fn):
        firstline = "%f\n" % self.width
        f = open(fn + '.trackinfo', 'w')
        f.write(firstline)
        for s in self.sectionList:
            ts = '%f %f %f %d\n' % (s.start, s.end, s.magnitude, s.badness)
            f.write(ts)
        f.close()

    def load_track(self, fn):
        self.sectionList = list()
        with open(fn + '.trackinfo', 'r') as f:
            self.width = float(f.readline().strip())
            for l in f:
                data = l.strip().split(' ')
                TS = TrackSection(float(data[0]), float(data[1]), float(data[2]), self.width, int(data[3]))
                self.sectionList.append(TS)
        self.laplength = self.sectionList[-1].end
        self.usable_model = True

    def section_in_now(self, d):
        '''ritorna la sezione in ci si trova attualmente, altrimenti None'''
        for s in self.sectionList:
            if s.start < d < s.end:
                return s
        else:
            return None

    def section_ahead(self, d):
        '''ritorna la sezione successiva a quella in ci si trova attualmente, altrimenti None'''
        for n, s in enumerate(self.sectionList):
            if s.start < d < s.end:
                if n < len(self.sectionList) - 1:
                    return self.sectionList[n + 1]
                else:
                    return self.sectionList[0]
        else:
            return None

    def record_badness(self, b, d):
        '''Salva la badness della sezione corrente'''
        sn = self.section_in_now(d)
        if sn:
            sn.badness += b


class TrackSection():
    def __init__(self, sBegin, sEnd, sMag, sWidth, sBadness):
        if sMag:
            self.direction = int(abs(sMag) / sMag)
        else:
            self.direction = 0
        self.start = sBegin
        self.end = sEnd
        self.dist = self.end - self.start
        if not self.dist: self.dist = .1
        self.apex = self.start + self.dist / 2  # centro della section (?)
        self.magnitude = sMag
        self.width = sWidth
        self.severity = self.magnitude / self.dist
        self.badness = sBadness

    def __repr__(self):
        tt = ['Right', 'Straight', 'Left'][self.direction + 1]
        o = "S: %f  " % self.start
        o += "E: %f  " % self.end
        o += "L: %f  " % (self.end - self.start)  # length
        o += "Type: %s  " % tt
        o += "M: %f " % self.magnitude
        o += "B: %f " % self.badness
        return o

    # unused and not implemented...
    def update(self, distFromStart, trackPos, steer, angle, z):
        pass

    # unused
    def current_section(self, x):
        return self.begin <= x and x <= self.end


def automatic_transimission(P, g, c, rpm, sx, ts, tick):
    clutch_releaseF = .05
    ng, nc = g, c
    if ts < 0 and g > -1:
        ng = -1
        nc = 1
    elif ts > 0 and g < 0:
        ng = g + 1
        nc = 1
    elif c > 0:
        if g:
            nc = c - clutch_releaseF
        else:
            if ts < 0:
                ng = -1
            else:
                ng = 1
    elif not tick % 50 and sx > 20:
        pass
    elif g == 6 and rpm < P['dnsh5rpm']:
        ng = g - 1
        nc = 1
    elif g == 5 and rpm < P['dnsh4rpm']:
        ng = g - 1
        nc = 1
    elif g == 4 and rpm < P['dnsh3rpm']:
        ng = g - 1
        nc = 1
    elif g == 3 and rpm < P['dnsh2rpm']:
        ng = g - 1
        nc = 1
    elif g == 2 and rpm < P['dnsh1rpm']:
        ng = g - 1
        nc = 1
    elif g == 5 and rpm > P['upsh6rpm']:
        ng = g + 1
        nc = 1
    elif g == 4 and rpm > P['upsh5rpm']:
        ng = g + 1
        nc = 1
    elif g == 3 and rpm > P['upsh4rpm']:
        ng = g + 1
        nc = 1
    elif g == 2 and rpm > P['upsh3rpm']:
        ng = g + 1
        nc = 1
    elif g == 1 and rpm > P['upsh2rpm']:
        ng = g + 1
        nc = 1
    elif not g:
        ng = 1
        nc = 1
    else:
        pass
    return ng, nc


# def automatic_transimission(P, g, c, rpm, sx, ts, tick):
#     clutch_releaseF = .15
#     ng, nc = g, c
#     if ts < 0 and g > -1:
#         ng = -1
#         nc = 1
#     elif ts > 0 and g < 0:
#         ng = g + 1
#         nc = 1
#     elif c > 0:
#         if g:
#             nc = c - clutch_releaseF
#         else:
#             if ts < 0:
#                 ng = -1
#             else:
#                 ng = 1
#     elif not tick % 25 and sx > 20:
#         pass
#     elif g == 6 and rpm < 5500:
#         ng = g - 1
#         nc = 1
#     elif g == 5 and rpm < 5300:
#         ng = g - 1
#         nc = 1
#     elif g == 4 and rpm < 5000:
#         ng = g - 1
#         nc = 1
#     elif g == 3 and rpm < 4700:
#         ng = g - 1
#         nc = 1
#     elif g == 2 and rpm < 4400:
#         ng = g - 1
#         nc = 1
#     elif g == 5 and rpm > 8600:
#         ng = g + 1
#         nc = 1
#     elif g == 4 and rpm > 8500:
#         ng = g + 1
#         nc = 1
#     elif g == 3 and rpm > 8400:
#         ng = g + 1
#         nc = 1
#     elif g == 2 and rpm > 8200:
#         ng = g + 1
#         nc = 1
#     elif g == 1 and rpm > 8000:
#         ng = g + 1
#         nc = 1
#     elif not g:
#         ng = 1
#         nc = 1
#     else:
#         pass
#     return ng, nc


def find_slip(wsv_list):
    w1, w2, w3, w4 = wsv_list
    if w1:
        slip = (w3 + w4) - (w1 + w2)
    else:
        slip = 0
    return slip


def track_sensor_analysis(t, a):
    alpha = 0
    sense = 1
    ps = list()
    realt = list()
    sangsradang = [(math.pi * X / 180.0) + a for X in sangs]
    for n, sang in enumerate(sangsradang):
        x, y = t[n] * math.cos(sang), t[n] * -math.sin(sang)
        if float(x) > 190:
            alpha = math.pi
        else:
            ps.append((x, y))
            realt.append(t[n])
    firstYs = [p[1] for p in ps[0:3]]
    lastYs = [p[1] for p in ps[-3:]]
    straightnessf = abs(1 - abs(min(firstYs)) / max(.0001, abs(max(firstYs))))
    straightnessl = abs(1 - abs(min(lastYs)) / max(.0001, abs(max(lastYs))))
    straightness = max(straightnessl, straightnessf)
    farthest = realt.index(max(realt))
    ls = ps[0:farthest]
    rs = ps[farthest + 1:]
    rs.reverse()
    if 0 < farthest < len(ps) - 1:
        beforePdist = t[farthest - 1]
        afterPdist = t[farthest + 1]
        if beforePdist > afterPdist:
            sense = -1
            outsideset = ls
            # insideset = rs
            ls.append(ps[farthest])
        else:
            outsideset = rs
            # insideset = ls
            rs.append(ps[farthest])
    else:
        if ps[0][0] > ps[-1][0]:
            ps.reverse()
            # farthest = (len(ps) - 1) - farthest
        if ps[0][1] > ps[-1][1]:
            sense = -1
            outsideset = ls
            # insideset = rs
        else:
            outsideset = rs
            # insideset = ls
    maxpdist = 0
    if not outsideset:
        return (0, a, 2)
    nearx, neary = outsideset[0][0], outsideset[0][1]
    farx, fary = outsideset[-1][0], outsideset[-1][1]
    cdeltax, cdeltay = (farx - nearx), (fary - neary)
    c = math.sqrt(cdeltax * cdeltax + cdeltay * cdeltay)
    for p in outsideset[1:-1]:
        dx1 = p[0] - nearx
        dy1 = p[1] - neary
        dx2 = p[0] - farx
        dy2 = p[1] - fary
        a = math.sqrt(dx1 * dx1 + dy1 * dy1)
        b = math.sqrt(dx2 * dx2 + dy2 * dy2)
        pdistances = a + b
        if pdistances > maxpdist:
            maxpdist = pdistances
            inflectionp = p
            ia = a
            ib = b
    if maxpdist and not alpha:
        infleX = inflectionp[0]
        preprealpha = 2 * ia * ib
        if not preprealpha: preprealpha = .00000001
        prealpha = (ia * ia + ib * ib - c * c) / preprealpha
        if prealpha > 1:
            alpha = 0
        elif prealpha < -1:
            alpha = math.pi
        else:
            alpha = math.acos(prealpha)
        turnsangle = sense * (180 - (alpha * 180 / math.pi))
    else:
        infleX = max(t)
        turnsangle = sangs[t.index(infleX)]
    return (infleX, turnsangle, straightness)


def speed_planning(P, t, sx, sy, st, a, infleX, infleA):
    cansee = max(t[2:17])
    if cansee > 0:
        carmax = P['carmaxvisib'] * cansee
        if cansee > 190 and abs(a) < .1:
            return carmax
    else:
        return 70

    if t[9] < 40:
        return P['obviousbase'] + t[9] * P['obvious']
    if infleA:
        willneedtobegoing = 600 - 180.0 * math.log(abs(infleA))
        willneedtobegoing = max(willneedtobegoing, P['carmin'])
    else:
        willneedtobegoing = carmax
    brakingpacecut = 150
    if sx > brakingpacecut:
        brakingpace = P['brakingpacefast']
    else:
        brakingpace = P['brakingpaceslow']
    base = min(infleX * brakingpace + willneedtobegoing, carmax)
    base = max(base, P['carmin'])
    if st < P['consideredstr8']:
        return base
    uncoolsy = abs(sy) / sx
    syadjust = 2 - 1 / P['oksyp'] * uncoolsy
    return base * syadjust


def damage_speed_adjustment(d):
    dsa = 1
    if d > 1000:
        dsa = 1 - .02 * d / 1000
    return dsa


def jump_speed_adjustment(z):
    offtheground = snakeoil.clip(z - .350, 0, 1000)
    jsa = offtheground * -800
    return jsa


def traffic_speed_adjustment(os, sx, ts, tsen):
    global opHistory
    if not opHistory:
        opHistory = os
        return 0
    tsa = 0
    mpn = 0
    sn = min(os[17], os[18])
    if sn > tsen[9] and tsen[9] > 0:
        return 0
    if sn < 15:
        sn = min(sn, os[16], os[19])
    if sn < 8:
        sn = min(sn, os[15], os[20])
    sn -= 5
    if sn < 3:
        opHistory = os
        return -ts
    opn = mpn + sn
    mpp = mpn - sx / 180
    sp = min(opHistory[17], opHistory[18])
    if sp < 15:
        sp = min(sp, os[16], os[19])
    if sp < 8:
        sp = min(sn, os[15], os[20])
    sp -= 5
    opHistory = os
    opp = mpp + sp
    osx = (opn - opp) * 180
    osx = snakeoil.clip(osx, 0, 300)
    if osx - sx > 0: return 0
    max_tsa = osx - ts
    max_worry = 80
    full_serious = 20
    if sn > max_worry:
        seriousness = 0
    elif sn < full_serious:
        seriousness = 1
    else:
        seriousness = (max_worry - sn) / (max_worry - full_serious)
    tsa = max_tsa * seriousness
    tsa = snakeoil.clip(tsa, -ts, 0)
    return tsa


def steer_centeralign(P, tp, a, ttp=0):
    pointing_ahead = abs(a) < P['pointingahead']   #  "margine di sicurezza"   2
    onthetrack = abs(tp) < P['sortofontrack']      #  dipende dal circuito     1
    offrd = 1
    if not onthetrack:
        offrd = P['offroad']
    if pointing_ahead:
        sto = a
    else:
        sto = a * P['backward']
    ttp *= 1 - a
    sto += (ttp - min(tp, P['steer2edge'])) * P['s2cen'] * offrd
    return sto


def speed_appropriate_steer(P, sto, sx):
    if sx > 0:
        stmax = max(P['sxappropriatest1'] / math.sqrt(sx) - P['sxappropriatest2'], P['safeatanyspeed'])
    else:
        stmax = 1
    return snakeoil.clip(sto, -stmax, stmax)


def steer_reactive(P, tp, a, t, sx, infleA, str8ness):
    if abs(a) > .6:
        return steer_centeralign(P, tp, a)
    maxsen = max(t)
    if maxsen > 0 and abs(tp) < .99:
        MaxSensorPos = t.index(maxsen)
        MaxSensorAng = sangsrad[MaxSensorPos]
        sensangF = -.9
        aadj = MaxSensorAng * sensangF
        if maxsen < 40:
            ttp = MaxSensorAng * - P['s2sen'] / maxsen
        else:
            if str8ness < P['str8thresh'] and abs(infleA) > P['ignoreinfleA']:
                ttp = -abs(infleA) / infleA
                aadj = 0
            else:
                ttp = 0
        senslimF = .031
        ttp = snakeoil.clip(ttp, tp - senslimF, tp + senslimF)
    else:
        aadj = a
        if tp:
            ttp = .94 * abs(tp) / tp
        else:
            ttp = 0
    sto = steer_centeralign(P, tp, aadj, ttp)
    return speed_appropriate_steer(P, sto, sx)


def traffic_navigation(os, sti):
    sto = sti
    c = min(os[4:32])
    cs = os.index(c)
    if not c: c = .0001
    if min(os[18:26]) < 7:
        sto += .5 / c
    if min(os[8:17]) < 7:
        sto -= .5 / c
    if cs == 17:
        sto += .1 / c
    elif cs == 18:
        sto -= .1 / c
    if .1 < os[17] < 40:
        sto += .01
    if .1 < os[18] < 40:
        sto -= .01
    return sto


def clutch_control(P, cli, sl, sx, sy):
    if abs(sx) < .1 and not cli:
        return 1
    clo = cli - .2
    clo += sl / P['clutchslip']
    clo += sy / P['clutchspin']
    return clo


def throttle_control(P, ai, ts, sx, sl, sy, ang, steer):
    ao = ai
    if ts < 0:
        tooslow = sx - ts
    else:
        if steer > P['fullstis']:
            ts = P['fullstmaxsx']
        else:
            okmaxspeed4steer = P['stst'] * steer * steer - P['st'] * steer + P['stC']
            ts = min(ts, okmaxspeed4steer)
        tooslow = ts - sx
    try:
        ao = 2 / (1 + math.exp(-tooslow)) - 1
    except:
        print "exp overflow:", -tooslow
        ao = -1

    ao -= abs(sl) * P['slipdec']
    spincut = P['spincutint'] - P['spincutslp'] * abs(sy)
    spincut = snakeoil.clip(spincut, P['spincutclip'], 1)
    ao *= spincut
    ww = abs(ang) / P['wwlim']
    wwcut = min(ww, .1)
    if ts > 0 and sx > 5:
        ao -= wwcut
    if ao > .8: ao = 1
    return ao


def brake_control(P, bi, sx, sy, ts, sk):
    bo = bi
    toofast = sx - ts
    if toofast <= 0:
        return 0

    bo = 1  # e se commento questo?
    if sk > P['seriousABS'] or sx < 0:
        bo = 0
    if sx < -.1 and ts > 0:
        bo += .05
    sycon = 1
    if sy:
        sycon = min(1, P['sycon2'] - P['sycon1'] * math.log(abs(sy)))
    return min(bo, sycon)


def iberian_skid(wsv, sx):
    speedps = sx / 3.6
    sxshouldbe = sum([[.3179, .3179, .3276, .3276][x] * wsv[x] for x in range(3)]) / 4.0
    return speedps - sxshouldbe


def skid_severity(P, wsv_list, sx):
    skid = 0
    avgws = sum(wsv_list) / 4
    if avgws:
        skid = P['skidsev1'] * sx / avgws - P['wheeldia']
    return skid


def car_might_be_stuck(sx, a, p):
    if p > 1.2 and a < -.5:
        return True
    if p < -1.2 and a > .5:
        return True
    if sx < 3:
        return True
    return False


def car_is_stuck(t, a, p, fwdtsen, ts):
    if fwdtsen > 5 and ts > 0:
        return False
    if abs(a) < .5 and abs(p) < 2 and ts > 0:
        return False
    if t < 100:
        return False
    return True


def learn_track(T, st, a, t, dfs):
    global secType
    global secBegin
    global secMagnitude
    global secWidth
    NOSTEER = 0.07
    T.laplength = max(dfs, T.laplength)
    if len(trackHistory) >= TRACKHISTORYMAX:
        trackHistory.pop(0)
    trackHistory.append(st)
    steer_sma = sum(trackHistory) / len(trackHistory)
    if abs(steer_sma) > NOSTEER:
        secType_now = abs(steer_sma) / steer_sma
        if secType != secType_now:
            T.sectionList.append(TrackSection(secBegin, dfs, secMagnitude, secWidth, 0))
            secMagnitude = 0
            secWidth = 0
            secType = secType_now
            secBegin = dfs
        secMagnitude += st
    else:
        if secType:
            T.sectionList.append(TrackSection(secBegin, dfs, secMagnitude, secWidth, 0))
            secMagnitude = 0
            secWidth = 0
            secType = 0
            secBegin = dfs
    if not secWidth and abs(a) < NOSTEER:
        secWidth = t[0] + t[-1]


def learn_track_final(T, dfs):
    global secType
    global secBegin
    global secMagnitude
    global secWidth
    global badness
    T.sectionList.append(TrackSection(secBegin, dfs, secMagnitude, secWidth, badness))


def drive(c, T, tick):
    S, R, P = c.S.d, c.R.d, c.P
    global target_speed
    global lap
    global prev_distance_from_start
    global learn_final
    global badness
    # badness = S['damage'] - badness
    skid = skid_severity(P, S['wheelSpinVel'], S['speedX'])
    # if skid > 1:
    #     badness += 15

    if car_might_be_stuck(S['speedX'], S['angle'], S['trackPos']):
        S['stucktimer'] = (S['stucktimer'] % 400) + 1
        if car_is_stuck(S['stucktimer'], S['angle'],
                        S['trackPos'], S['track'][9], target_speed):
            # badness += 100
            R['brake'] = 0
            if target_speed > 0:
                target_speed = -40
            else:
                target_speed = 40
    else:
        S['stucktimer'] = 0

    # if S['z'] > 4:
    #     badness += 20
    infleX, infleA, straightness = track_sensor_analysis(S['track'], S['angle'])
    if target_speed > 0:
        # if c.stage:
        if not S['stucktimer']:
            target_speed = speed_planning(P, S['track'], S['speedX'], S['speedY'], R['steer'], S['angle'], infleX,
                                          infleA)
        target_speed += jump_speed_adjustment(S['z'])
        # if c.stage > 1:
        # ---- target_speed += traffic_speed_adjustment( S['opponents'], S['speedX'], target_speed, S['track'])
        target_speed *= damage_speed_adjustment(S['damage'])
    # else:
    #     print 'c.stage never equal to zero'
    #     if lap > 1 and T.usable_model:
    #         target_speed = speed_planning(P, S['distFromStart'], S['track'], S['trackPos'], S['speedX'], S['speedY'], R['steer'], S['angle'], infleX, infleA)
    #         target_speed *= damage_speed_adjustment(S['damage'])
    #     else:
    #         target_speed = 50
    target_speed = min(target_speed, 333)
    # caution = 1
    # if T.usable_model:
    #     print 'model always not usable'
    #     snow = T.section_in_now(S['distFromStart'])
    #     snext = T.section_ahead(S['distFromStart'])
    #     if snow:
    #         if snow.badness > 100: caution = .80
    #         if snow.badness > 1000: caution = .65
    #         if snow.badness > 10000: caution = .4
    #         if snext:
    #             if snow.end - S['distFromStart'] < 200:
    #                 if snext.badness > 100: caution = .90
    #                 if snext.badness > 1000: caution = .75
    #                 if snext.badness > 10000: caution = .5
    # target_speed *= caution
    # if T.usable_model or c.stage > 1:
    if abs(S['trackPos']) > 1:
        s = steer_centeralign(P, S['trackPos'], S['angle'])
        # badness += 1
    else:
        s = steer_reactive(P, S['trackPos'], S['angle'], S['track'], S['speedX'], infleA, straightness)
    # else:
    #     print 'stage never smaller than 1'
    #     s = steer_centeralign(P, R['steer'], S['trackPos'], S['angle'])
    # if S['stucktimer'] and S['distRaced'] > 20:
    #     if target_speed < 0:
    #         R['steer'] = -S['angle']
    # if c.stage > 1:
    R['steer'] = s
    if target_speed < 0:
        # ------ target_speed *= snakeoil.clip(S['opponents'][0] / 20, .1, 1)
        # ------ target_speed *= snakeoil.clip(S['opponents'][35] / 20, .1, 1)
        if S['stucktimer'] and S['distRaced'] > 20:
            R['steer'] = -S['angle']
    # else:
    #     R['steer'] = speed_appropriate_steer(P, traffic_navigation(S['opponents'], R['steer']), S['speedX'] + 50)

    if not S['stucktimer']:
        target_speed = abs(target_speed)
    slip = find_slip(S['wheelSpinVel'])
    R['accel'] = throttle_control(P, R['accel'], target_speed, S['speedX'], slip, S['speedY'], S['angle'], R['steer'])
    if R['accel'] < .01:
        R['brake'] = brake_control(P, R['brake'], S['speedX'], S['speedY'], target_speed, skid)
    else:
        R['brake'] = 0
    R['gear'], R['clutch'] = automatic_transimission(P, S['gear'], R['clutch'], S['rpm'], S['speedX'], target_speed,
                                                     tick)
    R['clutch'] = clutch_control(P, R['clutch'], slip, S['speedX'], S['speedY'])
    # if S['distRaced'] < S['distFromStart']:
    #     lap = 0
    # if prev_distance_from_start > S['distFromStart'] and abs(S['angle']) < .1:
    #     lap += 1
    # prev_distance_from_start = S['distFromStart']
    # if not lap:
    #     T.laplength = max(S['distFromStart'], T.laplength)
    # elif lap == 1 and not T.usable_model:
    #     print "learning track"
    #     learn_track(T, R['steer'], S['angle'], S['track'], S['distFromStart'])
    # elif c.stage == 3:
    #     pass
    # else:
    #     print 'i\'m going to set usable model to true'
    #     if not learn_final:
    #         learn_track_final(T, T.laplength)
    #         T.post_process_track()
    #         learn_final = True
    #     if T.laplength:
    #         properlap = S['distRaced'] / T.laplength
    #     else:
    #         properlap = 0
    #     if c.stage == 0 and lap < 4:
    #         T.record_badness(badness, S['distFromStart'])
    S['targetSpeed'] = target_speed
    target_speed = 70
    # badness = S['damage']
    return


def initialize_car(c):
    R = c.R.d
    R['gear'] = 1
    R['steer'] = 0
    R['brake'] = 0
    R['clutch'] = 1
    R['accel'] = 1
    R['focus'] = 0
    c.respond_to_server()


def main(P, port, m=1):
    global lap
    T = Track()
    C = snakeoil.Client(P=P, port=port)
    lastLapTime = []
    damages = []
    distance = []

    positions_out = []
    times_out = 0
    max_out = 0
    out = False

    lastLapTime.append(0)

    if C.stage == 1 or C.stage == 2:
        try:
            T.load_track(C.trackname)
        except:
            print "Could not load the track: %s" % C.trackname
            sys.exit()
        print "Track loaded!"

    initialize_car(C)
    C.respond_to_server()
    C.S.d['stucktimer'] = 0
    C.S.d['targetSpeed'] = 0
    # gear = 0
    lap = 1
    for step in xrange(C.maxSteps, 0, -1):
        C.get_servers_input()
        drive(C, T, step)
        C.respond_to_server()

        # print C.S.d['rpm']
        #
        # if gear != C.S.d['gear']:
        #     print 'Cambio marcia da', gear, 'a', C.S.d['gear']
        #     gear = C.S.d['gear']

        if lap > 1:
            tp = abs(C.S.d['trackPos'])
            # print tp
            if tp >= 0.95:
                times_out += 1
                out = True
                if tp > max_out:
                    max_out = tp
            if tp < 0.95 and out:
                out = False
                if times_out > 30:
                    # print "out", [max_out, times_out]
                    positions_out.append([max_out, times_out])
                times_out = 0
                max_out = 0

        if (lastLapTime[len(lastLapTime) - 1] != C.S.d['lastLapTime']):
            lap += 1
            lastLapTime.append(C.S.d['lastLapTime'])
            damages.append(C.S.d['damage'])
            distance.append(C.S.d['distRaced'])
            if (len(lastLapTime) == 5) and m == 1:
                C.R.d['meta'] = 1
                C.respond_to_server()
                C.shutdown()

                return lastLapTime, damages, distance, positions_out, port

        if C.S.d['damage'] > 8000 or C.S.d['curLapTime'] > 200:
            damages.append(50000)
            C.R.d['meta'] = 1
            C.respond_to_server()
            C.shutdown()
            return lastLapTime, damages, distance, positions_out, port

    if not C.stage:
        T.write_track(C.trackname)


if __name__ == "__main__":
    port = 3005
    print port
    par = {'seriousABS': 18.572278222386533, 'safeatanyspeed': 0.002060391388847591, 'ignoreinfleA': 1.8618974032266842,
           'carmaxvisib': 2.996281012911541, 'sxappropriatest2': 0.6915872114893653, 'clutchspin': 65.76649224108006,
           'fullstis': 1.392560073959177, 'backontracksx': 105.82341286599376, 'offroad': 1.5595908595638819,
           'consideredstr8': 0.01490247151823319, 'wheeldia': 0.25776785651051376, 'slipdec': 0.008427959807821133,
           'fullstmaxsx': 6.842454237804415, 'st': 757.0689003343408, 'carmin': 53.72284196802518,
           'sxappropriatest1': 19.92997091677259, 'oksyp': 10.266787818551606, 'wwlim': 3.309819636861068,
           'sycon2': 1.175293684910017, 'spincutclip': 0.05952907186871913, 's2cen': 0.35858001046562926,
           'sycon1': 0.6014722357964999, 'brakingpacefast': 1.7651811793889665, 'backward': 1.982552195440424,
           'obviousbase': 55.23196014694696, 'spincutint': 2.700169505538187, 'stC': 416.61294427108675,
           'stst': 175.6662371794496, 'damage': 4.514608172374178, 'timesout': 0.7339606012009418,
           'spincutslp': 0.06366452905665826, 'brakingpaceslow': 3.0543067018137866, 's2sen': 1.6284672741342163,
           'obvious': 2.086033855908092, 'str8thresh': 0.04456850252159655, 'steer2edge': 0.7690023210954672,
           'clutchslip': 37.04190793722127, 'skidsev1': 0.7400827508572864}
    par2 = {'seriousABS': 8.538960594587435, 'safeatanyspeed': 0.0009124314567578924,
            'ignoreinfleA': 1.8747226772296302, 'carmaxvisib': 3.251657311084868,
            'sxappropriatest2': 0.5309963421274929, 'clutchspin': 50.407362431673754, 'fullstis': 1.3937850889377525,
            'backontracksx': 83.96695571974224, 'offroad': 1.111041132955934, 'consideredstr8': 0.009199174756372353,
            'wheeldia': 1.4195173592741637, 'slipdec': 0.015297406721840007, 'fullstmaxsx': 6.3780769723428135,
            'st': 477.603200464589, 'carmin': 38.060421056328565, 'sxappropriatest1': 11.469580946666719,
            'oksyp': 26.007154561059334, 'wwlim': 1.7747760385815512, 'sycon2': 0.31782510755235244,
            'spincutclip': 0.030995914445634362, 's2cen': 0.15588788046425536, 'sycon1': 0.9718537523893206,
            'brakingpacefast': 1.6861700923582466, 'backward': 1.690672095529629, 'obviousbase': 33.32820560589409,
            'spincutint': 1.6870493065975387, 'stC': 394.9831561238934, 'stst': 304.7881819509628,
            'damage': 7.23082675755309, 'timesout': 0.0007137635525768515, 'spincutslp': 0.0534896845945276,
            'brakingpaceslow': 2.5491074993054172, 's2sen': 4.998168372819903, 'obvious': 2.27394578553118,
            'str8thresh': 0.14174616825119313, 'steer2edge': 1.2755583692814547, 'clutchslip': 75.03208006918459,
            'skidsev1': 0.5329530665949473}
    par3 = {'seriousABS': 10.383014412859051, 'safeatanyspeed': 0.0006430941500266245,
            'ignoreinfleA': 1.6928116239983326, 'carmaxvisib': 3.745161315707878,
            'sxappropriatest2': 0.5319992642549535, 'clutchspin': 59.97668980026459, 'fullstis': 1.2390314701653942,
            'backontracksx': 52.913464932476785, 'offroad': 0.812812978456645, 'consideredstr8': 0.011319004681476673,
            'wheeldia': 1.4542272036921977, 'slipdec': 0.014454091254072175, 'fullstmaxsx': 6.302286948510615,
            'st': 496.22346031115745, 'carmin': 49.27556074471944, 'sxappropriatest1': 11.414838221013394,
            'oksyp': 26.48176640918227, 'wwlim': 2.8312057482591486, 'sycon2': 0.3203248218579146,
            'spincutclip': 0.04262206879878136, 's2cen': 0.15434478990357992, 'sycon1': 0.9868537903171561,
            'brakingpacefast': 1.7025469098266375, 'backward': 0.5007674360703409, 'obviousbase': 32.76996950311814,
            'spincutint': 1.697467300318605, 'stC': 425.02271528245063, 'stst': 206.7896605534902,
            'damage': 8.917954706913461, 'timesout': 0.00029602843981267135, 'spincutslp': 0.02964549529861994,
            'brakingpaceslow': 2.255305358819442, 's2sen': 4.940808490166029, 'obvious': 2.282192506204596,
            'str8thresh': 0.1421234296364856, 'steer2edge': 1.6134161813923473, 'clutchslip': 90.43910909320124,
            'skidsev1': 0.5009745158332416}
    par4 = {'seriousABS': 35.24963482788227, 'safeatanyspeed': 0.0012476122707033945,
            'ignoreinfleA': 0.3822746167252149, 'carmaxvisib': 3.4967186513680124,
            'sxappropriatest2': 0.6007935995196417, 'clutchspin': 28.762118771028234, 'fullstis': 0.842419904907317,
            'backontracksx': 94.12553741011524, 'offroad': 1.1054006480663205, 'consideredstr8': 0.0037122125166424744,
            'wheeldia': 0.35820406367689556, 'slipdec': 0.007479270430413779, 'fullstmaxsx': 19.817712968950094,
            'st': 494.7335347622853, 'carmin': 57.576926370054736, 'sxappropriatest1': 16.423887890626883,
            'oksyp': 11.227521879806217, 'wwlim': 1.3461144779941618, 'sycon2': 0.6749112134503027,
            'spincutclip': 0.11820255880934134, 's2cen': 0.6457643325081968, 'sycon1': 0.19287732533152435,
            'brakingpacefast': 1.0570597404663955, 'backward': 2.203201922561544, 'obviousbase': 74.86481960259077,
            'spincutint': 1.505517755619526, 'stC': 312.02763813952834, 'stst': 610.9199606273635,
            'damage': 4.720368499021208, 'timesout': 0.0013355484919079913, 'spincutslp': 0.03865061786937338,
            'brakingpaceslow': 3.250333438244792, 's2sen': 1.2224656119462207, 'obvious': 1.82922735342368,
            'str8thresh': 0.17878489779914272, 'steer2edge': 1.083050028546696, 'clutchslip': 128.88942140324906,
            'skidsev1': 0.2605611615741265}
    par5 = {'seriousABS': 35.96008406734591, 'safeatanyspeed': 0.0014806609950232185,
            'ignoreinfleA': 0.3952343913613903, 'carmaxvisib': 2.8549341423109036,
            'sxappropriatest2': 0.9101287464349838, 'clutchspin': 30.366504223044114, 'fullstis': 1.3641657497721758,
            # 'backontracksx': 69.11444242102745,
            'offroad': 0.4047106159236165, 'consideredstr8': 0.0030243811398615846,
            'wheeldia': 0.9289017855835372, 'slipdec': 0.005530076084552113, 'fullstmaxsx': 20.0708188626746,
            'st': 329.4392839619138, 'carmin': 50.615319404295114, 'sxappropriatest1': 23.744187483409963,
            'oksyp': 10.17992860655802, 'wwlim': 3.8970675172700746, 'sycon2': 0.6392287315457917,
            'spincutclip': 0.11665222445240457, 's2cen': 0.8200363031681391, 'sycon1': 0.19452943678385415,
            'brakingpacefast': 1.5224721402034023, 'backward': 1.460648093706204, 'obviousbase': 83.82938288585149,
            'spincutint': 1.7106922509044515, 'stC': 449.7092844805364, 'stst': 805.6249548592508,
            'damage': 7.951404912539468, 'timesout': 0.0009390033434325899, 'spincutslp': 0.03075895537245576,
            'brakingpaceslow': 3.812361668977617, 's2sen': 2.579334163417181, 'obvious': 1.2423628927358195,
            'str8thresh': 0.180931110454203, 'steer2edge': 1.3855757303789364, 'clutchslip': 96.14902282246956,
            'skidsev1': 0.17298500834395264}

    omega = {"seriousABS": 30.917313675035082, "dnsh3rpm": 2277.3748124890767, "dnsh5rpm": 5161.008529255238, "consideredstr8": 0.014422763716695626, "upsh6rpm": 4641.849598646489, "dnsh2rpm": 4083.7460965865716, "obviousbase": 91.56323901577467, "stst": 646.8840720470463, "upsh3rpm": 3617.9543837958627, "str8thresh": 0.046064523522487126, "clutchslip": 73.7071618881323, "safeatanyspeed": 0.0016737414663727987, "upsh4rpm": 10084.914268381892, "offroad": 0.4830693886271663, "fullstmaxsx": 28.626081603738953, "wwlim": 5.450207901757214, "spincutclip": 0.09160353424897875, "dnsh1rpm": 2025.0389080699022, "obvious": 1.8341497210854247, "backontracksx": 73.17177848544353, "upsh2rpm": 7829.607462662457, "clutchspin": 25.941154979343406, "fullstis": 1.2734285158250205, "brake": 0.00013612297181159191, "carmin": 35.59853750218664, "carmaxvisib": 2.7670297838796625, "oksyp": 0.0220715793152442, "spincutslp": 0.03176100234699471, "sycon2": 1.0478499278186009, "s2cen": 0.592852636508848, "sycon1": 0.31201996681216904, "upsh5rpm": 11673.407335364689, "stC": 165.06076012234882, "slipdec": 0.01072623479463959, "sxappropriatest1": 15.142023248780777, "sortofontrack": 1.9257910090979415, "sxappropriatest2": 0.7124374626647256, "skidsev1": 0.5979255478875778, "ignoreinfleA": 10.294684912584234, "wheeldia": 0.9635012405454104, "brakingpacefast": 1.4128425367853756, "sensang": -1.5764557788683555, "spincutint": 2.627619163570864, "st": 429.9001162693834, "brakingpaceslow": 2.6559009390624877, "s2sen": 3.729780318500916, "pointingahead": 2.9657004097086963, "steer2edge": 1.5286627573670089, "backward": 1.1948757776299521, "dnsh4rpm": 2879.0513770796924}
    main(omega, port, m=0)

####### snakeoil (5laps) #######
# snakeoil: (on 5 laps)
# speedway_n1  45.52s
# forza        1.52.64s  112.64s
# corkscrew    1.54.60s  114.60s
# alpine2      1.54.17s  114.17s
# E-track      1.53.41s
# E-track4     2.03.15s  123.15

######### dt7 (5laps) ##########
# speedway_n1  44.27s
# forza        1.50.19s  110.19s
# corkscrew    1.51.15s  111.15s
# alpine2      1.57.41s  117.41s
# E-track

############# BEST #############
# speedway_n1  31.35s
# forza        1.17.90s  77.90s
# corkscrew    1.08.79s  68.79s
# alpine2      1.19.03s  79.03s
# E-track      1.14.88s  74.88s
# Brondehach   1.06.80s  66.80s

# pso(gen=n_gen, omega=0.7298, eta1=2.05, eta2=2.05, max_vel=0.5, variant=5, neighb_type=2, memory=True,seed=1234)
# Fitness evaluation 562 completed, time: 7 -- 0
# {'seriousABS': 10.70716876752739, 'safeatanyspeed': 0.0009277850069909176, 'ignoreinfleA': 1.6289360945069244, 'carmaxvisib': 3.1660836709656612, 'sxappropriatest2': 0.4622756356957972, 'clutchspin': 33.39367345379378, 'fullstis': 1.3937850889377525, 'backontracksx': 101.05463527986095, 'offroad': 1.148153689702724, 'consideredstr8': 0.009116589307880417, 'wheeldia': 1.3887374513717305, 'slipdec': 0.01871308650466206, 'fullstmaxsx': 6.708350159043171, 'st': 506.47943127636853, 'carmin': 41.36151277099982, 'sxappropriatest1': 13.619593554814497, 'oksyp': 24.669646731504795, 'wwlim': 3.567112643922968, 'sycon2': 0.3000717595299429, 'spincutclip': 0.07111358459158307, 's2cen': 0.15535502475571225, 'sycon1': 0.9337488130387825, 'brakingpacefast': 1.5532003127273126, 'backward': 1.584118428211973, 'obviousbase': 46.006574578302605, 'spincutint': 2.2726809753797346, 'stC': 382.9493761829953, 'stst': 306.4458810073181, 'damage': 4.967076187418524, 'timesout': 0.0020530598384111095, 'spincutslp': 0.0768814978966536, 'brakingpaceslow': 3.4749032967571134, 's2sen': 4.944295780389059, 'obvious': 2.222114746693038, 'str8thresh': 0.11353839876300874, 'steer2edge': 1.4298800345206129, 'clutchslip': 80.81723018662953, 'skidsev1': 0.4645880363441554}
# lastLapTime--->  44.844  --  95.982  --  98.716
# damages--->  0.0  --  29.0  --  0.0
# times out---> [[1.31111, 60], [1.03639, 41]]
# times out---> [[1.42482, 63], [4.61086, 224], [1.90398, 93], [0.979152, 48], [1.46087, 137], [1.00446, 63]]
# times out---> [[1.00747, 28], [0.993795, 36], [0.960132, 26]]
# damage: 4.967076187418524 out 0.0020530598384111095
# fitness---> 245.38044477229005
#
# Fitness evaluation 2825 completed, time: 6 -- 0
# {'seriousABS': 8.538960594587435, 'safeatanyspeed': 0.0009124314567578924, 'ignoreinfleA': 1.8747226772296302, 'carmaxvisib': 3.251657311084868, 'sxappropriatest2': 0.5309963421274929, 'clutchspin': 50.407362431673754, 'fullstis': 1.3937850889377525, 'backontracksx': 83.96695571974224, 'offroad': 1.111041132955934, 'consideredstr8': 0.009199174756372353, 'wheeldia': 1.4195173592741637, 'slipdec': 0.015297406721840007, 'fullstmaxsx': 6.3780769723428135, 'st': 477.603200464589, 'carmin': 38.060421056328565, 'sxappropriatest1': 11.469580946666719, 'oksyp': 26.007154561059334, 'wwlim': 1.7747760385815512, 'sycon2': 0.31782510755235244, 'spincutclip': 0.030995914445634362, 's2cen': 0.15588788046425536, 'sycon1': 0.9718537523893206, 'brakingpacefast': 1.6861700923582466, 'backward': 1.690672095529629, 'obviousbase': 33.32820560589409, 'spincutint': 1.6870493065975387, 'stC': 394.9831561238934, 'stst': 304.7881819509628, 'damage': 7.23082675755309, 'timesout': 0.0007137635525768515, 'spincutslp': 0.0534896845945276, 'brakingpaceslow': 2.5491074993054172, 's2sen': 4.998168372819903, 'obvious': 2.27394578553118, 'str8thresh': 0.14174616825119313, 'steer2edge': 1.2755583692814547, 'clutchslip': 75.03208006918459, 'skidsev1': 0.5329530665949473}
# lastLapTime--->  43.57  --  93.726  --  97.568
# damages--->  0.0  --  18.0  --  0.0
# times out---> []
# times out---> [[4.61855, 255], [1.46072, 170]]
# times out---> [[1.09194, 44], [1.04266, 48]]
# damage: 7.23082675755309 out 0.0007137635525768515
# fitness---> 237.3533418973422
#
# Fitness evaluation 7570 completed, time: 6 -- 1
# {'seriousABS': 35.96008406734591, 'safeatanyspeed': 0.0014806609950232185, 'ignoreinfleA': 0.3952343913613903, 'carmaxvisib': 2.8549341423109036, 'sxappropriatest2': 0.9101287464349838, 'clutchspin': 30.366504223044114, 'fullstis': 1.3641657497721758, 'backontracksx': 69.11444242102745, 'offroad': 0.4047106159236165, 'consideredstr8': 0.0030243811398615846, 'wheeldia': 0.9289017855835372, 'slipdec': 0.005530076084552113, 'fullstmaxsx': 20.0708188626746, 'st': 329.4392839619138, 'carmin': 50.615319404295114, 'sxappropriatest1': 23.744187483409963, 'oksyp': 10.17992860655802, 'wwlim': 3.8970675172700746, 'sycon2': 0.6392287315457917, 'spincutclip': 0.11665222445240457, 's2cen': 0.8200363031681391, 'sycon1': 0.19452943678385415, 'brakingpacefast': 1.5224721402034023, 'backward': 1.460648093706204, 'obviousbase': 83.82938288585149, 'spincutint': 1.7106922509044515, 'stC': 449.7092844805364, 'stst': 805.6249548592508, 'damage': 7.951404912539468, 'timesout': 0.0009390033434325899, 'spincutslp': 0.03075895537245576, 'brakingpaceslow': 3.812361668977617, 's2sen': 2.579334163417181, 'obvious': 1.2423628927358195, 'str8thresh': 0.180931110454203, 'steer2edge': 1.3855757303789364, 'clutchslip': 96.14902282246956, 'skidsev1': 0.17298500834395264}
# lastLapTime--->  44.264  --  88.108  --  97.412
# damages--->  0.0  --  0.0  --  0.0
# times out---> []
# times out---> [[1.29363, 150], [1.54658, 104]]
# times out---> [[1.00197, 30]]
# damage: 7.951404912539468 out 0.0009390033434325899
# fitness---> 229.78400000000002
