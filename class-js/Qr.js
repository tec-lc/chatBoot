class Qr {
  /**
   * selector: CSS selector (pode ser div ou canvas)
   * options: { size: number }
   */
  constructor(selector, options = {}) {
    this.size = options.size || 200;
    this.target = document.querySelector(selector);
    if (!this.target) throw new Error("Elemento não encontrado: " + selector);
  }

  set(text) {
    if (typeof QRCode === 'undefined') {
      throw new Error("QRCode.js não encontrado. Inclua: https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js");
    }

    // Se alvo for canvas -> vamos gerar temporariamente numa div e copiar
    const isCanvas = this.target.tagName.toLowerCase() === 'canvas';

    // limpar alvo se for div
    if (!isCanvas) this.target.innerHTML = '';

    // cria container temporário (se necessário)
    const container = isCanvas ? document.createElement('div') : this.target;

    // garante tamanho do container para QRCode.js
    container.style.width = this.size + 'px';
    container.style.height = this.size + 'px';

    // se usamos temporário, não o acrescentamos ao DOM visível
    if (isCanvas) container.style.position = 'absolute', container.style.left = '-9999px', document.body.appendChild(container);

    // remove QR anterior se houver
    container.innerHTML = '';

    // gerar qrcode com nível H (mais tolerância)
    const qr = new QRCode(container, {
      text: text,
      width: this.size,
      height: this.size,
      correctLevel: QRCode.CorrectLevel.H
    });

    // se o alvo era canvas: copiar o canvas gerado para o canvas do usuário
    if (isCanvas) {
      // busca o canvas gerado pelo QRCode.js dentro do container (pode gerar <canvas> ou <table>)
      const generatedCanvas = container.querySelector('canvas');
      const destCanvas = this.target;
      const ctx = destCanvas.getContext('2d');

      // se não houve canvas (p.ex. gerou table), convertemos usando SVG fallback
      if (generatedCanvas) {
        // limpar destino
        ctx.clearRect(0, 0, destCanvas.width, destCanvas.height);
        // desenha mantendo proporção
        ctx.drawImage(generatedCanvas, 0, 0, destCanvas.width, destCanvas.height);
      } else {
        // fallback: tenta desenhar a table via html2canvas não disponível -> mostrar mensagem de erro
        ctx.clearRect(0, 0, destCanvas.width, destCanvas.height);
        ctx.fillStyle = "#fff";
        ctx.fillRect(0,0,destCanvas.width,destCanvas.height);
        ctx.fillStyle = "#000";
        ctx.font = "12px sans-serif";
        ctx.fillText("QR gerado como table. Use div ou outra lib.", 6, 20);
      }

      // remove container temporário do DOM
      container.remove();
    }

    return this;
  }
}

//--------------------------------------------------------

class LoopeGet {
  constructor(arquivo) {
    this.arquivo = arquivo;
    this.interval = null;
  }

  exe(segundos, callback) {
    // segundos → intervalo (ms)
    const tempo = segundos * 1000;

    // garante que não existam loops duplicados
    if (this.interval) clearInterval(this.interval);

    // função que carrega o arquivo
    const carregar = () => {
      fetch(this.arquivo + "?t=" + Date.now()) // evita cache
        .then(res => res.text())
        .then(html => callback(html))
        .catch(err => callback("Erro: " + err));
    };

    // executa imediatamente
    carregar();

    // cria loop
    this.interval = setInterval(carregar, tempo);
  }

  stop() {
    if (this.interval) clearInterval(this.interval);
  }
}
