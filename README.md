# Chimera Clipboard-to-XSS Lab

**Independent, publicly documented single-developer proof of concept for studying how copied text can become active content when a destination application renders pasted input unsafely.**

Chimera is a small controlled web-security experiment built around three steps:

1. a source page intercepts a user-initiated copy event;
2. the copied text is replaced with a visible decoy followed by whitespace and an HTML fragment;
3. a deliberately vulnerable CRM simulation inserts the pasted value into `innerHTML`, allowing the fragment to become a DOM element.

The project demonstrates a specific chain:

```text
copy-event manipulation
        ->
clipboard carries an HTML-looking string as plain text
        ->
vulnerable destination stores the string in an input
        ->
destination later renders that value through innerHTML
        ->
HTML event handler executes in the destination origin
```

Chimera is **not a general active-defense system**, not a browser exploit, and not evidence that arbitrary CRM, spreadsheet, or clipboard targets are vulnerable.

The clipboard content remains inert unless the destination application places it into an executable HTML context without correct sanitization or output encoding.

## Research question

The project asks:

> Can an apparently ordinary copied value carry a hidden suffix that becomes executable only after a second application renders it through an unsafe HTML sink?

A secondary question is:

> Which traces remain after the generated DOM element removes itself?

The included files provide a purpose-built positive test case. They do not establish prevalence or effectiveness against real third-party systems.

## Current status

| Area | Current status |
|---|---|
| User-initiated `copy` interception | Implemented |
| Plain-text clipboard replacement | Implemented |
| Visible decoy plus whitespace padding | Implemented |
| Hidden HTML fragment in copied string | Implemented |
| Deliberately unsafe `innerHTML` sink | Implemented in the CRM fixture |
| Event-handler execution in the fixture | Implemented under compatible browser conditions |
| Local Flask receiver | Implemented |
| Cookie and location collection through `/exfil` | Implemented for accessible test values |
| JSON receiver through `/vacuum` | Implemented server-side but not used by the current clipboard payload |
| LocalStorage collection | Not connected to the current demo |
| Full HTML-document collection | Not connected to the current demo |
| Dual `text/plain` and `text/html` clipboard payloads | Not implemented in the current source page |
| Excel formula execution | Not implemented |
| Google Sheets execution | Not established |
| Real CRM compatibility | Not tested or claimed |
| Production readiness | Not claimed |

## Repository components

```text
Chimera/
├── README.md
├── vittima.html
├── crm_scammer_simulato.html
├── c2_server.py
└── CHIMERA_REPORT.md
```

### `vittima.html`

A source-page fixture displaying a fake one-time code.

Its JavaScript listens for a user-generated `copy` event. When the experiment switch is enabled, it prevents the default copy and places a constructed string in the `text/plain` clipboard format.

The string contains:

```text
selected text + whitespace padding + HTML-looking suffix
```

The padding provides visual displacement inside a single-line text field. It is not a security boundary or a reliable stealth mechanism.

### `crm_scammer_simulato.html`

A deliberately vulnerable destination fixture.

The pasted value first enters a normal text input, where it is inert. Execution occurs only after the user presses the save button and the page performs:

```javascript
document.getElementById("sinkArea").innerHTML =
    "Ultimo dato salvato: " + inputVal;
```

This unsafe `innerHTML` assignment is the actual injection sink.

The file also creates a synthetic session cookie for the local experiment. Browser behavior for cookies on `file://` pages is inconsistent or restricted; for a repeatable test, serve the HTML files through a local HTTP origin rather than relying on direct file URLs.

### `c2_server.py`

A Flask receiver exposing:

- `/ping` for a simple health response;
- `/exfil` for Base64-encoded cookie and location query parameters;
- `/vacuum` for arbitrary JSON fields written into `loot_dumps/`;
- `/track` for a simple source marker.

The current `vittima.html` payload calls `/exfil` only. It does not call `/vacuum` and does not collect LocalStorage or a full HTML dump.

The receiver is lab code, not a hardened service. It currently:

- binds to `0.0.0.0`;
- enables Flask debug mode;
- accepts cross-origin requests from any origin;
- has no authentication;
- performs minimal input validation;
- writes received JSON to disk;
- places selected data in console and URL-visible form.

Do not expose it to a public or shared network.

### `CHIMERA_REPORT.md`

A historical project report written during the initial experiment. It contains stronger terminology and several capabilities not present in the current source, including dual clipboard MIME handling and broader collection claims.

