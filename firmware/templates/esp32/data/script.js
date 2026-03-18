async function toggleLED() {
  const res = await fetch('/led/toggle');
  const state = await res.text();
  document.querySelector('button').textContent = 'LED: ' + state;
}

async function loadInfo() {
  const res = await fetch('/api/info');
  const data = await res.json();
  document.getElementById('info').innerHTML =
    `<strong>IP:</strong> ${data.ip} | <strong>SSID:</strong> ${data.ssid} | <strong>RSSI:</strong> ${data.rssi} dBm`;
}

window.addEventListener('load', loadInfo);
