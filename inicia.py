
from class_web import Web

zap=Web(headless=False)
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

#id_cliente='div[class="_ak72 false false false _ak73 _ak7n _asiw _ap1- _ap1_"]'
id_cliente='div[class="x10l6tqk xh8yej3 x1g42fcv"]'

id_inputCoversa='div[class="x1n2onr6 xh8yej3 xjdcl3y lexical-rich-text-input"]'

id_nanhumaCoversa='div[class="x1c436fg"]'
id_ultimaCoversa='div[class="_amk6 _amlo false false"] div div div span span'

res_inicio = (
    "Olá tudo bem?\n"
    "(1) Quero ser associado\n"
    "(2) Pagar minha conta\n"
    "(3) Falar com atendente\n"
)

res_1 = (
    "Para ser associado existem 2 planos!\n"
    "(a) Plano Premium 19,90 por mês\n"
    "(b) Plano Mediano 10,30 por mês\n"
)

res_2 = "Para pagar sua conta escreva seu RG:"
res_3 = "Aguarde que você já será atendido(a):"
res_planos = "Parabéns por assinar seu Plano!"
res_rg = "RG confirmado! Sua conta foi enviada por email."

respostas = {
    "Bom dia": res_inicio,
    "bom dia": res_inicio,
    "Menu": res_inicio,
    "menu": res_inicio,
    '1': res_1,
    '2': res_2,
    '3': res_3,
    "a": res_planos,
    "b": res_planos,
    "A": res_planos,
    "B": res_planos,
    '123': res_rg,
}
def respostaCorreta(texto):
    texto = str(texto).strip()
    return respostas.get(texto, False)





id_bntUser='img[class="x1n2onr6 x1lliihq xh8yej3 x5yr21d x6ikm8r x10wlt62 x1c9tyrk xeusxvb x1pahc9y x1ertn4p xl1xv1r x115dhu7 x17vty23 x1hc1fzr x4u6w88 x1g40iwv _ao3e"]'

id_imgUser='img[style="height: 100%; width: 100%; visibility: visible;"]'

id_telefone='span[class="x140p0ai x1gufx9m x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x193iq5w xeuugli x13faqbe x1vvkbs x1lliihq x1fj9vlw x14ug900 x1hx0egp x1jchvi3 xjb2p0i xo1l8bm x17mssa0 x1ic7a3i"]'

close= False
start=True
executa='carregandoQr'
mensagensQr=True
click_naoLidas=False
while start == True:
    close = str( zap.abre('bootClose.html') ).strip()
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

        val_bntNaoLidas=zap.html(id_bntNaoLidas)

        if mensagensQr == False:
            print('carregandoMsg')
            zap.arquivo('relatorio.html','carregandoMsg')

        if mensagensQr == False and val_bntNaoLidas!=False:
            executa = 'carregandoMsg'

    elif executa == 'carregandoMsg' :
        val_bntNaoLidas=zap.html(id_bntNaoLidas)
        print('aguardandoMsg')
        zap.arquivo('relatorio.html','aguardandoMsg')

        if val_bntNaoLidas != False :
            executa = 'boot'
            print('aguardandoMsg')
            zap.arquivo('relatorio.html','aguardandoMsg')

            zap.click(id_bntNaoLidas,1)#abre não lidas
            zap.pause(3)
            cont_msg=0

    elif executa == 'boot' :

        zap.pause(1)

        #nanhumaCoversa = zap.html(id_nanhumaCoversa,cont_msg)
        convesaResponder = zap.html(id_cliente,cont_msg)
        print('contador(',cont_msg,') criente(',convesaResponder,')')
        zap.pause(1)
        #if nanhumaCoversa == True:
        #    zap.click(id_bntNaoLidas,1)#fecha não lidas
        #    zap.pause(3)


        if convesaResponder!=False:

            print('abrindo não lidas')


            zap.arquivo('relatorio.html','boot')

            zap.click(id_cliente,cont_msg)
            zap.pause(1)

            #----obter ultima conversa
            ultimaCoversa=zap.html_array(id_ultimaCoversa)

            if ultimaCoversa != False :
                ultimaCoversa=ultimaCoversa[-3].get('text', False)
    
                #ultimaCoversa=ultimaCoversa[-3]['text']
                print(ultimaCoversa)

                zap.pause(1)
                VaiResponder=respostaCorreta(ultimaCoversa);
                if VaiResponder != False :
                    zap.escreve(respostaCorreta(ultimaCoversa),id_inputCoversa)
                    zap.teclado('enter')
                    cont_msg+= 1

        else :
            cont_msg=0





        #verificar mensagem
        #zap.arquivo('relatorio.html','off')
        #start = False


#input("sessão fechou...")
