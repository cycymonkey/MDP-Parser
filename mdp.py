import antlr4
from gramLexer import gramLexer
from gramListener import gramListener
from gramParser import gramParser
import numpy as np
import random
import networkx as nx
import matplotlib.pyplot as plt
import click
import copy
import time


class MDP:
    def __init__(self):
        self.initial_state = None
        self.current_state = None
        self.states = {}
        self.actions = set()
        self.transitions = {}
        self.pos = None
        self.hist = []
        self.RL = None
        self.gamma = 1/2
        self.eps = 1
        self.precision = 0.01
        self.erreur = 0.01
        self.recompense = 0
        self.adversaire = None


    def presentation_suite(self, mode_auto):
        '''
        Presente à l'utilisateur la suite dans le MDP quand pas en mode auto
        En mode auto, chosisit l'etape suivante
        '''
        if not mode_auto :
            if None in self.transitions[self.current_state]: 
                print('Vous êtes sur un choix probabiliste. Appuyez sur Entrée pour continuer :')
            else : 
                display = []
                for e in self.transitions[self.current_state] :
                    display.append(e) 

                print(f'Veuillez faire un choix dans : {display}')
                return('')
        else :
            if self.RL : 
                a = self.adversaire[self.current_state]
            else :
                if None in self.transitions[self.current_state]: 
                    a = ''
                else :
                    a = random.choice(list(self.transitions[self.current_state].keys()))
            return(a)


    def algo_it_valeurs(self):
        r = copy.deepcopy(self.states)
        V_old = {key: 0 for key in self.states.keys()}
        V_new = copy.deepcopy(self.states)

        while np.linalg.norm(np.array(list(V_new.values())) - np.array(list(V_old.values()))) > self.eps :
            V_old = copy.deepcopy(V_new)
            for etat_init in self.transitions :
                max_somme, _ = self.recherche_action_somme(etat_init, V_new, r)
                V_new[etat_init] = max_somme
            
        adversaire = {etat : None for etat in self.states.keys()}  
        for etat in self.transitions:
            _, adversaire[etat] = self.recherche_action_somme(etat, V_new, r)
        
        return(V_new, adversaire)
    

    def recherche_action_somme(self, etat_init, V, r):
        max_somme = 0
        action_choisie = None

        for action in self.transitions[etat_init]:
            somme = r[etat_init]
            p = self.proba(etat_init, action)
            
            for etat_arrive in self.transitions[etat_init][action]:
                somme += self.gamma*p[etat_arrive]*V[etat_arrive]
            
            if somme>max_somme :
                max_somme = somme
                action_choisie = action

        return(max_somme, action_choisie)
    

    def proba(self, etat_init, action):
        somme = sum(self.transitions[etat_init][action].values())
        p = copy.deepcopy(self.transitions[etat_init][action])
        for k,v in p.items():
            p[k]  = v/somme
        return(p)
    

    def s_proba(self, a = None):
        '''
        Returns
        ----------
        somme : int 
            Somme des poids des etats possibles suivants
        somme_proba : dict
            Dictionnaire, la clé est un état et le contenu est la sa proba au tour suivant additionné à 
            celle de l'etat avant lui dans le dictionnaire.
        '''
        while a not in self.transitions[self.current_state]:
            print(f"{a} n'est pas dans {list(self.transitions[self.current_state].keys())}")
            a = input(f'choisir vraiment dans {list(self.transitions[self.current_state].keys())}')
        somme = 0
        somme_proba = {}
        for e in self.transitions[self.current_state][a].keys() :
            somme += self.transitions[self.current_state][a][e]
            somme_proba[e] = somme

        for cle in somme_proba.keys():
            somme_proba[cle] = somme_proba[cle] / somme
        return(somme, somme_proba)


    def prochain_etat(self, somme_proba):
        '''
        Parameters
        ----------
        somme_proba : dict
            Dictionnaire, la clé est un état et le contenu est la sa proba au tour suivant additionné à 
            celle de l'etat avant lui dans le dictionnaire.

        Returns
        ----------
        cle : str
            Prochain etat
        '''
        aleatoire  = random.random()
        for cle, valeur in somme_proba.items() :
            if valeur > aleatoire : 
                return(cle)
    
    
    def avance(self, a = None, model_checked = False):
        '''
        Fais un pas dans le MDP ou MC
        '''
        _, somme_proba = self.s_proba(a)
        self.current_state = self.prochain_etat(somme_proba)
        if not model_checked :
            self.hist.append(self.current_state)
            self.recompense += self.states[self.current_state]
        return()            


    def initialisation(self):
       
        self.initial_state = click.prompt(f'choisir un etat de depart dans {list(self.states.keys())}', type=str)
        while self.initial_state not in self.states:
            print(f"{self.initial_state} n'est pas dans {list(self.states.keys())}")
            self.initial_state = click.prompt(f'choisir un etat de depart vraiment dans {list(self.states.keys())}', type=str)
        self.current_state = self.initial_state

        self.hist.append(self.current_state)
        self.recompense += self.states[self.current_state]

        nbr_tour = click.prompt('Combien de transitions voulez vous faire ? ', type=int)
        
        model_checked = click.prompt('Faire modele checking ? [True/False]' , type = bool)
        if model_checked :
            self.precision = click.prompt("Precision ? ", type = float)
            self.erreur = click.prompt("Erreur ? ", type = float)

        mode_auto = click.prompt('Faire la simulation en mode auto ? [True/False]' , type = bool)
        if mode_auto :
            self.RL = click.prompt("Faire de l'apprentissage par renforcement pour que les choix réalisés soient optimales ? [True/False]", type = bool)
            if self.RL :
                self.gamma = click.prompt("Valeur de gamma pour l'algorithme d'iteration de valeurs ? [<1]", type = float)
                self.eps = click.prompt("Valeur de epsilon pour l'lgorithme d’itération de valeurs ? ", type = float)
           
        return(nbr_tour, mode_auto, model_checked)


    def model_checking(self, nbr_tour):
        res_quant = self.SMC_quant(nbr_tour)
        res_qual = self.SMC_qual(nbr_tour)
        return(res_quant, res_qual)
    

    def SMC_quant(self, nbr_tour):
        somme_proba = {k : 0 for k in self.states.keys()}

        n = int(np.ceil(np.log(2)-np.log(self.erreur)/(2*self.precision)**2))

        for _ in range(n):
            res = self.simulation(nbr_tour, mode_auto=True, model_checked=True)
            somme_proba[res] +=1
        somme_proba = {k : v/n for k,v in somme_proba.items()}
        return(somme_proba)
    

    def SMC_qual(self, nbr_tour, alpha = 0.01, beta = 0.01):

        DM = {k : 0 for k in self.states.keys()}
        m = 0
        SPRT_result = {k : None for k in self.states.keys()}
        depart = time.time()
        while None in SPRT_result.values() :
            m +=1
            res = self.simulation(nbr_tour, mode_auto = True, model_checked  = True)
            DM[res] +=1
            for k in DM.keys() :
                if SPRT_result[k] is None :
                    SPRT_result[k] = self.SPRT(m, DM[k], alpha, beta, self.precision)

            duree = time.time() - depart
            if duree > 3 :
                break

        return(SPRT_result)

    
    def SPRT(self, m, dm, alpha, beta, precision):
        A = (1-beta)/alpha
        B = beta/(1-alpha)
        
        gamma0 = dm/m+precision
        gamma1 = dm/m-precision

        if (gamma0**dm)*((1-gamma0)**(m-dm)) != 0 :
            Rm = ((gamma1**dm)*((1-gamma1)**(m-dm)))/((gamma0**dm)*((1-gamma0)**(m-dm)))
            if Rm >= A :
                return('H1')
            elif Rm <= B:
                return('H2')
        
        return(None)


    def simulation(self, nbr_tour, mode_auto = False, model_checked = False ,plot = False, printer = False):
        for _ in range(nbr_tour):
            a = self.presentation_suite(mode_auto)
            if not mode_auto :
                a = input()

            if a == '':
                self.avance(model_checked=model_checked)
            else:
                self.avance(a, model_checked)
            if plot :
                self.plot_graph()
            if printer :
                print(f"Historique = {self.hist}")
                print(f"Recompense = {self.recompense}")
        return(self.current_state)


    def plot_graph(self):
        G = nx.DiGraph()

        list_node = []
        list_choix = []

        for etat in self.transitions:
            G.add_node(etat, label = etat)  
            if etat != self.current_state:
                list_node.append(etat)

        for etat in self.transitions:
            if None in self.transitions[etat]:
                total_prob = sum(self.transitions[etat][None].values()) 
                for node, prob in self.transitions[etat][None].items():
                    G.add_edge(etat, node, label=str(prob / total_prob))
            else:
                for choix, next_states in self.transitions[etat].items():
                    G.add_node(etat + choix, label=choix)
                    list_choix.append(etat + choix)

                    G.add_edge(etat, etat + choix)
                    total_prob = sum(next_states.values())
                    for p_etat, prob in next_states.items():
                        G.add_edge(etat + choix, p_etat, label=str(prob / total_prob))

        if self.pos is None :
            self.pos = nx.spring_layout(G)

        nx.draw_networkx_nodes(G, self.pos, node_color='red', nodelist=[self.current_state], node_size=500, alpha=0.8)
        nx.draw_networkx_nodes(G, self.pos, node_color='blue', nodelist=list_node, node_size=500, alpha=0.8)
        nx.draw_networkx_nodes(G, self.pos, node_color='gray', nodelist=list_choix, node_size=250, alpha=0.8)
        nx.draw_networkx_edges(G, self.pos, width=1, edge_color='black', connectionstyle="arc3,rad=0.15", arrowstyle='-|>')
        
        nx.draw_networkx_labels(G, self.pos, labels={i: G.nodes[i]['label'] for i in G.nodes})
        nx.draw_networkx_edge_labels(G, self.pos, edge_labels={(i, j): G[i][j]['label'] for i, j in G.edges if 'label' in G[i][j]})

        plt.axis('off')
        plt.show()
        return()


    def verif_model(self):
        '''
        Verifie que les états et les actions sont bien déclarés dans le préambule. 
        Verifie aussi qu'on ne melange pas MDP et MC
        '''
        for etat in self.transitions:
            if etat not in self.states:
                raise ValueError(f"{etat} n'est pas dans {self.states}, le fichier input comporte une erreur")

        for etat in self.transitions:
            for action in self.transitions[etat]:
                if action is not None :
                    if action not in self.actions:
                        raise ValueError(f"{action} n'est pas dans {self.actions}, le fichier input comporte une erreur")
            
        for etat in self.transitions:
            for action in self.transitions[etat]:
                for cle in self.transitions[etat][action].keys():
                    if cle not in self.states:
                        raise ValueError(f"{cle} n'est pas dans {self.states}, le fichier input comporte une erreur")
        
        for etat in self.transitions:
            if None in self.transitions[etat]:
                if len(self.transitions[etat]) > 1:
                    raise ValueError(f"Il y a un melange entre MC et MDP dans l'etat {etat}, le fichier input comporte une erreur")



