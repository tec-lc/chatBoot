<?php
/**
 * offEnd - executar e monitorar scripts python em segundo plano (Linux / Windows)
 *
 * Uso:
 * $exe = new offEnd('windows', 'C:\\caminho\\python.py');
 * echo $exe->start();
 *
 * $exe = new offEnd('windows', 'C:\\caminho\\python.py');
 * echo $exe->status();
 *
 * $exe = new offEnd('windows', 'C:\\caminho\\python.py');
 * echo $exe->close();
 */

class offEnd {
    protected $platform; // 'windows' ou 'linux'
    protected $script;   // caminho para o script python
    protected $metaFile; // arquivo JSON para salvar pid/log
    protected $logFile;

    public function __construct(string $platform, string $script) {
        $this->platform = strtolower($platform) === 'windows' ? 'windows' : 'linux';
        $this->script = $this->normalizeScriptPath($script);
        $this->logFile = $this->makeLogPath();
        $this->metaFile = $this->makeMetaPath();
    }

    /** inicia em segundo plano, salva meta (pid,log) e retorna a primeira saída (se houver) */
    public function start(): string {
        // Se já existe e está rodando, retorna aviso
        $meta = $this->readMeta();
        if ($meta && isset($meta['pid']) && $this->isRunning((int)$meta['pid'])) {
            return "already running (pid={$meta['pid']}).";
        }

        // garante diretórios
        $this->ensureDir(dirname($this->logFile));

        // comando por plataforma
        if ($this->platform === 'linux') {
            // usa nohup e retorna PID
            $python = $this->whichPythonLinux();
            $cmd = sprintf(
                "nohup %s %s > %s 2>&1 & echo $!",
                escapeshellcmd($python),
                escapeshellarg($this->script),
                escapeshellarg($this->logFile)
            );
            $pid = $this->execAndCapture($cmd);
            $pid = is_numeric($pid) ? (int)trim($pid) : null;
        } else {
            // Windows: tenta powershell Start-Process -PassThru para pegar PID
            // fallback: start /B (não retorna PID)
            $psCmd = sprintf(
                "powershell -NoProfile -Command \"(Start-Process -FilePath 'python' -ArgumentList '%s' -PassThru).Id\"",
                $this->escapeForPowerShell($this->script)
            );
            $pid = $this->execAndCapture($psCmd);
            if (!is_numeric(trim($pid))) {
                // fallback: start /B and não temos PID (tentaremos descobrir depois)
                $startCmd = sprintf("start /B python %s", $this->escapeShellArgWindows($this->script));
                pclose(popen($startCmd, "r"));
                $pid = null;
            } else {
                $pid = (int)trim($pid);
            }
            // redirecionamento de output para logfile (powershell Start-Process não redireciona facilmente),
            // então vamos rodar um segundo command para forçar redirecionamento se possível (mais confiável no Linux).
            // Como fallback, o script Python pode fazer seu próprio log.
        }

        // salva meta (pid pode ser null)
        $meta = [
            'pid' => $pid,
            'platform' => $this->platform,
            'script' => $this->script,
            'log' => $this->logFile,
            'started_at' => date('c')
        ];
        $this->writeMeta($meta);

        // Espera rápido por saída (até 3s) para obter a primeira linha
        $first = $this->waitForFirstLogLine(3);
        if ($first === null) {
            return "started (pid=" . ($pid ?? 'unknown') . "), no immediate output yet.";
        }
        return $first;
    }

    /** retorna status e última saída */
    public function status(): string {
        $meta = $this->readMeta();
        if (!$meta) return "no process metadata found.";

        $pid = isset($meta['pid']) ? (int)$meta['pid'] : null;
        $running = $pid ? $this->isRunning($pid) : $this->guessRunningByLog($meta['log']);

        $last = $this->tailFile($meta['log'], 5);
        $out = "script: {$meta['script']}\nplatform: {$meta['platform']}\n";
        $out .= "pid: " . ($pid ?? 'unknown') . "\n";
        $out .= "running: " . ($running ? 'yes' : 'no') . "\n";
        $out .= "last log lines:\n" . ($last ?: "(empty log)");
        return $out;
    }

    /** finaliza o processo (se estiver aberto) */
    public function close(): string {
        $meta = $this->readMeta();
        if (!$meta) return "no process metadata found.";

        $pid = isset($meta['pid']) ? (int)$meta['pid'] : null;
        $errors = [];

        if ($pid && $this->isRunning($pid)) {
            if ($this->platform === 'linux') {
                // tenta posix_kill se disponível
                if (function_exists('posix_kill')) {
                    @posix_kill($pid, SIGTERM);
                    usleep(200000);
                    if ($this->isRunning($pid)) {
                        @posix_kill($pid, SIGKILL);
                    }
                } else {
                    exec(sprintf("kill -TERM %d >/dev/null 2>&1", $pid));
                    usleep(200000);
                    if ($this->isRunning($pid)) {
                        exec(sprintf("kill -KILL %d >/dev/null 2>&1", $pid));
                    }
                }
                if ($this->isRunning($pid)) $errors[] = "could not kill pid $pid";
            } else {
                // Windows
                exec(sprintf("taskkill /F /PID %d 2>&1", $pid), $out, $rc);
                if ($rc !== 0) $errors[] = "taskkill returned: " . implode("\n", $out);
            }
        } else {
            // Se não temos PID, tentamos encontrar processos que contenham o nome do script (opcional e arriscado)
            $found = $this->findProcessesByScriptName(basename($meta['script']));
            if (!empty($found)) {
                foreach ($found as $p) {
                    if ($this->platform === 'linux') exec("kill -TERM {$p} >/dev/null 2>&1");
                    else exec("taskkill /F /PID {$p} 2>&1");
                }
                usleep(200000);
            } else {
                // nada a finalizar
            }
        }

        // limpa meta (remover pid)
        if (file_exists($this->metaFile)) @unlink($this->metaFile);

        if (!empty($errors)) {
            return "close attempted but errors: " . implode(" | ", $errors);
        }
        return "closed";
    }