Treat this README and the executable code as the current description of the project.

## Negative control: safe CRM rendering

The repository now includes two destination fixtures with the same input/output IDs:

| Fixture | Rendering | Expected observation |
| --- | --- | --- |
| `crm_scammer_simulato.html` | Deliberately unsafe `innerHTML` sink | The copied HTML-like suffix can become markup under compatible browser conditions. |
| `crm_safe_simulato.html` | `textContent` sink | The same copied value remains inert, visible text. |

This paired design makes it possible to compare a positive case with a concrete safe negative control, instead of treating execution in a deliberately vulnerable fixture as sufficient evidence of a broader exploit.

The safe fixture does not collect cookies or transmit data. The included CI checks file structure, source syntax, and intended sinks **without running any browser payload or receiver**. Those static checks are not a substitute for a controlled browser compatibility matrix.

To use the fixtures manually, keep the experiment on local loopback and compare the output of both CRM pages with the same controlled sample. Do not expose `c2_server.py` to a shared network: its historical implementation binds to all interfaces and runs in debug mode.

## What actually triggers execution

The clipboard is only a carrier.

The full positive condition is:

```text
A. The source page receives a real copy event.
B. The browser permits ClipboardEvent data replacement.
C. The target receives the entire plain-text value.
D. The value is later inserted into an HTML parser context.
E. The target does not encode or sanitize the value correctly.
F. Content Security Policy and browser defenses permit the event handler.
G. The receiver URL is reachable from the target context.
```

If any condition fails, the chain can stop.

Examples:

- pasting into a text-only system does not execute HTML;
- assigning with `textContent` does not execute HTML;
- server-side HTML encoding neutralizes the fragment;
- a robust sanitizer can remove unsafe attributes or elements;
- CSP can block inline event handlers or network destinations;
- field-length limits can truncate the suffix;
- the destination may strip or normalize whitespace;
- browser clipboard behavior can differ by context and permission model.

## Data collected by the current demo

The current HTML suffix attempts to send two values to `/exfil`:

- `document.cookie`;
- `document.location` converted to text.

### Cookie boundary

`document.cookie` exposes only cookies available to JavaScript for that origin.

It does not expose:

- `HttpOnly` cookies;
- cookies belonging to another origin;
- cookies blocked by browser policy;
- server-side session data not present in the cookie value.

A successful request with an empty cookie value is still compatible with correct browser security behavior.

### Location boundary

The location identifies the page context in which the event handler ran. It does not provide geographic location.

### Source IP boundary

The Flask receiver can observe the network source address of the incoming request. This may be a loopback, proxy, NAT gateway, VPN exit, corporate egress address, or other intermediary. It does not identify a person.

## Self-removal and forensic traces

The generated image element calls `this.remove()` after its error handler runs.

This removes that DOM node. It does **not** guarantee zero traces.

Possible remaining evidence includes:

- the original clipboard content;
- the value stored in the input before rendering;
- residual text and quotation characters in the sink;
- application database records;
- browser console entries;
- network and proxy logs;
- the attempted relative request produced by the invalid image source;
- the receiver request and query string;
- browser history or developer-tool records;
- server-side access logs;
- the Flask console output;
- JSON files written by `/vacuum` when that endpoint is used.

The project is therefore useful for studying both injection and detection.

## Requirements

- Python 3;
- Flask;
- a modern browser;
- an isolated local test environment.

Install Flask:

```bash
python -m pip install flask
```

## Recommended local setup

Use one local HTTP origin for the two HTML fixtures and a separate loopback port for the Flask receiver.

For example, in the repository directory, start a static server:

```bash
python -m http.server 8000 --bind 127.0.0.1
```

In another terminal, start the receiver:

```bash
python c2_server.py
```

Then open the fixtures through the local static server rather than by double-clicking the files:

```text
http://127.0.0.1:8000/vittima.html
http://127.0.0.1:8000/crm_scammer_simulato.html
```

Before testing, verify that `C2_URL` in `vittima.html` points to:

```text
http://127.0.0.1:5000
```

This setup remains laboratory-only. The Flask server currently listens on all interfaces, so use a host firewall or change the source to bind explicitly to loopback before running on a machine connected to an untrusted network.

## Controlled demonstration

