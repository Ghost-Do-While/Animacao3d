# layout.py - constantes de layout do condomínio AMPLIADO (lote 32 x 26 m), compartilhadas por todas as partes.
# Origem no centro do lote. +X direita (vagas do muro direito), +Y fundos, -Y frente/rua.
LX, LY = 16.0, 13.0                  # meio-lote: X -16..16, Y -13..13
WALL_H = 2.4
COB_H = 1.3                          # muros de cobogó
FLOORS, FLOOR_H = 4, 3.0             # prédio: 4 x 3 m = 12 m

# frente do lote (Y = -13): guarita CENTRALIZADA, SAÍDA à esquerda e ENTRADA à direita (5 m cada), simétricas
EXIT_X = (-8.5, -3.5)                # SAÍDA (esquerda)
COBC_X = (-3.5, 3.5)                 # cobogó central (abraça a guarita)
ENTR_X = (3.5, 8.5)                  # ENTRADA (direita)
COBL_X = (-16.0, -8.5)               # cobogó esquerdo
COBR_X = (8.5, 16.0)                 # cobogó direito
ENTR_CX = 6.0                        # eixo da faixa de entrada
EXIT_CX = -6.0

# prédio (canto fundo-esquerdo): 7 x 13 m
BX0, BX1 = -15.7, -8.7               # X do prédio (fachada de sacadas voltada para +X em BX1)
BY0, BY1 = -0.3, 12.7
B_RECUO = 0.7                        # Bloco B recuado
BYM = 6.2                            # divisa entre Bloco A (frente, -Y) e Bloco B (fundos, +Y)

# guarita 4 x 5 m, centralizada em X = 0 (sem pilar nos fundos da marquise)
GX0, GX1, GY0, GY1 = -2.0, 2.0, -12.6, -7.6
GH = 2.8

# cancelas / sensores (sensores encostados nas laterais da faixa, fora do caminho dos carros)
ARM_LEN = 5.2
C1_BASE = (-9.0, -10.5); C1_PIV = (-8.75, -10.5)      # saída: braço aponta +X
C2_BASE = (9.0, -7.5);   C2_PIV = (8.75, -7.5)        # entrada: braço aponta -X
S1_POS = (-9.4, -5.8)                                  # saída: dentro do lote, junto à lateral esquerda da faixa
S2_POS = (9.3, -11.6)                                  # entrada: junto ao cobogó direito, ao lado da faixa

# gradis e postes (os gradis encostam nos muros)
GR1 = ((-5.2, -1.5), (-5.2, 12.95))  # vertical (até o muro dos fundos)
GR2 = ((-16.0, -3.3), (-6.2, -3.3))  # horizontal (desde o muro esquerdo)
P1 = (-5.5, 12.4); P2 = (-6.3, -3.9)

# vagas: 2,6 x 5,2 m; as linhas encostam no muro dos fundos, no muro direito e no gradil
SLOT_W, SLOT_D = 2.6, 5.2
LINE_TOP = 12.94                                       # primeira linha, colada ao muro dos fundos
RIGHT_X0, RIGHT_X1 = 10.8, 16.0                        # 4 vagas no muro direito
RIGHT_Y = [LINE_TOP - 1.3 - 2.6 * i for i in range(4)]    # centros V1..V4 (V3 = vaga disputada)
CENT_X0, CENT_X1 = -5.18, 0.02                         # 2 vagas centrais (encostadas no gradil)
CENT_Y = {'V6': LINE_TOP - 1.3, 'V5': LINE_TOP - 1.3 - 2.6}
AISLE_X = 4.4                                          # eixo do corredor de manobra (carros em direção às vagas)

# rua (fora do lote)
SW_Y = (-16.0, -13.0)                # calçada da frente (3 m)
ROAD_Y = (-23.0, -16.0)              # rua: 2 faixas de 3,5 m
SW2_Y = (-26.0, -23.0)
LANE_Y = -17.75                      # faixa mais próxima do condomínio
LANE2_Y = -21.25

# apartamento (Bloco A, 3º andar, dentro do prédio)
APT_FLOOR = 2
APT_Z = APT_FLOOR * FLOOR_H + 0.2    # topo do piso
APT_X0, APT_X1 = -15.5, -8.95
APT_Y0, APT_Y1 = 0.0, 6.0
def AZ(x, y, z=0.0): return (x, y, APT_Z + z)

# discussão na frente da V3 e picape do Miguel (fora do caminho de manobra das vagas)
MIGUEL_POS = (10.0, RIGHT_Y[2] + 0.6); CLAUDIO_POS = (10.0, RIGHT_Y[2] - 0.6)
PICKUP_POS = (11.4, 1.0)
