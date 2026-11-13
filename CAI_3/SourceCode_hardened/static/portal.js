// FIX: script externo (no inline) para ser compatible con la cabecera
// Content-Security-Policy: default-src 'self' (CODE-07) sin necesitar
// 'unsafe-inline'. La logica es la misma que en el proyecto original.

async function probarAPI(url, metodo) {
    const res = await fetch(url, { method: metodo });
    const texto = await res.text();
    document.getElementById('resultado').textContent = `HTTP ${res.status} ${res.statusText}\n${texto}`;
}

async function modificarHistorial() {
    const diagnostico = document.getElementById('nuevo-diagnostico').value;
    const res = await fetch('/api/historial', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ diagnostico: diagnostico })
    });
    const texto = await res.text();
    document.getElementById('resultado').textContent = `HTTP ${res.status} ${res.statusText}\n${texto}`;
}

function verCookiesJS() {
    // FIX RT-05: con httponly=True, access_token YA NO aparece aqui.
    document.getElementById('resultado').textContent =
        `document.cookie accesible por JS:\n${document.cookie || '(Vacío - el access_token ya no es legible por JavaScript)'}`;
}

document.addEventListener('DOMContentLoaded', () => {
    const host = window.location.hostname;
    const linkMfa = document.getElementById('link-mfa');
    if (linkMfa) linkMfa.href = `http://${host}:8000/setup-mfa`;

    document.getElementById('btn-leer').addEventListener('click', () => probarAPI('/api/historial', 'GET'));
    document.getElementById('btn-modificar').addEventListener('click', modificarHistorial);
    document.getElementById('btn-cookies').addEventListener('click', verCookiesJS);
});