    /* ---------------- helper methods ---------------- */

    protected function normalizeScriptPath(string $s): string {
        // se for relativo tenta transformar em absoluto (com base no cwd)
        if (strpos($s, DIRECTORY_SEPARATOR) === false && !preg_match('#^[A-Za-z]:#', $s)) {
            return getcwd() . DIRECTORY_SEPARATOR . $s;
        }
        return $s;
    }

    protected function makeLogPath(): string {
        $tmp = sys_get_temp_dir();
        $name = 'offend_log_' . $this->sanitizeForFilename($this->script) . '.log';
        return $tmp . DIRECTORY_SEPARATOR . $name;
    }

    protected function makeMetaPath(): string {
        $tmp = sys_get_temp_dir();
        $name = 'offend_meta_' . $this->sanitizeForFilename($this->script) . '.json';
        return $tmp . DIRECTORY_SEPARATOR . $name;
    }

    protected function sanitizeForFilename(string $s): string {
        $s = str_replace(['/', '\\', ' ', ':'], '_', $s);
        return preg_replace('/[^A-Za-z0-9_\-\.]/', '', $s);
    }

    protected function ensureDir(string $dir) {
        if (!is_dir($dir)) @mkdir($dir, 0777, true);
    }

    protected function writeMeta(array $meta) {
        @file_put_contents($this->metaFile, json_encode($meta));
    }

    protected function readMeta(): ?array {
        if (!file_exists($this->metaFile)) return null;
        $c = @file_get_contents($this->metaFile);
        if (!$c) return null;
        $j = json_decode($c, true);
        return is_array($j) ? $j : null;
    }

    protected function isRunning(int $pid): bool {
        if ($pid <= 0) return false;
        if (strtolower(PHP_OS_FAMILY) === 'windows' || $this->platform === 'windows') {
            // Windows: use tasklist
            exec("tasklist /FI \"PID eq {$pid}\" /NH", $out);
            if (empty($out)) return false;
            $line = trim(implode("\n", $out));
            return stripos($line, (string)$pid) !== false;
        } else {
            // Linux/Unix: posix_kill 0 check or kill -0
            if (function_exists('posix_kill')) {
                return @posix_kill($pid, 0);
            } else {
                exec(sprintf("kill -0 %d 2>&1", $pid), $o, $rc);
                return $rc === 0;
            }
        }
    }

    protected function execAndCapture(string $cmd) {
        // executa comando e retorna stdout (trim)
        $out = null;
        $last = [];
        exec($cmd, $last, $rc);
        if (!empty($last)) $out = implode("\n", $last);
        return $out;
    }

    protected function waitForFirstLogLine(int $timeoutSeconds = 3): ?string {
        $start = time();
        while (time() - $start < $timeoutSeconds) {
            if (file_exists($this->logFile) && filesize($this->logFile) > 0) {
                $f = fopen($this->logFile, 'r');
                if ($f) {
                    $line = fgets($f);
                    fclose($f);
                    if ($line !== false) return trim($line);
                }
            }
            usleep(200000); // 200ms
        }
        return null;
    }

    protected function tailFile(string $file, int $lines = 1): ?string {
        if (!file_exists($file)) return null;
        // método simples: ler todo e pegar últimas linhas (adequado para logs pequenos)
        $content = @file_get_contents($file);
        if ($content === false || $content === '') return null;
        $arr = preg_split("/\r\n|\n|\r/", trim($content));
        $last = array_slice($arr, -$lines);
        return implode("\n", $last);
    }

    protected function guessRunningByLog(string $logfile): bool {
        // heurística: if logfile modified in last 10s -> probably running
        if (!file_exists($logfile)) return false;
        return (time() - filemtime($logfile)) < 10;
    }

    protected function findProcessesByScriptName(string $name): array {
        $pids = [];
        if ($this->platform === 'windows') {
            exec("wmic process where \"CommandLine like '%$name%'\" get ProcessId 2>NUL", $out);
            foreach ($out as $line) {
                $line = trim($line);
                if (is_numeric($line)) $pids[] = (int)$line;
            }
        } else {
            exec("pgrep -f " . escapeshellarg($name), $out);
            foreach ($out as $l) if (is_numeric(trim($l))) $pids[] = (int)trim($l);
        }
        return $pids;
    }

    protected function whichPythonLinux(): string {
        // tenta python3, python
        $bins = ['python3', 'python'];
        foreach ($bins as $b) {
            $path = trim(shell_exec("which " . escapeshellcmd($b) . " 2>/dev/null"));
            if ($path) return $path;
        }
        // fallback
        return 'python3';
    }

    /* Helpers Windows escaping */
    protected function escapeForPowerShell(string $s): string {
        // simples: duplica ' para uso em single-quoted PS string
        return str_replace("'", "''", $s);
    }
    protected function escapeShellArgWindows(string $s): string {
        // basic escape for start /B usage
        return '"' . str_replace('"', '\"', $s) . '"';
    }
}
?>