class gramPrintListener(gramListener):
    def __init__(self, model):
        self.model = model

    def enterDefstates(self, ctx):
        for state_def in ctx.stateDef():
            state_name = str(state_def.ID())
            state_value = int(state_def.INT().getText())
            self.model.states[state_name] = state_value

    def enterDefactions(self, ctx):
        for action in ctx.ID():
            self.model.actions.add(str(action))

    def enterTransact(self, ctx):
        source_state = str(ctx.ID(0))
        action = str(ctx.ID(1))
        target_states = [str(x) for x in ctx.ID()[2:]]
        weights = [int(x.getText()) for x in ctx.INT()]
        self.model.transitions.setdefault(source_state, {}).setdefault(action, {})
        for target_state, weight in zip(target_states, weights):
            self.model.transitions[source_state][action][target_state] = weight

    def enterTransnoact(self, ctx):
        source_state = str(ctx.ID(0))
        target_states = [str(x) for x in ctx.ID()[1:]]
        weights = [int(x.getText()) for x in ctx.INT()]
        self.model.transitions.setdefault(source_state, {}).setdefault(None, {})
        for target_state, weight in zip(target_states, weights):
            self.model.transitions[source_state][None][target_state] = weight



def parse_file(file_content):
    model = MDP()
    lexer = gramLexer(antlr4.InputStream(file_content))
    stream = antlr4.CommonTokenStream(lexer)
    parser = gramParser(stream)
    tree = parser.program()
    printer = gramPrintListener(model)
    walker = antlr4.ParseTreeWalker()
    walker.walk(printer, tree)
    return(model)


def main(file_content):
    model = parse_file(file_content)

    print("States:", model.states)
    print("Actions:", model.actions)
    print("Transitions:", model.transitions)

    model.verif_model()

    nbr_tour, mode_auto, model_checked = model.initialisation()

    if model_checked:
        res_quant, res_qual = model.model_checking(nbr_tour)
        model.current_state = model.initial_state
        print(f"Resultats SMC quantitatif = {res_quant}")
        print(f"Resultats SMC qualitatif = {res_qual}")

    if model.RL :
        V_new, model.adversaire = model.algo_it_valeurs()
        print(f"Vn = {V_new}")
        print(f"adversaire choisi = {model.adversaire}")

    model.plot_graph()
    model.simulation(nbr_tour, mode_auto, plot = True, printer = True)

    print('Merci et au revoir')
    return(0)



if __name__ == '__main__':
    file_name = click.prompt('Nom du fichier input ? ', type=str)
    with open(file_name, 'r') as file:
        file_content = file.read()
        main(file_content)