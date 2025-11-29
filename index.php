<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
  <script src="class-js/Qr.js"></script>

  <title>Mensagens Auto Programaveis!</title>
  <style>
    /* Layout inspirado no Google: foco no centro, muito espaço em branco */
    :root{--bg:#fff;--muted:#666;--accent:#1a73e8}
    html,body{height:100%;margin:0;font-family:Inter, Roboto, Arial, Helvetica, sans-serif;background:var(--bg);color:#111}
    .wrap{min-height:100%;display:flex;flex-direction:column}

    header{padding:28px 16px;text-align:center}
    header h1{margin:0;font-weight:600;font-size:28px;color:#202124}
    main{flex:1;display:flex;align-items:flex-start;justify-content:center;padding:40px 16px}

    .card{width:720px;max-width:96%;text-align:center}
    .user{margin-top:18px;font-size:18px;color:var(--muted)}

    .qr-wrap{margin:28px auto 18px;display:flex;justify-content:center}
    .qr{width:220px;height:220px;border:1px solid #e6e6e6;display:grid;place-items:center;background:linear-gradient(180deg,#fafafa,#fff)}
    .qr canvas{width:200px;height:200px}
    .qr .caption{font-size:13px;color:var(--muted);margin-top:8px}

    .actions{display:flex;gap:12px;justify-content:center;margin-top:18px}
    button{background:var(--accent);color:#fff;border:none;padding:10px 16px;border-radius:6px;font-size:15px;cursor:pointer;box-shadow:0 1px 0 rgba(0,0,0,0.08)}
    button.ghost{background:transparent;color:var(--accent);border:1px solid #dbe7ff}

    /* Textarea panel */
    .panel{margin-top:20px;}
    .panel textarea{width:100%;min-height:160px;padding:12px;font-size:14px;border:1px solid #ddd;border-radius:8px;resize:vertical}
    .panel .panel-actions{display:flex;justify-content:flex-end;margin-top:8px}
    .small{font-size:13px;color:var(--muted)}

    footer{padding:18px;text-align:center;color:var(--muted);font-size:13px}

    .img_carregando{
      width: auto;
      height: 50px;
    }

    @media (max-width:420px){.qr{width:180px;height:180px}.qr canvas{width:160px;height:160px}}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>chatBoot Mensagens Auto Programaveis!</h1>
    </header>

    <main>
      <div class="card" role="main">

        <div class="carregandoQr msgGlobal" style="display:none;">
          <img src="icon/carregando.gif" class="img_carregando">
          <div class="user" id="username">
            Aguarde!<br>
            Pareando Qrcode...
          </div>
          <div class="user dados_reais" id="username">
            retorno:
          </div>

          <div class="actions">
            <button id="btnCancel" class="ghost btnCancel" title="Cancelar pareamento">Cancelar pareamento</button>
          </div>
        </div>


        <div class="carregandoMsg msgGlobal" style="display:none;">
          <img src="icon/carregando.gif" class="img_carregando">
          <div class="user" id="username">
            Login autenticado!<br>
            Carregando Mensagens...
          </div>
          <div class="user dados_reais" id="username">
            retorno:
          </div>
          <div class="actions">
            <button id="btnCancel" class="ghost btnCancel" title="Cancelar pareamento">Desconectar</button>
          </div>
        </div>

        <div class="aguardandoMsg msgGlobal" style="display:none;">
          <img src="icon/carregando.gif" class="img_carregando">
          <div class="user" id="username">
            Mensagens carregadas!<br>
            Aguardando Mensagens para iniciar boot...
          </div>
          <div class="user dados_reais" id="username">
            retorno:
          </div>
          <div class="actions">
            <button id="btnCancel" class="ghost btnCancel" title="Cancelar pareamento">Desconectar</button>
          </div>
        </div>


        <div class="boot msgGlobal" style="display:none;">
          <img src="icon/carregando.gif" class="img_carregando">
          <div class="user" id="username">
            Boot em andamento!<br>
            Respondendo mensagens...
          </div>
          <div class="user dados_reais" id="username">
            retorno:
          </div>
          <div class="actions">
            <button id="btnCancel" class="ghost btnCancel" title="Cancelar pareamento">Desconectar</button>
          </div>
        </div>


        <div class="carregandoOff msgGlobal" style="display:none;">
          <img src="icon/carregando.gif" class="img_carregando">
          <div class="user" id="username">
            Finalizando boot!<br>
            Desconectando...
          </div>
          <div class="user dados_reais" id="username">
            retorno:
          </div>
        </div>


        <div class="off msgGlobal" style="display:none;">
          <div class="user" id="username">
            Boot Finalisado!
          </div>
          <div class="user dados_reais" id="username">
            retorno:
          </div>

          <div class="actions">
            <button id="btnProgram">Iniciar novamente</button>
          
          </div>
          <!--<div class="panel" id="panel">
            <div class="small">Escreva aqui as respostas automáticas que deseja programar. Use uma resposta por linha.</div>
            <textarea id="responsesArea" placeholder="Ex: Olá! Estou ocupado no momento. Retorno em breve..."></textarea>
            <div class="panel-actions">
              <button id="saveBtn">Salvar</button>
            </div>
          </div>-->
        </div>



        <div class="qrcodPareado msgGlobal" style="display:none;">
          <div class="user" id="username">
            QrCode Pareado!
          </div>

          <div class="qr-wrap" >
            <div class="qr" aria-label="QR code de pareamento" title="QR code de pareamento">
              <canvas id="qrCanvas" width="200" height="200"></canvas>
            </div>
          </div>
          <div class="user" id="username">
            Para iniciar o chatBoot aponte seu autenticador do WhatsApp
          </div>

          <div class="user dados_reais" id="username">
            retorno:
          </div>

          <div class="actions">
            <button id="btnCancel" class="ghost btnCancel" title="Cancelar pareamento">Cancelar pareamento</button>
          </div>
        </div>




      </div>
    </main>

    <footer>
      <span class="small">Tela de pareamento — apenas protótipo</span>
    </footer>
  </div>

  <script>
  $(document).ready(function() {



    function carregandoQr(){//-------
      $('.msgGlobal').attr('style','display:none;');
      $('.carregandoQr').attr('style','display:block;');
    }//------------------------------
    function carregandoMsg(){//-------
      $('.msgGlobal').attr('style','display:none;');
      $('.carregandoMsg').attr('style','display:block;');
    }//------------------------------
    function aguardandoMsg(){//-------
      $('.msgGlobal').attr('style','display:none;');
      $('.aguardandoMsg').attr('style','display:block;');
    }//------------------------------
    function boot(){//-------
      $('.msgGlobal').attr('style','display:none;');
      $('.boot').attr('style','display:block;');
    }//------------------------------
    function carregandoOff(){//-------
      $('.msgGlobal').attr('style','display:none;');
      $('.carregandoOff').attr('style','display:block;');
    }//------------------------------
    function off(){//-------
      $('.msgGlobal').attr('style','display:none;');
      $('.off').attr('style','display:block;');
    }//------------------------------
    function qrcodPareado(){//-------
      $('.msgGlobal').attr('style','display:none;');
      $('.qrcodPareado').attr('style','display:block;');
    }//------------------------------

    //---------------------------------------------------------

    function startBoot(){//-------
      exe=false;
      $('button').attr('style','');
      carregandoQr();
      $.post('servidor/startBoot.php', {start: 'start'}, function(resposta) {
        console.log('start:', resposta);
      });
    }//------------------------------

    function offBoot(){//-------
      //alert('desconectar');
      exe=true;
      carregandoOff();
      $.post('servidor/finalizarConexao.php', {start: 'start'}, function(resposta) {
        console.log('stop:', resposta);

        off();

      });
    }//------------------------------



    //---------------------------------------------------------
    //inicio pagina:
    var exe=false;
    startBoot();


    //---------------------------------------------------
    new LoopeGet('servidor/relatorio.html').exe(1,(data)=>{

      //console.log('retornou: ',data);

      if(exe==false){
        data=data.split('<>');
        console.log(data);

        if(data[1]=='carregandoQr'){
          carregandoQr();
        }else if(data[1]=='carregandoMsg'){
          carregandoMsg();
        }else if(data[1]=='aguardandoMsg'){
          aguardandoMsg();
        }else if(data[1]=='boot'){
          boot();
        }else if(data[1]=='carregandoOff'){
          carregandoOff();
        }else if(data[1]=='off'){
          off();
        }else if(data[1]=='qrcodPareado'){
          qrcodPareado();
          new Qr('#qrCanvas', { size: 200 }).set(data[2]);
          console.log(data[2]);
        }
        $('.dados_reais').html(data[2]);

      }

    });
    //-----------------------------------------------------------
    // configure conforme necessário
    $('button[class="ghost btnCancel"]').click(function(){
      //alert('click');
      $(this).attr('style','display:none;');
      offBoot();
    });
    $('button[id="btnProgram"]').click(function(){
      //alert('click');
      startBoot();
    });


    //------------------------------------------------------------
  });//this
  </script>
</body>
</html>
