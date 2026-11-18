# Prompt para cards de futebol

Use `modelos-cards.png` como referência visual.

```text
Crie um card de futebol personalizado inspirado no estilo EAFC/FIFA, seguindo a imagem anexada.

DADOS
Nome: [NOME]
Nota geral: [99]
Posição: [ATA]
País: [PAÍS]
Time ou seleção do uniforme: [TIME OU SELEÇÃO]
Clube do escudo: [CLUBE]
Estilo escolhido: [BRANCO / ROXO / AZUL / PRETO / DOURADO / VERDE]

ESTILOS
Branco: fundo branco marmorizado com fragmentos dourados e borda metálica champagne clara.
Roxo: fundo roxo com facetas e ondas magenta, borda neon turquesa e rosa.
Azul: fundo azul-safira escuro com cristais azuis, detalhes e borda em ouro antigo escuro, levemente envelhecido.
Preto: fundo preto com facetas e detalhes dourados, borda prata escura em aço escovado.
Dourado: fundo dourado luminoso com facetas triangulares, borda bronze escuro/café metálico.
Verde: fundo verde-esmeralda escuro com facetas e detalhes dourados, borda prata clara com filete esmeralda.

COMPOSIÇÃO
Card vertical em formato de escudo, topo ornamentado e ponta inferior. Mostrar a carta inteira, sem cortar as bordas.
No alto à esquerda, organizar verticalmente: nota geral grande, posição abaixo, bandeira do país e escudo do clube.
Posicionar o jogador no centro, deixando essa coluna visível. Usar a pessoa da foto anexada como referência, preservando suas características faciais, com o uniforme solicitado.
Escrever o nome centralizado acima dos atributos, diretamente sobre o fundo, SEM faixa, caixa ou moldura. Colocar uma linha horizontal fina abaixo do nome.

ATRIBUTOS
Duas colunas com divisória vertical fina.
Esquerda:
[00] TEC
[00] VIS
[00] PAS

Direita:
[00] DRI
[00] FIN
[00] DEF

Abaixo, centralizado:
[00] FIS

TEC = Técnica; VIS = Visão; PAS = Passe; DRI = Drible; FIN = Finalização; DEF = Defesa; FIS = Físico.
Exibir somente as abreviações no card.
Tipografia esportiva condensada e legível, com bom contraste. Acabamento metálico detalhado, alta resolução e proporções iguais às da referência. Não adicionar textos ou elementos extras.
```

## Modelo vazio, sem jogador

Acrescente ao prompt:

```text
Não incluir jogador, pessoa ou silhueta. Usar NOME, nota 99 e posição ATA. Substituir as notas dos atributos por --. Deixar um retângulo vazio para a bandeira e um contorno de escudo vazio para o clube, mantendo o espaço central livre para adicionar a foto depois.
```

## Prancha dos seis modelos

Para reproduzir o conjunto da imagem, acrescente:

```text
Gerar os seis modelos vazios em uma grade de três colunas e duas linhas: branco, roxo e azul acima; preto, dourado e verde abaixo. Mesmos tamanhos e proporções, cartas inteiras, separadas e sem sobreposição sobre fundo cinza claro. Manter todos os textos e espaços do modelo vazio em cada card.
```
