# O que é que este script faz?
Este script foi feito para recolher informação da API do IST (scholar.tecnico.ulisboa.pt/api). Quando se corre o script, para cada um dos tipos de dados disponíveis é criado um ficheiro CSV com os dados recolhidos. Enquando to script está a correr, vai imprimindo no ecrã o link do último pedido à API que analizou e quantos links extraiu desse pedido à API. 

## Tipos de dados disponíveis
O script permite recolher até 4 dados diferentes:
- `units` : Unidades de investigação. Devolve os links para a página do IST scholar de todas as unidades de investigação registadas na plataforma.
- `researchers` : Investigadores. Devolve os links para a página do IST scholar de todos os investigadores registados na plataforma.
- `records` : Publicações. Devolve os links para a página do IST scholar de todas as publicações registados na plataforma.
- `files` : Ficheiros. Devolve links directos para todos os ficheiros publicados em formato aberto na plataforma.

# Prerequisitos
- Node.js
- npm

# Como instalar
 `npm i`

# Como escolher o que recolher da API
- Abrir o ficheiro `crawl.js`
- Alterar a linha 8 (`const requestTypes = ['files'];`) para incluir o(s) tipo(s) de dados que se quer recolher da API

# Como correr
 `node ./crawl.js`

# Troubleshooting

## "É muito lento"
Baixa o delay entre pedidos na linha 12, `const delayBetweenRequests = 5000`.  

## Script falha com erro "ECONNRESET" ou semelhante
És capaz de ter sido automaticamente bloqueado pela API por estares a fazer demasiados pedidos. Aumenta o delay entre pedidos na linha 12, `const delayBetweenRequests = 5000`, espera um minuto ou outro e volta a correr o script.  