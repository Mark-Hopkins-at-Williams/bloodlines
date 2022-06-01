import numpy as np
import os
import pygame as pg
import threading
from bayes import BayesianNetwork
from junction import BeliefPropagation
from junction import build_junction_tree_for_bayes_net
from genetics import Male, Female, create_family_bayes_net
from graphics import CartesianPlane, AnimatedSprite, PlayButton
from graphics import RainbowOverlay, FamilyMemberWidget


class VictoriaBloodlines:
    def __init__(self):
        self.plane = CartesianPlane(30, 21, 1000, 700, bg_image_file="images/royals.png")
        family = create_victoria_lineage()
        coords = victoria_lineage_coordinates()
        self.family_widgets = []
        for member in family:
            x, y = coords[member.get_name()]
            widget = FamilyMemberWidget(x, y, member)
            self.family_widgets.append(widget)
            self.plane.add_widget(widget)
        self.overlay = RainbowOverlay(15.18, 10.84)
        self.plane.add_sprite(self.overlay)
        self.button = PlayButton(17.4, 3.5, scale=2.0)
        self.plane.add_sprite(self.button)
        self.bnet = create_family_bayes_net(family)
        self.jtree = build_junction_tree_for_bayes_net(self.bnet)
        self.running_bp = False

    def harvest_evidence(self):
        evidence = {}
        for widget in self.family_widgets:
            if widget.get_color() == (255, 0, 0):
                evidence[f'P_{widget.get_name()}'] = '+'
        return evidence

    def start(self):
        going = True
        clock = pg.time.Clock()
        while going:
            clock.tick(60)
            if self.running_bp or self.overlay.current_cell != 0:
                self.overlay.flip()
            else:
                self.overlay.current_cell = 0
            for event in pg.event.get():
                self.plane.notify(event)
                if event.type == pg.QUIT:
                    going = False
            if self.button.down and not self.running_bp:
                evidence = self.harvest_evidence()
                try:
                    t1 = threading.Thread(target=self.run_belief_propagation, args=(evidence,))
                    t1.start()
                except Exception:
                    print("Error: unable to start thread")
            self.plane.refresh()

    def run_belief_propagation(self, evidence):
        self.running_bp = True
        bp = BeliefPropagation(self.jtree)
        bp.run(evidence)
        marginals = bp.get_marginals()
        for person in self.family_widgets:
            if person.get_color() != (255, 0, 0):
                try:
                    cond_dist = marginals[f'G_{person.get_name()}']
                    if person.get_sex() == "female":
                        prob_mass = (cond_dist.get_value({f'G_{person.get_name()}': 'xX'}) +
                                     cond_dist.get_value({f'G_{person.get_name()}': 'XX'}))
                    else:
                        prob_mass = cond_dist.get_value({f'G_{person.get_name()}': 'Xy'})
                    person.current_color = (255, 255 - 140 * prob_mass, 255 - 250 * prob_mass)
                except KeyError:
                    pass
        self.running_bp = False


