"""Exploración: abre cajones y lista ventanas y gadgets."""
import sys, time
import amiga, piloto as p, agente
def ventanas():
    for w in amiga.ventanas(): print(w[1:], flush=True)