1. Start the local static server and Flask receiver.
2. Open both fixture pages through `127.0.0.1`.
3. Select the visible test code on `vittima.html`.
4. Copy it using a normal browser copy action.
5. Paste it into the CRM fixture's name field.
6. Inspect the field value before pressing save.
7. Press the save button.
8. Observe the CRM DOM, browser network panel, and Flask console.
9. Record whether a request reached `/exfil` and which values were present.
10. Repeat after replacing the vulnerable `innerHTML` assignment with `textContent`.

The final repetition is the essential negative control. The payload should remain visible or stored as text without becoming an active element.

## Expected result under the positive fixture

Under compatible conditions, the controlled fixture may demonstrate:

- the copied value differs from the visibly selected value;
- the long suffix is not immediately visible inside the text field;
- the value is inert while it remains an input value;
- pressing save passes the value to an unsafe HTML sink;
- the injected element is parsed;
- its error handler makes a request to the local receiver;
- the element removes itself afterward.

The strongest valid conclusion is:

> A copy-event handler transported a hidden plain-text suffix into a deliberately unsafe `innerHTML` sink, where it became executable DOM content in the controlled fixture.

## What the experiment does not prove

It does not prove that:

- all browsers allow the same clipboard replacement behavior;
- a real CRM uses an equivalent sink;
- a real application preserves 500 spaces;
- the suffix is invisible in every interface;
- a remote browser would reach the receiver;
- CSP, Trusted Types, sanitization, or output encoding can be bypassed;
- HttpOnly session cookies can be read;
- spreadsheets execute the payload;
- a public receiver would make Google Sheets work;
- the technique has a 95% success rate;
- the generated request identifies an operator;
- DOM removal eliminates forensic evidence.

No efficacy percentage is assigned because the repository contains one intentionally vulnerable positive fixture rather than a representative target set.

## Security controls demonstrated by the negative case

The CRM fixture can be hardened by changing the render step to:

```javascript
document.getElementById("sinkArea").textContent =
    "Ultimo dato salvato: " + inputVal;
```

Other relevant controls include:

- contextual output encoding;
- allowlist-based HTML sanitization when HTML is genuinely required;
- Content Security Policy without unsafe inline handlers;
- Trusted Types in supported applications;
- `HttpOnly`, `Secure`, and appropriate `SameSite` cookie settings;
- input length limits as a secondary control;
- logging unusually long or markup-bearing pasted values;
- avoiding storage of raw untrusted HTML;
- outbound-network restrictions from sensitive administrative applications.

Input validation alone is not a complete XSS defense; the primary control is safe handling at the output sink.

## Known limitations

- The test page and vulnerable destination are designed to fit each other.
- Only the `text/plain` clipboard format is set.
- The current source does not implement the dual-MIME technique described in the historical report.
- The `/vacuum` receiver is disconnected from the current clipboard payload.
- The demo cookie may not behave correctly when pages are opened through `file://`.
- The image `src=x` request can create a visible relative-resource error before the external fetch.
- Base64 in a URL is encoding, not confidentiality.
- Query parameters can be retained in logs and intermediary systems.
- `btoa()` can fail on non-Latin-1 strings.
- Wildcard CORS is unnecessary for some send-only patterns and unsafe as a general server default.
- Flask debug mode and `0.0.0.0` binding are inappropriate outside an isolated lab.
- Filenames based only on second-resolution timestamps and source IP can collide.
- `/vacuum` accepts arbitrary JSON without size limits or schema validation.
- The current test suite is manual.
- No browser or sanitizer compatibility matrix is included.

## Intended use

Chimera is intended for:

- private web-security research;
- controlled clipboard-behavior experiments;
- XSS training with deliberately vulnerable fixtures;
- testing safe rendering and sanitization controls;
- studying the forensic traces left by self-removing DOM payloads.

It is not intended for deployment against people, third-party applications, real administrative systems, or any browser context without explicit ownership and authorization.

## Development direction

Useful next steps include:

- adding a safe and vulnerable CRM mode side by side;
- serving all fixtures through a reproducible local harness;
- adding Playwright tests for supported browsers;
- recording the exact clipboard MIME contents;
- validating that the payload remains inert in `textContent`, textarea, and server-encoded outputs;
- adding CSP and sanitizer test matrices;
- removing debug mode and wildcard CORS from the default receiver;
- binding the receiver to loopback by default;
- adding request-size limits and a typed schema;
- separating collection endpoints from the basic proof of execution;
- replacing success language with observable assertions;
- adding negative tests for HttpOnly cookies and truncated fields.

## License

See the repository license, when present, for the current terms of use.
