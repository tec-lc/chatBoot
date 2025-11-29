# ChatBoot

Sistema simples para autenticação via QR Code e automação de mensagens no WhatsApp usando **PHP**, **JavaScript**, **Python** e **Selenium**.

---

## 📌 Descrição do Projeto

Este projeto fornece uma página em **PHP + JavaScript** que executa um arquivo em **Python** responsável por abrir o WhatsApp Web e iniciar uma automação de mensagens.

A comunicação entre PHP/JS e Python é feita através de **troca de arquivos**, permitindo que qualquer linguagem consiga controlar o processo apenas editando ou lendo arquivos.

---

## 🚀 Como funciona

1. Instale um servidor com **PHP**, **Python** e **Selenium** configurado.
2. Abra o arquivo **`index.php`** no navegador.
3. O `index.php` executará o arquivo **`inicia.py`**.
4. O `inicia.py` abrirá o WhatsApp Web para autenticação via **QR Code**.
5. Assim que o login for concluído, a automação começará automaticamente.

---

## ✏️ Alterando as mensagens automáticas

Toda a lógica e conteúdo das mensagens automáticas ficam dentro do arquivo:

```
inicia.py
```

Basta editar esse arquivo para mudar frases, lógicas, comportamentos etc.

---

## 📁 Resumo da Estrutura

```
chatBoot/
├── index.php        # Página inicial que chama o Python
├── inicia.py        # Automação do WhatsApp com Selenium
├── ... outros arquivos de controle
```

---

## ✔️ Conclusão

Após configurar o servidor e abrir o `index.php`, o sistema fará todo o processo automaticamente. A partir daí, qualquer mudança na automação é feita editando o `inicia.py`.
