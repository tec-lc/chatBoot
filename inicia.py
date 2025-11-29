
from class_web import Web

zap=Web()
zap.sessao('sessao_bootzap')
zap.url('https://web.whatsapp.com')
zap.arquivo('relatorio.html','carregandoQr')
zap.pause(3)
# função que será executada dentro do loop
id_confi='div[class="x1c4vz4f xs83m0k xdl72j9 x1g77sc7 x78zum5 xozqiw3 x1oa3qoh x12fk4p8 xeuugli x2lwn1j x1nhvcw1 x1q0g3np x1cy8zhl x100vrsf x1vqgdyp x1ekkm8c x1143rjc xum4auv xj21bgg x1277o0a x13i9f1t xr9ek0c xjpr12u x14ug900 xzs022t"]'

id_mensagensQr='div[class="x579bpy xo1l8bm xggjnk3 x1hql6x6"]'

id_qrcode='div[class="_akau x1n2onr6 x78zum5 x1okw0bk x6s0dn4 xl56j7k x1tdqgrh x1l76qip x6ikm8r x10wlt62 xr9e8f9 x1e4oeot x1ui04y5 x6en5u8 x9r4l05 x8idabb"]'
attr_qrcod='data-ref'

id_bntNaoLidas='button[aria-controls="chat-list"]'

id_cliente='div[class="_ak72 false false false _ak73 _ak7n _asiw _ap1- _ap1_"]'





id_bntUser='img[class="x1n2onr6 x1lliihq xh8yej3 x5yr21d x6ikm8r x10wlt62 x1c9tyrk xeusxvb x1pahc9y x1ertn4p xl1xv1r x115dhu7 x17vty23 x1hc1fzr x4u6w88 x1g40iwv _ao3e"]'

id_imgUser='img[style="height: 100%; width: 100%; visibility: visible;"]'

id_telefone='span[class="x140p0ai x1gufx9m x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x193iq5w xeuugli x13faqbe x1vvkbs x1lliihq x1fj9vlw x14ug900 x1hx0egp x1jchvi3 xjb2p0i xo1l8bm x17mssa0 x1ic7a3i"]'

close= False
start=True
executa='carregandoQr'
mensagensQr=True
click_naoLidas=False
while start == True:
    close = zap.abre('bootClose.html')
    zap.arquivo('bootClose.html','')
    print(close);
    zap.pause(1)
    if close == 'close' :
        zap.sessao_salve()
        start = False
        executa = False
        zap.arquivo('relatorio.html','off')


    elif executa == 'carregandoQr':

        mensagensQr=zap.html(id_mensagensQr)

        qrcod = zap.attr(id_qrcode,attr_qrcod)
        print(qrcod)
        zap.arquivo('relatorio.html',qrcod)


        if mensagensQr == False:
            executa = 'carregandoMsg'
            print('carregandoMsg')
            zap.arquivo('relatorio.html','carregandoMsg')

    elif executa == 'carregandoMsg' :
        val_bntNaoLidas=zap.html(id_bntNaoLidas)
        print('aguardandoMsg')
        zap.arquivo('relatorio.html','aguardandoMsg')

        if val_bntNaoLidas != False :

            zap.click(id_bntNaoLidas,1)
            print('abrindo não lidas')
            zap.arquivo('relatorio.html','boot')
            executa = 'boot'
            zap.pause(3)

    elif executa == 'boot' :

        valor = zap.html(id_cliente)
        if valor!=False:
            zap.click(id_cliente)
            zap.pause(3)
            zap.escreve('Olá! Tudo bem?')
            zap.pause(1)
            zap.teclado('enter')
            zap.pause(1)
            zap.escreve(
                "1 - Quero resolver minhas finanças\n"
                "2 - Problemas pessoais\n"
                "3 - Falar com atendente\n"
            )
            zap.pause(1)
            zap.teclado('enter')
            zap.pause(30)
        #verificar mensagem
        #zap.arquivo('relatorio.html','off')
        #start = False


input("sessão fechou...")
