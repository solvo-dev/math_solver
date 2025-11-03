// Einfacher Mathe-Chatbot: Additionen und Subtraktionen
(function () {
	const chat = document.getElementById('chat');
	const form = document.getElementById('composer');
	const input = document.getElementById('userInput');

	// Initiale Begrüßung
	appendMessage('bot', 'Hallo! Ich kann einfache Additionen, Subtraktionen und Multiplikationen lösen. Frage mich z. B.: 3 + 4, 10 - 7, 6 * 5, 3 × 4 oder "5 mal 8".');

	form.addEventListener('submit', (e) => {
		e.preventDefault();
		const text = (input.value || '').trim();
		if (!text) return;

		appendMessage('user', text);

		const res = solve(text);
		if (res.ok) {
			const { a, b, op, result, usedComma } = res;
			const fmt = (n) => formatNumber(n, usedComma);
			appendMessage('bot', `${fmt(a)} ${op} ${fmt(b)} = ${fmt(result)}`);
		} else {
			appendMessage('bot', res.error + ' Tipp: Versuche z. B. "3 + 4" oder "10 minus 7".');
		}

		input.value = '';
		input.focus();
	});

	function appendMessage(role, text) {
		const wrap = document.createElement('div');
		wrap.className = `msg msg--${role}`;

		const avatar = document.createElement('div');
		avatar.className = 'msg__avatar';
		avatar.textContent = role === 'user' ? 'DU' : 'BOT';

		const bubble = document.createElement('div');
		bubble.className = 'msg__bubble';
		bubble.textContent = text;

		wrap.appendChild(avatar);
		wrap.appendChild(bubble);
		chat.appendChild(wrap);
		chat.scrollTop = chat.scrollHeight;
	}

	function solve(text) {
		// Merke, ob Benutzer Dezimalkomma benutzt hat
		const usedComma = /\d,\d/.test(text);

		// Normalisieren
		let s = ' ' + text.toLowerCase() + ' ';
		// Standardisiere Wörter auf Operatoren
		s = s
			.replace(/[–—]/g, '-') // En/Em-Dash
			// Schlüsselwörter
			.replace(/\bplus\b/g, '+')
			.replace(/\bminus\b/g, '-')
			.replace(/\bmal\b/g, '*')
			.replace(/\bund\b/g, ' und ')
			.replace(/\bmit\b/g, ' mit ')
			.replace(/\bvon\b/g, ' von ')
			.replace(/[=\?]/g, ' ')
			.replace(/was ist|wie viel ist|berechne|rechne|bitte|\s+/g, ' ');

		// Multiplikationssymbole vereinheitlichen
		s = s
			.replace(/[×·]/g, '*')
			// Fälle wie 3x4 oder 3×4 -> 3 * 4
			.replace(/(\d)\s*[x×·]\s*(\d)/g, '$1 * $2')
			// alleinstehendes x als Operator
			.replace(/\bx\b/g, '*');

		// Dezimalkomma -> Punkt
		s = s.replace(/(\d),(\d)/g, '$1.$2');

		// Mögliche Formen:
		// 1) a + b  |  a - b  |  a * b
		let m = s.match(/(-?\d+(?:\.\d+)?)\s*([+\-*])\s*(-?\d+(?:\.\d+)?)/);
		if (m) {
			const a = parseFloat(m[1]);
			const op = m[2];
			const b = parseFloat(m[3]);
			let result;
			if (op === '+') result = a + b;
			else if (op === '-') result = a - b;
			else result = a * b;
			return { ok: true, a, b, op, result, usedComma };
		}

		// 2) addiere a und b
		m = s.match(/addiere\s+(-?\d+(?:\.\d+)?)\s+und\s+(-?\d+(?:\.\d+)?)/);
		if (m) {
			const a = parseFloat(m[1]);
			const b = parseFloat(m[2]);
			return { ok: true, a, b, op: '+', result: a + b, usedComma };
		}

		// 3) subtrahiere a und b  (interpretation: a - b)
		m = s.match(/subtrahiere\s+(-?\d+(?:\.\d+)?)\s+und\s+(-?\d+(?:\.\d+)?)/);
		if (m) {
			const a = parseFloat(m[1]);
			const b = parseFloat(m[2]);
			return { ok: true, a, b, op: '-', result: a - b, usedComma };
		}

		// 4) subtrahiere b von a  (a - b)
		m = s.match(/subtrahiere\s+(-?\d+(?:\.\d+)?)\s+von\s+(-?\d+(?:\.\d+)?)/);
		if (m) {
			const b = parseFloat(m[1]);
			const a = parseFloat(m[2]);
			return { ok: true, a, b, op: '-', result: a - b, usedComma };
		}

		// 5) multipliziere a und/mit b  (a * b)
		m = s.match(/multipliziere\s+(-?\d+(?:\.\d+)?)\s+(?:und|mit)\s+(-?\d+(?:\.\d+)?)/);
		if (m) {
			const a = parseFloat(m[1]);
			const b = parseFloat(m[2]);
			return { ok: true, a, b, op: '*', result: a * b, usedComma };
		}

		// 6) produkt aus a und b  (a * b)
		m = s.match(/produkt\s+aus\s+(-?\d+(?:\.\d+)?)\s+und\s+(-?\d+(?:\.\d+)?)/);
		if (m) {
			const a = parseFloat(m[1]);
			const b = parseFloat(m[2]);
			return { ok: true, a, b, op: '*', result: a * b, usedComma };
		}

		return { ok: false, error: 'Ich konnte deine Aufgabe nicht erkennen.' };
	}

	function formatNumber(n, preferComma) {
		// Runde leicht, um 0.30000000004 & Co. zu vermeiden
		const rounded = Math.round((n + Number.EPSILON) * 1e10) / 1e10;
		let s = String(rounded);
		// Entferne trailing .0
		if (s.includes('.')) {
			s = s.replace(/\.0+$/, '');
			s = s.replace(/(\.[0-9]*?)0+$/, '$1');
		}
		return preferComma ? s.replace('.', ',') : s;
	}
})();