def create_victoria_lineage():
    # Generation 1
    victoria_of_saxe_coburg = Female(name="victoria_of_saxe_coburg")
    edward_duke_of_kent = Male(name="edward_duke_of_kent")
    # Generation 2
    queen_victoria = Female(name="queen_victoria", mother=victoria_of_saxe_coburg, father=edward_duke_of_kent)
    albert = Male(name="albert")
    # Generation 3
    iii_victoria = Female(mother=queen_victoria, father=albert, name="iii_victoria")
    royal_3_2 = Male(name="royal_3_2")
    edward_vii = Male(mother=queen_victoria, father=albert, name="edward_vii")
    royal_3_4 = Female(name="royal_3_4")
    alice = Female(mother=queen_victoria, father=albert, name="alice")
    louis_of_hesse = Male(name="louis_of_hesse")
    alfred = Male(mother=queen_victoria, father=albert, name="alfred")
    helena = Female(mother=queen_victoria, father=albert, name="helena")
    louise = Female(mother=queen_victoria, father=albert, name="louise")
    arthur = Male(mother=queen_victoria, father=albert, name="arthur")
    iii_leopold = Male(mother=queen_victoria, father=albert, name="iii_leopold")
    royal_3_12 = Female(name="royal_3_12")
    iii_beatrice = Female(mother=queen_victoria, father=albert, name="iii_beatrice")
    iii_henry = Male(name="iii_henry")
    # Generation 4
    wilhelm = Male(mother=iii_victoria, father=royal_3_2, name="wilhelm")
    sophie_of_greece = Female(mother=iii_victoria, father=royal_3_2, name="sophie_of_greece")
    george_v = Male(mother=royal_3_4, father=edward_vii, name="george_v")
    royal_4_4 = Female(name="royal_4_4")
    royal_4_5 = Male(name="royal_4_5")
    royal_4_6 = Female(mother=alice, father=louis_of_hesse, name="royal_4_6")
    royal_4_7 = Female(mother=alice, father=louis_of_hesse, name="royal_4_7")
    irene = Female(mother=alice, father=louis_of_hesse, name="irene")
    iv_henry = Male(name="iv_henry")
    frederick = Male(mother=alice, father=louis_of_hesse, name="frederick")
    alexandra = Female(mother=alice, father=louis_of_hesse, name="alexandra")
    czar_nicholas = Male(name="czar_nicholas")
    royal_4_13 = Female(mother=alice, father=louis_of_hesse, name="royal_4_13")
    royal_4_14 = Male(name="royal_4_14")
    alice_of_athlone = Female(mother=royal_3_12, father=iii_leopold, name="alice_of_athlone")
    royal_4_16 = Male(mother=royal_3_12, father=iii_leopold, name="royal_4_16")
    royal_4_17 = Male(mother=iii_beatrice, father=iii_henry, name="royal_4_17")
    alfonso_xiii = Male(name="alfonso_xiii")
    iv_eugenie = Female(mother=iii_beatrice, father=iii_henry, name="iv_eugenie")
    iv_leopold = Male(mother=iii_beatrice, father=iii_henry, name="iv_leopold")
    maurice = Male(mother=iii_beatrice, father=iii_henry, name="maurice")
    # Generation 5
    royal_5_1 = Male(mother=royal_4_4, father=george_v, name="royal_5_1")
    george_vi = Male(mother=royal_4_4, father=george_v, name="george_vi")
    royal_5_3 = Female(name="royal_5_3")
    royal_5_4 = Female(mother=royal_4_6, father=royal_4_5, name="royal_5_4")
    royal_5_5 = Female(mother=royal_4_6, father=royal_4_5, name="royal_5_5")
    royal_5_6 = Male(mother=royal_4_6, father=royal_4_5, name="royal_5_6")
    royal_5_7 = Male(mother=royal_4_6, father=royal_4_5, name="royal_5_7")
    waldemar = Male(mother=irene, father=iv_henry, name="waldemar")
    sigmund_of_prussia = Male(mother=irene, father=iv_henry, name="sigmund_of_prussia")
    v_henry = Male(mother=irene, father=iv_henry, name="v_henry")
    olga = Female(mother=alexandra, father=czar_nicholas, name="olga")
    tatiana = Female(mother=alexandra, father=czar_nicholas, name="tatiana")
    marie = Female(mother=alexandra, father=czar_nicholas, name="marie")
    anastasia = Female(mother=alexandra, father=czar_nicholas, name="anastasia")
    alexis = Male(mother=alexandra, father=czar_nicholas, name="alexis")
    royal_5_16 = Male(name="royal_5_16")
    royal_5_17 = Female(mother=alice_of_athlone, father=royal_4_14, name="royal_5_17")
    rupert = Male(mother=alice_of_athlone, father=royal_4_14, name="rupert")
    royal_5_19 = Male(mother=alice_of_athlone, father=royal_4_14, name="royal_5_19")
    alfonso = Male(mother=iv_eugenie, father=alfonso_xiii, name="alfonso")
    royal_5_21 = Male(mother=iv_eugenie, father=alfonso_xiii, name="royal_5_21")
    royal_5_22 = Female(mother=iv_eugenie, father=alfonso_xiii, name="royal_5_22")
    royal_5_23 = Female(mother=iv_eugenie, father=alfonso_xiii, name="royal_5_23")
    gonzalo = Male(mother=iv_eugenie, father=alfonso_xiii, name="gonzalo")
    v_juan = Male(mother=iv_eugenie, father=alfonso_xiii, name="v_juan")
    maria = Female(name="maria")
    # Generation 6
    margaret = Female(mother=royal_5_3, father=george_vi, name="margaret")
    elizabeth_ii = Female(mother=royal_5_3, father=george_vi, name="elizabeth_ii")
    philip = Male(mother=royal_5_4, name="philip")
    royal_6_4 = Male(mother=royal_5_17, father=royal_5_16, name="royal_6_4")
    royal_6_5 = Female(mother=royal_5_17, father=royal_5_16, name="royal_6_5")
    royal_6_6 = Female(mother=royal_5_17, father=royal_5_16, name="royal_6_6")
    royal_6_7 = Female(mother=royal_5_22, name="royal_6_7")
    royal_6_8 = Male(mother=royal_5_22, name="royal_6_8")
    royal_6_9 = Female(mother=royal_5_22, name="royal_6_9")
    royal_6_10 = Female(mother=royal_5_23, name="royal_6_10")
    juan_carlos = Male(mother=maria, father=v_juan, name="juan_carlos")
    sophia_of_greece = Female(name="sophia_of_greece")
    # Generation 7
    charles = Male(mother=elizabeth_ii, father=philip, name="charles")
    anne = Female(mother=elizabeth_ii, father=philip, name="anne")
    andrew = Male(mother=elizabeth_ii, father=philip, name="andrew")
    edward = Male(mother=elizabeth_ii, father=philip, name="edward")
    elena = Female(mother=sophia_of_greece, father=juan_carlos, name="elena")
    cristina = Female(mother=sophia_of_greece, father=juan_carlos, name="cristina")
    filipe = Male(mother=sophia_of_greece, father=juan_carlos, name="filipe")
    # Generation 8
    william = Male(father=charles, name="william")
    harry = Male(father=charles, name="harry")
    peter = Male(mother=anne, name="peter")
    zara = Female(mother=anne, name="zara")
    viii_beatrice = Female(father=andrew, name="viii_beatrice")
    viii_eugenie = Female(father=andrew, name="viii_eugenie")
    felipe = Male(mother=elena, name="felipe")
    viii_victoria = Female(mother=elena, name="viii_victoria")
    viii_juan = Male(mother=cristina, name="viii_juan")
    pablo = Male(mother=cristina, name="pablo")
    miguel = Male(mother=cristina, name="miguel")
    family = [victoria_of_saxe_coburg, edward_duke_of_kent, queen_victoria, albert,
              iii_victoria, royal_3_2, edward_vii, royal_3_4, helena,
              alice, helena, louise, royal_3_12, iii_beatrice,
              louis_of_hesse, alfred, arthur, iii_leopold, iii_henry,
              sophie_of_greece, royal_4_4, royal_4_6, royal_4_7,
              irene, alexandra, royal_4_13, alice_of_athlone, iv_eugenie,
              wilhelm, george_v, royal_4_5, iv_henry, frederick, czar_nicholas,
              royal_4_14, royal_4_16, royal_4_17, alfonso_xiii, iv_leopold, maurice,
              royal_5_3, royal_5_4, royal_5_5, olga, tatiana, marie, anastasia,
              royal_5_17, royal_5_22, royal_5_23, maria,
              royal_5_1, george_vi, royal_5_6, royal_5_7, waldemar, sigmund_of_prussia,
              v_henry, alexis, royal_5_16, rupert, royal_5_19, alfonso, gonzalo,
              royal_5_21, v_juan, margaret, elizabeth_ii, royal_6_5, royal_6_6, royal_6_7,
              royal_6_9, royal_6_10, sophia_of_greece, philip, royal_6_4, royal_6_8,
              juan_carlos, anne, elena, cristina, charles, andrew, edward, filipe,
              zara, viii_beatrice, viii_eugenie, viii_victoria,
              william, harry, peter, felipe, viii_juan, pablo, miguel]
    return family


