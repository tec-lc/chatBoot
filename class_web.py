# selenium_web_wrapper.py
# Versão atualizada: adiciona html_array, attr_array, abre, sessao, sessao_salve, sessao_drop

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, WebDriverException, JavascriptException

import threading
import time
import os
import sys
import traceback
import shutil


class Web:
    def __init__(self, headless=False, chrome_driver_path=None, chrome_binary_path=None, default_wait=10, window_size=(1280, 800)):
        """
        headless: True para rodar sem interface, False para abrir o Chrome
        chrome_driver_path: caminho para chromedriver (se None usa PATH)
        chrome_binary_path: caminho para o binário do Chrome (opcional)
        default_wait: tempo padrão de espera para operações
        window_size: tupla (width, height)
        """
        self.headless = headless
        self.chrome_driver_path = chrome_driver_path
        self.chrome_binary_path = chrome_binary_path
        self.default_wait = default_wait
        self.window_size = window_size

        # sessão (pasta de perfil do Chrome)
        self._session_path = None

        self._exit_flag = False
        self._loop_thread = None

        self._driver = None
        self._actions = None
        self._start_driver()

    def _build_options(self):
        chrome_options = Options()
        if self.headless:
            # selenium >=4 headless new
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--window-size={self.window_size[0]},{self.window_size[1]}")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        if self.chrome_binary_path:
            chrome_options.binary_location = self.chrome_binary_path

        # se sessão configurada, define user-data-dir
        if self._session_path:
            chrome_options.add_argument(f"--user-data-dir={os.path.abspath(self._session_path)}")

        return chrome_options

    def _start_driver(self):
        try:
            chrome_options = self._build_options()
            if self.chrome_driver_path:
                # executável custom
                self._driver = webdriver.Chrome(executable_path=self.chrome_driver_path, options=chrome_options)
            else:
                self._driver = webdriver.Chrome(options=chrome_options)
        except TypeError:
            # fallback para assinaturas antigas
            chrome_options = self._build_options()
            self._driver = webdriver.Chrome(options=chrome_options)
        except WebDriverException as e:
            print(f"Erro ao iniciar ChromeDriver: {e}")
            raise

        self._actions = ActionChains(self._driver)

    def _restart_driver_with_profile(self):
        """Reinicia o driver (usado quando sessao é alterada)."""
        try:
            if self._driver:
                try:
                    self._driver.quit()
                except Exception:
                    pass
        finally:
            self._start_driver()

    # ---------------------- funções existentes (com pequenas adaptações) ----------------------
    def url(self, endereco: str):
        """Abre a URL informada"""
        try:
            self._driver.get(endereco)
            return True
        except Exception as e:
            print(f"url error: {e}")
            return False

    def pause(self, segundos: float = None):
        """Se segundos for None faz waiting até document.readyState == 'complete' (até default_wait)
           Se número: sleep(segundos)
        """
        if segundos is None:
            timeout = self.default_wait
            start = time.time()
            while True:
                try:
                    ready = self._driver.execute_script('return document.readyState')
                except JavascriptException:
                    ready = None
                if ready == 'complete':
                    return True
                if time.time() - start > timeout:
                    return False
                time.sleep(0.1)
        else:
            time.sleep(segundos)
            return True

    def _find(self, selector):
        try:
            elems = self._driver.find_elements(By.CSS_SELECTOR, selector)
            return elems
        except Exception:
            return []

    def html(self, selector, index=0):
        """
        Retorna o TEXTO do elemento indicado.
        - html('p') -> pega o primeiro <p>
        - html('p', 0) -> pega o primeiro <p>
        - html('p', 2) -> pega o terceiro <p>
        """
        elems = self._find(selector)
        if not elems:
            return False

        if index < 0:
            index = 0
        if index >= len(elems):
            return False

        el = elems[index]

        try:
            return el.text
        except Exception:
            return False


    def html_array(self, selector):
        """Retorna lista de dicionários [{'text':..., 'html':...}, ...] ou [] se não existir"""
        elems = self._find(selector)
        results = []
        for e in elems:
            try:
                inner = self._driver.execute_script('return arguments[0].innerHTML;', e)
            except Exception:
                inner = ''
            results.append({'text': e.text, 'html': inner})
        return results

    def click(self, selector, index=0):
        """
        Clica no elemento pelo índice.
        Ex:
            click('h1')      -> index 0
            click('h1', 2)   -> terceiro h1 encontrado
        """
        elems = self._find(selector)
        if not elems:
            return False

        # garante index válido
        if index < 0 or index >= len(elems):
            return False

        elem = elems[index]

        try:
            elem.click()
            return True
        except Exception as e:
            # fallback: click via JS
            try:
                self._driver.execute_script("arguments[0].click();", elem)
                return True
            except Exception:
                print(f"click error: {e}")
                return False


    def focus(self, selector=None, index=0):
        """
        Foca no elemento indicado pelo selector (CSS) e índice.
        - selector=None -> foca no body
        - retorna True se conseguiu focar, False caso contrário
        Ex:
          zap.focus('input')        # foca no primeiro input
          zap.focus('input', 2)     # foca no terceiro input
        """
        try:
            if selector is None:
                # foco no body
                body = self._driver.find_element(By.TAG_NAME, 'body')
                try:
                    body.click()
                except Exception:
                    pass
                return True

            elems = self._find(selector)
            if not elems:
                return False

            if index < 0:
                index = 0
            if index >= len(elems):
                return False

            el = elems[index]
            try:
                # tenta focus via JS (mais robusto)
                self._driver.execute_script("arguments[0].scrollIntoView({behavior:'auto',block:'center'}); arguments[0].focus();", el)
                try:
                    el.click()
                except Exception:
                    pass
                return True
            except Exception:
                try:
                    el.click()
                    return True
                except Exception:
                    return False
        except Exception as e:
            print(f"focus error: {e}")
            return False


    def escreve(self, texto, selector=None, index=0, clear=False, delay_between_keys=0.01):
        """
        Escreve texto simulando teclado.
        - selector: CSS selector do elemento (ex: 'input', "div.abreInput", "input[name='pesquise']")
        - index: índice do elemento quando selector seleciona vários (padrão 0)
        - clear: se True, limpa o campo (quando possível) antes de digitar
        - delay_between_keys: intervalo entre caracteres

        Comportamentos:
        - zap.escreve('ola tudobem') -> digita no elemento atualmente focado (body.send_keys)
        - zap.escreve('ola','input') -> digita no primeiro input
        - zap.escreve('ola','input',2) -> digita no terceiro input
        - zap.escreve('ola','div.abreInput') -> foca no div (click/focus) e digita (via elemento ativo)
        """
        try:
            # caso sem selector: digita no elemento ativo (body)
            if selector is None:
                try:
                    active = self._driver.switch_to.active_element
                    # se for um input/textarea, use send_keys diretamente
                    tag = active.tag_name.lower() if active else ''
                    if active and tag in ('input', 'textarea', 'select'):
                        if clear:
                            try:
                                active.clear()
                            except Exception:
                                pass
                        for ch in str(texto):
                            active.send_keys(ch)
                            if delay_between_keys:
                                time.sleep(delay_between_keys)
                        return True
                    else:
                        # digita no body (ou elemento ativo) via Actions
                        body = self._driver.find_element(By.TAG_NAME, 'body')
                        if clear:
                            # não há clear para body
                            pass
                        for ch in str(texto):
                            body.send_keys(ch)
                            if delay_between_keys:
                                time.sleep(delay_between_keys)
                        return True
                except Exception as e:
                    print(f"escreve error (no selector): {e}")
                    return False

            # se selector informado: encontra elemento pelo selector e index
            elems = self._find(selector)
            if not elems:
                return False

            if index is None:
                index = 0
            if index < 0:
                index = 0
            if index >= len(elems):
                return False

            elem = elems[index]

            # tenta identificar se é input/textarea/select ou contenteditable
            tag = ''
            try:
                tag = elem.tag_name.lower()
            except Exception:
                pass
            contenteditable = ''
            try:
                contenteditable = elem.get_attribute('contenteditable') or ''
            except Exception:
                contenteditable = ''

            is_form_field = tag in ('input', 'textarea', 'select') or (contenteditable.lower() == 'true')

            # foca no elemento primeiro
            try:
                self.focus(selector, index)
            except Exception:
                pass

            if is_form_field:
                try:
                    if clear:
                        try:
                            elem.clear()
                        except Exception:
                            # fallback: select all + delete
                            try:
                                elem.send_keys(Keys.CONTROL + 'a')
                                elem.send_keys(Keys.DELETE)
                            except Exception:
                                pass
                    for ch in str(texto):
                        elem.send_keys(ch)
                        if delay_between_keys:
                            time.sleep(delay_between_keys)
                    return True
                except Exception as e:
                    # fallback para enviar ao elemento ativo
                    try:
                        active = self._driver.switch_to.active_element
                        for ch in str(texto):
                            active.send_keys(ch)
                            if delay_between_keys:
                                time.sleep(delay_between_keys)
                        return True
                    except Exception:
                        print(f"escreve error (form_field fallback): {e}")
                        return False
            else:
                # não é campo de formulário: focamos e enviamos para o elemento ativo
                try:
                    # after focus, active element should be the target or body — use actions to type
                    actions = ActionChains(self._driver)
                    for ch in str(texto):
                        actions.send_keys(ch)
                        actions.pause(delay_between_keys)
                    actions.perform()
                    return True
                except Exception as e:
                    # última tentativa: enviar ao body
                    try:
                        body = self._driver.find_element(By.TAG_NAME, 'body')
                        for ch in str(texto):
                            body.send_keys(ch)
                            if delay_between_keys:
                                time.sleep(delay_between_keys)
                        return True
                    except Exception:
                        print(f"escreve error (non-form fallback): {e}")
                        return False

        except Exception as e:
            print(f"escreve unexpected error: {e}")
            return False


    def _parse_key_sequence(self, tecla: str):
        """Converte strings como 'ctrl+shift+t' em uma lista de Keys ou caracteres."""
        if not tecla:
            return []
        parts = tecla.lower().split('+')
        mapping = {
            'ctrl': Keys.CONTROL,
            'control': Keys.CONTROL,
            'shift': Keys.SHIFT,
            'alt': Keys.ALT,
            'enter': Keys.ENTER,
            'tab': Keys.TAB,
            'esc': Keys.ESCAPE,
            'escape': Keys.ESCAPE,
            'backspace': Keys.BACKSPACE,
            'delete': Keys.DELETE,
            'space': Keys.SPACE,
            'arrow_up': Keys.ARROW_UP,
            'arrow_down': Keys.ARROW_DOWN,
            'arrow_left': Keys.ARROW_LEFT,
            'arrow_right': Keys.ARROW_RIGHT,
            'home': Keys.HOME,
            'end': Keys.END,
            'page_up': Keys.PAGE_UP,
            'page_down': Keys.PAGE_DOWN,
        }
        seq = []
        for p in parts:
            p = p.strip()
            if p in mapping:
                seq.append(mapping[p])
            elif len(p) == 1:
                seq.append(p)
            else:
                # suporte a teclas como 'f5'
                if p.startswith('f') and p[1:].isdigit():
                    seq.append(p.upper())
                else:
                    seq.append(p)
        return seq

    def teclado(self, tecla: str):
        """Simula tecla(s). Exemplos: 'enter','tab','ctrl+f','ctrl+shift+t','esc'"""
        seq = self._parse_key_sequence(tecla)
        if not seq:
            return False
        try:
            modifiers = [k for k in seq[:-1] if isinstance(k, Keys)]
            last = seq[-1]

            actions = ActionChains(self._driver)
            for m in modifiers:
                actions.key_down(m)
            if isinstance(last, Keys):
                actions.send_keys(last)
            else:
                actions.send_keys(str(last))
            for m in reversed(modifiers):
                actions.key_up(m)
            actions.perform()
            return True
        except Exception as e:
            print(f"teclado error: {e}")
            return False

    def attr(self, selector, nome_atributo):
        """Retorna o valor do primeiro elemento encontrado ou False se não existir"""
        elems = self._find(selector)
        if not elems:
            return False
        try:
            val = elems[0].get_attribute(nome_atributo)
            return val
        except Exception:
            return False

    def attr_array(self, selector, nome_atributo):
        """Retorna lista de valores do atributo para todos os elementos (pode retornar lista vazia)"""
        elems = self._find(selector)
        results = []
        for e in elems:
            try:
                results.append(e.get_attribute(nome_atributo))
            except Exception:
                results.append(None)
        return results

    def arquivo(self, caminho, conteudo, modo=None, encoding='utf-8'):
        """Cria/reescreve/insere arquivo.
        modo: None = overwrite, '+': prepend, '-': append
        """
        try:
            os.makedirs(os.path.dirname(caminho) or '.', exist_ok=True)
            if modo == '+':
                existing = ''
                if os.path.exists(caminho):
                    with open(caminho, 'r', encoding=encoding) as f:
                        existing = f.read()
                with open(caminho, 'w', encoding=encoding) as f:
                    f.write(str(conteudo))
                    f.write(existing)
                return True
            elif modo == '-':
                with open(caminho, 'a', encoding=encoding) as f:
                    f.write(str(conteudo))
                return True
            else:
                with open(caminho, 'w', encoding=encoding) as f:
                    f.write(str(conteudo))
                return True
        except Exception as e:
            print(f"arquivo error: {e}")
            return False

    def abre(self, caminho, encoding='utf-8'):
        """Abre e retorna o conteúdo do arquivo. Se não existir retorna False."""
        try:
            if not os.path.exists(caminho):
                return False
            with open(caminho, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            print(f"abre error: {e}")
            return False

    def get(self, texto):
        """Procura texto no body. Retorna True/False"""
        try:
            body = self._driver.find_element(By.TAG_NAME, 'body')
            return str(texto) in body.text
        except Exception:
            return False

    def loop(self, interval_seconds, func, run_now=True):
        """Executa func repetidamente a cada interval_seconds. func deve ser callable.
           Para parar, chamar zap.exit()
        """
        if not callable(func):
            raise ValueError('func deve ser callable')
        self._exit_flag = False

        def _worker():
            if run_now:
                try:
                    func()
                except Exception:
                    traceback.print_exc()
            while not self._exit_flag:
                time.sleep(interval_seconds)
                try:
                    func()
                except Exception:
                    traceback.print_exc()

        self._loop_thread = threading.Thread(target=_worker, daemon=True)
        self._loop_thread.start()
        return True

    def exit(self):
        """Sinaliza para terminar loops"""
        self._exit_flag = True
        if self._loop_thread and self._loop_thread.is_alive():
            self._loop_thread.join(timeout=1)
        return True

    def close(self):
        try:
            self._driver.close()
        except Exception:
            pass

    def quit(self):
        try:
            self._driver.quit()
        except Exception:
            pass

    # ---------------------- novas funções de sessão ----------------------
    def sessao(self, caminho_pasta):
        """
        Define/abre uma sessão (pasta) para o Chrome.
        Se a sessão já existir, ela será usada; se não, será criada.
        OBS: essa operação reinicia o driver para aplicar o user-data-dir.
        """
        try:
            if caminho_pasta is None:
                return False
            os.makedirs(caminho_pasta, exist_ok=True)
            # guarda path e reinicia driver com esse profile
            self._session_path = os.path.abspath(caminho_pasta)
            self._restart_driver_with_profile()
            return True
        except Exception as e:
            print(f"sessao error: {e}")
            return False

    def sessao_salve(self):
        """
        Garante que a sessão foi escrita no disco. O Chrome normalmente persiste automaticamente.
        Tentamos um flush básico pedindo para o navegador sincronizar (quando possível).
        """
        try:
            # uma aproximação: executar um comando simples para forçar escrita
            if not self._driver:
                return False
            try:
                # comando leve - não há garantia absoluta, mas força execução
                self._driver.execute_script('return 1;')
            except Exception:
                pass
            return True
        except Exception as e:
            print(f"sessao_salve error: {e}")
            return False

    def sessao_drop(self):
        """Apaga a pasta da sessão atual (se existir) e reinicia driver sem sessão."""
        try:
            path = self._session_path
            # encerra driver antes de remover arquivos
            try:
                if self._driver:
                    self._driver.quit()
            except Exception:
                pass
            self._driver = None
            self._actions = None
            self._session_path = None
            if path and os.path.exists(path):
                try:
                    shutil.rmtree(path)
                except Exception as e:
                    print(f"sessao_drop: não foi possível remover {path}: {e}")
                    return False
            # reinicia driver sem profile
            self._start_driver()
            return True
        except Exception as e:
            print(f"sessao_drop error: {e}")
            return False


if __name__ == '__main__':
    # Pequeno teste manual
    zap = Web(headless=False)
    zap.url('https://example.com')
    ok = zap.pause()
    print('loaded?', ok)
    print('contains Example Domain?', zap.get('Example Domain'))
    print('h1 primeiro texto:', zap.html('h1'))
    print('h1 array:', zap.html_array('h1'))
    zap.arquivo('relatorio/test.txt', 'Primeira linha\n')
    zap.arquivo('relatorio/test.txt', 'Começo\n', modo='+')
    zap.arquivo('relatorio/test.txt', 'Fim\n', modo='-')
    print('abre arquivo:', zap.abre('relatorio/test.txt'))
    zap.quit()



'''

'''
