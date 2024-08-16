# Chatbot de Transcrição de Áudio

Este projeto cria uma notas de resumos diárias dos seus canais do Youtube Favoritos, utilizando 
a API do Youtube e Pytube para baixar os áudios dos vídeos, FastWhisper para gerar a transcrição
e alguma LLM para criar os resumos.


# Requisitos

- `Python 3.6+`
- `ffmpeg`
- `Ollama` instalado no seu computador (caso queira rodar modelos locais).

# Instalação

1.	Clone o repositório e navegue até o diretório do projeto.
2.	Instale os pacotes Python necessários:

`pip install -r requirements.txt`

3. Certifique-se de ter o Ollama rodando na sua máquina.
4. Instale o [ffmpeg](https://www.ffmpeg.org/).
5. Crie uma chave de acesso da [Youtube Data API](https://console.cloud.google.com/marketplace/product/google/youtube.googleapis.com?q=search&referrer=search&hl=pt-br&project=scidata-299417).
6. Crie uma chave de Acesso na GroqAI ou na OpenAI. Estas chaves serão usadas no passo 3 para resumir os vídeos, onde um Agent foi criado usando LangFlow. Caso queira editá-lo, instale a `langflow`, carregue o arquivo `Youtube Resumer.json` e edite-o. Lembre-se de alterar o arquivo 3.resume_video para contemplar suas mudanças.
7. Adicione as chaves geradas nos passos 5 e 6 em um arquivo chamado ".env", que deve ficar no mesmo diretório dos demais. 



# Como rodar?

1. Atualize o arquivo "canais" com a lista de canais que você deseja acompanhar.
2. Execute os scripts em ordem (1, 2 e 3).

Altere os scripts para atender melhor suas necessidades.