def victoria_lineage_coordinates():
    coord_map = {
        'victoria_of_saxe_coburg': (13.2, 19.85),
        'edward_duke_of_kent': (15.46, 19.85),
        'queen_victoria': (14.32, 17.62),
        'albert': (15.84, 17.64),
        'iii_victoria': (2.21, 15.43),
        'royal_3_2': (3.71, 15.43),
        'edward_vii': (5.06, 15.43),
        'royal_3_4': (6.62, 15.42),
        'alice': (12.49, 15.43),
        'louis_of_hesse': (13.98, 15.43),
        'alfred': (15.23, 15.42),
        'helena': (16.49, 15.42),
        'louise': (17.77, 15.42),
        'arthur': (18.95, 15.42),
        'iii_leopold': (20.5, 15.42),
        'royal_3_12': (22.02, 15.42),
        'iii_beatrice': (24.94, 15.42),
        'iii_henry': (26.46, 15.42),
        'wilhelm': (2.08, 13.21),
        'sophie_of_greece': (3.37, 13.2),
        'george_v': (4.82, 13.21),
        'royal_4_4': (6.37, 13.2),
        'royal_4_5': (7.39, 13.21),
        'royal_4_6': (8.44, 13.2),
        'royal_4_7': (9.41, 13.2),
        'irene': (10.62, 13.2),
        'iv_henry': (11.65, 13.21),
        'frederick': (12.96, 13.21),
        'alexandra': (15.04, 13.2),
        'czar_nicholas': (16.85, 13.21),
        'royal_4_13': (18.34, 13.2),
        'royal_4_14': (19.3, 13.21),
        'alice_of_athlone': (20.72, 13.2),
        'royal_4_16': (21.76, 13.21),
        'royal_4_17': (22.78, 13.21),
        'alfonso_xiii': (24.08, 13.21),
        'iv_eugenie': (25.7, 13.2),
        'iv_leopold': (27.07, 13.21),
        'maurice': (28.42, 13.21),
        'royal_5_1': (1.98, 10.56),
        'george_vi': (3.41, 10.56),
        'royal_5_3': (4.76, 10.54),
        'royal_5_4': (5.79, 10.54),
        'royal_5_5': (6.46, 10.54),
        'royal_5_6': (7.04, 10.56),
        'royal_5_7': (7.68, 10.56),
        'waldemar': (9.65, 10.56),
        'sigmund_of_prussia': (11, 10.56),
        'v_henry': (12.22, 10.56),
        'olga': (14.6, 10.54),
        'tatiana': (15.54, 10.54),
        'marie': (16.48, 10.54),
        'anastasia': (17.42, 10.54),
        'alexis': (18.27, 10.56),
        'royal_5_16': (19.54, 10.56),
        'royal_5_17': (20.34, 10.54),
        'rupert': (20.95, 10.56),
        'royal_5_19': (21.62, 10.56),
        'alfonso': (23.18, 10.56),
        'royal_5_21': (24.02, 10.56),
        'royal_5_22': (24.79, 10.54),
        'royal_5_23': (25.5, 10.54),
        'gonzalo': (26.2, 10.56),
        'v_juan': (27.22, 10.56),
        'maria': (28.33, 10.54),
        'margaret': (3.1, 7.7),
        'elizabeth_ii': (5, 7.7),
        'philip': (7.25, 7.7),
        'royal_6_4': (19.56, 7.7),
        'royal_6_5': (20.22, 7.7),
        'royal_6_6': (20.9, 7.7),
        'royal_6_7': (22.15, 7.7),
        'royal_6_8': (22.8, 7.7),
        'royal_6_9': (23.46, 7.7),
        'royal_6_10': (24.26, 7.7),
        'juan_carlos': (25.86, 7.7),
        'sophia_of_greece': (27.98, 7.7),
        'charles': (4.1, 5.04),
        'anne': (6.8, 5.02),
        'andrew': (9.5, 5.04),
        'edward': (11.35, 5.04),
        'elena': (25.65, 5.02),
        'cristina': (26.92, 5.02),
        'filipe': (28.2, 5.04),
        'william': (3.47, 2.68),
        'harry': (4.80, 2.68),
        'peter': (6.22, 2.68),
        'zara': (7.38, 2.64),
        'viii_beatrice': (8.78, 2.64),
        'viii_eugenie': (10.34, 2.64),
        'felipe': (23.19, 2.68),
        'viii_victoria': (24.5, 2.64),
        'viii_juan': (25.79, 2.68),
        'pablo': (26.91, 2.68),
        'miguel': (28.07, 2.68)
    }
    return coord_map


if __name__ == '__main__':
    pg.init()
    if not pg.font:
        print("Warning, fonts disabled")
    if not pg.mixer:
        print("Warning, sound disabled")
    pg.display.set_caption("Bloodlines")
    pg.mouse.set_visible(True)
    app = VictoriaBloodlines()
    app.start()