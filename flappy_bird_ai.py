import pygame
import random
import numpy as np
import math

pygame.init()

mafont = pygame.font.SysFont("monospace",35,True)
bird = pygame.image.load('images/bird.png')
background = pygame.image.load('images/flappy_bird_background.png')

def distance(x1,y1,x2,y2):
	return ((x1 - x2)**2 + (y1 - y2)**2)**(1/2)

def croisement(joueurs,pris):
	resu = sorted(joueurs,key = lambda x:x.score,reverse = True)
	scores = list(map(lambda x: x.score , resu))
	print(scores)
	resu = resu[:pris]
	print(len(resu))

	variation = 2

	for i in range(pris):
		resu[i].score = 0
		for j in range(pris):

			poids_parent1 = resu[i].poids
			poids_parent2 = resu[j].poids
			
			carac = np.zeros((4,1))
			
			for k in range(4):
				lancer = random.randint(0,1)
				if lancer == 1:
					carac[k][0] = poids_parent1[k][0] + random.uniform(-variation,variation)
				else:
					carac[k][0] = poids_parent2[k][0] + random.uniform(-variation,variation)
			
			lancer = random.randint(0,1)

			if lancer == 1:
				b = resu[i].bias + random.uniform(-variation,variation)
			else:
				b = resu[j].bias + random.uniform(-variation,variation)

			resu.append(Joueur(240,320,carac,b))
	print(len(resu))
	return resu


def initialisation(n):
	liste_poids = []
	resu = []

	for i in range(n):
		val = np.zeros((4,1))
		for j in range(4):
			val[j][0] = random.randrange(-10,10)

		liste_poids.append(val)

	for i in range(n):
		bias = random.randrange(-100,100)
		resu.append(Joueur(240,320,liste_poids[i],bias))
	return resu

class Joueur():
	def __init__(self,x,y,poids,bias):
		self.x = x
		self.y = y
		self.compte_saut = 2
		self.saute = False
		self.att = 0
		self.score = 0
		self.perdu = False
		self.poids = poids
		self.entree = np.zeros((1,4))
		self.bias = bias
		self.vitesse = 0
	
	def dessine(self,ecran):
		#pygame.draw.circle(ecran,(255,211,25),(int(self.x),int(self.y)),15)
		ecran.blit(bird,(int(self.x)-30,int(self.y)-30))

	def bouge(self):
		if self.saute:
			if self.compte_saut > -1:
				self.y -= self.compte_saut*0.3
				self.vitesse = self.compte_saut*0.3
				self.compte_saut -= 0.03
			else:
				self.compte_saut = 5
				self.saute = False
				self.y += 0.3
				self.vitesse = 0.3
				self.att = 50
		else:
			self.y += 0.4
			self.vitesse = 0.4
			if self.att > 0:
				self.att -= 1

	def controle(self):
		produit = np.dot(self.entree,self.poids)

		sortie = math.tanh(produit)

		if sortie > 0.5 and not self.saute and self.att == 0:
			self.saute = True


	def verifie_perdu(self,passages):
		for passage in passages:
			if self.x + 12 >= passage.x and self.x <= passage.x + 80 and self.y + 12 >= passage.hauteur:
				self.perdu = True
			elif self.x + 12 >= passage.x and self.x <= passage.x + 80 and self.y <= passage.hauteur - 180:
				self.perdu = True

	def calcule_distances(self,passages):

		for passage in passages:
			if passage.x >= 200:
				self.entree[0][0] = passage.x - self.x
				self.entree[0][1] = self.y - (passage.hauteur - 180)
				self.entree[0][2] = self.y - passage.hauteur
		
		self.entree[0][3] = self.vitesse 

class Passage():
	def __init__(self,x,hauteur):
		self.x = x
		self.hauteur = hauteur
		self.passe = False

	def dessine(self,ecran):
		pygame.draw.rect(ecran,(76,187,23),(int(self.x),0,80,int(self.hauteur - 180)))
		pygame.draw.rect(ecran,(76,187,23),(int(self.x),self.hauteur,80,int(640 - self.hauteur)))

	def avance(self):
		self.x -= 0.3

class Jeu():
	def __init__(self,hauteur,largeur,nom):
		self.hauteur = hauteur
		self.largeur = largeur
		self.nom = nom
		self.compteur = 0
		self.record = 0

	def maj_ecran(self,ecran,persos,passa,generation,score):
		#ecran.fill((52,204,255))
		#pygame.draw.rect(ecran,(154,94,0),(0,560,480,80))
		ecran.blit(background,(0,0))
		
		for passage in passa:
			passage.dessine(ecran)

		for joueur in persos:
			joueur.dessine(ecran)
			
		texte_en_vie = mafont.render("alive: " + str(len(persos)),1,(0,0,0)) 
		ecran.blit(texte_en_vie,(5,5))

		texte_gen = mafont.render("generation: " + str(generation),1,(0,0,0))
		ecran.blit(texte_gen,(5,35))

		texte_score = mafont.render("score: " + str(score),1,(0,0,0))
		ecran.blit(texte_score,(5,65))

		texte_record = mafont.render("record: " + str(self.record),1,(0,0,0))
		ecran.blit(texte_record,(5,95))

		pygame.display.update()

	def run(self):
		screen = pygame.display.set_mode((self.largeur,self.hauteur))
		pygame.display.set_caption(self.nom)

		generation = 1
		
		cont = True
		debut = True

		roaster = initialisation(100)
		joueurs = list(roaster)

		#optimizing the blitting of these images
		global bird
		bird = bird.convert_alpha()
		global background
		background = background.convert()
		
		while cont:

			score = 0
			
			if debut:
				debut = False
			else:
				roaster = croisement(roaster,10)
				joueurs = list(roaster)
				generation += 1
				self.compteur = 0
			
			passages = []
			
			while joueurs != []:


				events = pygame.event.get()
				for event in events:
					if event.type == pygame.QUIT:
						cont = False

				#Ajoute les passages
				if self.compteur > 0:
					self.compteur -= 1
				else:
					haut = random.randrange(220,520)
					passages.append(Passage(480,haut))
					self.compteur = 1000

				#La mise à jour des positions
				for passage in passages:
					passage.avance()
					if int(passage.x) == 240 and not passage.passe:
						score += 1
						passage.passe = True

					if passage.x <= -80:
						passages.pop(passages.index(passage))
				
				for joueur in joueurs:
					if not joueur.perdu:
						joueur.controle()
						joueur.bouge()
						joueur.calcule_distances(passages)
						joueur.verifie_perdu(passages)

						joueur.score += 1

					else:
						joueurs.pop(joueurs.index(joueur))

				if score > self.record:
					self.record = score

				self.maj_ecran(screen,joueurs,passages,generation,score)


if __name__ == "__main__":
	jeu = Jeu(640,480,"Flappy Bird IA")
	jeu.run()
	pygame.quit()