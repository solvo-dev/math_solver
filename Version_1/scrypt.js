// Einfacher Mathe-Chatbot: Additionen und Subtraktionen
(function () {
	const chat = document.getElementById('chat');
	const form = document.getElementById('composer');
	const input = document.getElementById('userInput');
	const micBtn = document.getElementById('micBtn');
	const ttsBtn = document.getElementById('ttsBtn');

	let ttsEnabled = false;
	if (ttsBtn) {
		ttsBtn.addEventListener('click', () => {
			ttsEnabled = !ttsEnabled;
			ttsBtn.classList.toggle('is-active', ttsEnabled);
			ttsBtn.setAttribute('aria-pressed', String(ttsEnabled));
		});
	}

	// Initiale Begrüßung
	appendMessage('bot', 'Hallo! Ich kann einfache Additionen, Subtraktionen, Multiplikationen und Divisionen lösen. Frage mich z. B.: 3 + 4, 10 - 7, 6 * 5, 3 × 4, 8 / 2, 9 ÷ 3 oder "12 geteilt durch 4".');

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

		// Optional: Sprachausgabe für Bot
		if (role === 'bot' && ttsEnabled && 'speechSynthesis' in window) {
			try {
				const u = new SpeechSynthesisUtterance(text);
				u.lang = 'de-DE';
				window.speechSynthesis.cancel();
				window.speechSynthesis.speak(u);
			} catch (_) { /* ignore */ }
		}
	}

	// Spracherkennung (Diktat)
	const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
	let recognition = null;
	let listening = false;
	if (SpeechRecognition && micBtn) {
		recognition = new SpeechRecognition();
		recognition.lang = 'de-DE';
		recognition.interimResults = false;
		recognition.continuous = false;

		micBtn.addEventListener('click', () => {
			if (listening) {
				recognition.stop();
				return;
			}
			try {
				recognition.start();
				listening = true;
				micBtn.classList.add('is-active');
				micBtn.setAttribute('aria-pressed', 'true');
			} catch (_) {}
		});

		recognition.addEventListener('result', (ev) => {
			let transcript = '';
			for (let i = ev.resultIndex; i < ev.results.length; i++) {
				if (ev.results[i].isFinal) transcript += ev.results[i][0].transcript;
			}
			transcript = (transcript || '').trim();
			if (transcript) {
				input.value = transcript;
				// automatisch absenden
				if (typeof form.requestSubmit === 'function') form.requestSubmit();
				else form.dispatchEvent(new Event('submit', { cancelable: true }));
			}
		});

		recognition.addEventListener('end', () => {
			listening = false;
			micBtn.classList.remove('is-active');
			micBtn.setAttribute('aria-pressed', 'false');
		});

		recognition.addEventListener('error', () => {
			listening = false;
			micBtn.classList.remove('is-active');
			micBtn.setAttribute('aria-pressed', 'false');
		});
	} else if (micBtn) {
		micBtn.addEventListener('click', () => {
			appendMessage('bot', 'Dein Browser unterstützt Spracherkennung nicht. Nutze Chrome/Edge auf Desktop oder gib den Text ein.');
		});
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
			.replace(/\bgeteilt\s+durch\b/g, '/')
			.replace(/\bund\b/g, ' und ')
			.replace(/\bmit\b/g, ' mit ')
			.replace(/\bvon\b/g, ' von ')
			.replace(/[=\?]/g, ' ')
			.replace(/was ist|wie viel ist|berechne|rechne|bitte|\s+/g, ' ');

		// Operator-Symbole vereinheitlichen
		s = s
			.replace(/[×·]/g, '*')
			.replace(/[÷:]/g, '/')
			// Fälle wie 3x4 oder 3×4 -> 3 * 4
			.replace(/(\d)\s*[x×·]\s*(\d)/g, '$1 * $2')
			// Fälle wie 3:4 oder 3÷4 -> 3 / 4
			.replace(/(\d)\s*[/:÷]\s*(\d)/g, '$1 / $2')
			// alleinstehendes x als Operator
			.replace(/\bx\b/g, '*');

		// Dezimalkomma -> Punkt
		s = s.replace(/(\d),(\d)/g, '$1.$2');

		// Mögliche Formen:
		// 1) a + b  |  a - b  |  a * b | a / b
		let m = s.match(/(-?\d+(?:\.\d+)?)\s*([+\-*\/])\s*(-?\d+(?:\.\d+)?)/);
		if (m) {
			const a = parseFloat(m[1]);
			const op = m[2];
			const b = parseFloat(m[3]);
			let result;
			if (op === '+') result = a + b;
			else if (op === '-') result = a - b;
			else if (op === '*') result = a * b;
			else {
				if (b === 0) return { ok: false, error: 'Division durch 0 ist nicht definiert.' };
				result = a / b;
			}
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

		// 7) dividiere/teile a durch b  (a / b)
		m = s.match(/(?:dividiere|teile)\s+(-?\d+(?:\.\d+)?)\s+durch\s+(-?\d+(?:\.\d+)?)/);
		if (m) {
			const a = parseFloat(m[1]);
			const b = parseFloat(m[2]);
			if (b === 0) return { ok: false, error: 'Division durch 0 ist nicht definiert.' };
			return { ok: true, a, b, op: '/', result: a / b, usedComma };
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
