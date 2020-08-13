import pygame
import random
import os
pygame.init()

mafont = pygame.font.SysFont("monospace",35,True)
bird = pygame.image.load('images/bird.png')
background = pygame.image.load('images/flappy_bird_background.png')

class Joueur():
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.compte_saut = 3
		self.saute = False
		self.att = 0
		self.score = 0
		self.perdu = False
	
	def dessine(self,ecran):
		#pygame.draw.circle(ecran,(255,211,25),(int(self.x),int(self.y)),15)
		ecran.blit(bird,(int(self.x)-30,int(self.y)-30))

	def bouge(self):
		if self.saute:
			if self.compte_saut > -1:
				self.y -= self.compte_saut*0.3
				self.compte_saut -= 0.03
			else:
				self.compte_saut = 5
				self.saute = False
				self.y += 0.3
				self.att = 50
		else:
			self.y += 0.4
			if self.att > 0:
				self.att -= 1

	def controle(self):
		if pygame.mouse.get_pressed()[0] and not self.saute and self.att == 0:
			self.saute = True

	def verifie_perdu(self,passages):
		for passage in passages:
			if self.x + 12 >= passage.x and self.x <= passage.x + 80 and self.y + 12 >= passage.hauteur:
				self.perdu = True
			elif self.x + 12 >= passage.x and self.x <= passage.x + 80 and self.y <= passage.hauteur - 180:
				self.perdu = True


class Passage():
	def __init__(self,x,hauteur,indice):
		self.x = x
		self.hauteur = hauteur
		self.indice = indice

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
		self.compteur = 500

	def maj_ecran(self,ecran,persos,passa):
		#ecran.fill((52,204,255))
		#pygame.draw.rect(ecran,(154,94,0),(0,560,480,80))
		ecran.blit(background,(0,0))
		
		#drawing the green rectangles
		for passage in passa:
			passage.dessine(ecran)

		#drawing the player(s)
		for joueur in persos:
			joueur.dessine(ecran)
			
			texte_score = mafont.render("SCORE: " + str(joueur.score),1,(0,0,0)) 
			ecran.blit(texte_score,(5,5))
		
		texte_instru = mafont.render("Left Click to jump",1,(0,0,0))
		ecran.blit(texte_instru,(20,self.hauteur - 50))

		pygame.display.update()

	def run(self):
		screen = pygame.display.set_mode((self.largeur,self.hauteur))
		pygame.display.set_caption(self.nom)

		cont = True

		joueur = Joueur(240,320)
		joueurs = [joueur]
		passages = []
		indice_passage = 1

		#optimization
		global background
		background = background.convert()

		while cont:

			pygame.time.delay(1)

			events = pygame.event.get()
			for event in events:
				if event.type == pygame.QUIT:
					cont = False

			#Ajoute les passages
			if self.compteur > 0:
				self.compteur -= 1
			else:
				haut = random.randrange(150,520)
				passages.append(Passage(480,haut,indice_passage))
				indice_passage += 1
				self.compteur = 1000

			#La mise à jour des positions
			if not joueur.perdu:
				for passage in passages:
					passage.avance()
			
			for joueur in joueurs:
				if not joueur.perdu:
					joueur.controle()
					joueur.bouge()
					joueur.verifie_perdu(passages)

					for passage in passages:
						if passage.x <= 200:
							joueur.score = passage.indice

			self.maj_ecran(screen,joueurs,passages)

if __name__ == "__main__":
	jeu = Jeu(640,480,"Flappy Bird")
	jeu.run()
	pygame.quit()
