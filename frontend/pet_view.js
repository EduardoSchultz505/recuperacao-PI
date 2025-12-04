const API_URL = 'http://127.0.0.1:5000/pets';
const params = new URLSearchParams(window.location.search);
const petId = params.get('id');

const petFoto = document.getElementById('pet-foto');
const petNome = document.getElementById('pet-nome');
const petRaca = document.getElementById('pet-raca');
const petGenero = document.getElementById('pet-genero');
const petIdade = document.getElementById('pet-idade');
const petCor = document.getElementById('pet-cor');

const configBtn = document.getElementById('config-btn');
const editSection = document.getElementById('edit-section');
const editForm = document.getElementById('edit-pet-form');
const cancelBtn = document.getElementById('cancel-btn');

const eventForm = document.getElementById('event-form');
const eventList = document.getElementById('event-list');
const vacinaList = document.getElementById('vacina-list');
const vermifugoList = document.getElementById('vermifugo-list');

const nomeEventoSelect = document.getElementById('nome-evento');
const nomeOutroInput = document.getElementById('nome-outro');

const VACINA_INTERVALOS = { "V10": 365, "V8": 365, "Raiva": 365, "Antirrábica": 365, "Polivalente": 365, "Leucemia Felina": 365 };
const VERMIFUGO_INTERVALO = 90; // dias

function formatarDataDMA(iso) {
    const [y, m, d] = iso.split("-").map(Number);
    return `${String(d).padStart(2, "0")}/${String(m).padStart(2, "0")}/${y}`;
}

function adicionarDias(dataISO, dias) {
    const [y, m, d] = dataISO.split("-").map(Number);
    const data = new Date(y, m - 1, d);
    data.setDate(data.getDate() + dias);
    return `${data.getFullYear()}-${String(data.getMonth() + 1).padStart(2, "0")}-${String(data.getDate()).padStart(2, "0")}`;
}

function statusData(event) {
    const proximaISO = event.proximaDose || event.data;
    const [y, m, d] = proximaISO.split("-").map(Number);
    const proxima = new Date(y, m - 1, d);
    const hoje = new Date();
    const hojeZero = new Date(hoje.getFullYear(), hoje.getMonth(), hoje.getDate());
    const diff = Math.floor((proxima - hojeZero) / (1000 * 60 * 60 * 24));
    if (diff < 0) return "🔴 Atrasada";
    if (diff <= 7) return "🟡 Vence em breve";
    return "🟢 Em dia";
}

async function loadPet() {
    try {
        const res = await fetch(`${API_URL}/${petId}`);
        if (!res.ok) throw new Error('Pet não encontrado.');
        const pet = await res.json();

        petFoto.src = pet.foto ? `${API_URL.replace('/pets', '')}/uploads/${pet.foto}` : './assets/no-image.webp';
        petNome.textContent = pet.nome;
        petRaca.textContent = pet.raca || '-';
        petGenero.textContent = pet.genero || '-';
        petIdade.textContent = pet.idade || '-';
        petCor.textContent = pet.cor || '-';

        editForm.nome.value = pet.nome;
        editForm.idade.value = pet.idade;
        editForm.genero.value = pet.genero;
        editForm.raca.value = pet.raca;
        editForm.cor.value = pet.cor;
    } catch (err) {
        alert(err.message);
    }
}

async function loadEvents() {
    const res = await fetch(`${API_URL}/${petId}/events`);
    const events = await res.json();

    vacinaList.innerHTML = "";
    vermifugoList.innerHTML = "";
    const eventosComuns = [];

    events.forEach(e => {
        if (VACINA_INTERVALOS[e.nome]) {
            const proximaDose = e.proximaDose || adicionarDias(e.data, VACINA_INTERVALOS[e.nome]);
            e.proximaDose = proximaDose;
            const item = document.createElement("li");
            item.innerHTML = `<b>${e.nome}</b> - ${formatarDataDMA(e.data)}<br>Próxima dose: ${formatarDataDMA(proximaDose)}<br>${statusData(e)}`;
            vacinaList.appendChild(item);
        } else if (e.nome.toLowerCase() === "vermifugo") {
            const proximaDose = e.proximaDose || adicionarDias(e.data, VERMIFUGO_INTERVALO);
            e.proximaDose = proximaDose;
            const item = document.createElement("li");
            item.innerHTML = `<b>Vermífugo</b> - ${formatarDataDMA(e.data)}<br>Próxima dose: ${formatarDataDMA(proximaDose)}<br>${statusData(e)}`;
            vermifugoList.appendChild(item);
        } else {
            eventosComuns.push(e);
        }
    });

    eventList.innerHTML = eventosComuns.map(e => `
        <li>
          <b>${e.nome}</b> - ${formatarDataDMA(e.data)}<br>
          ${e.descricao || ''}<br>
          <button class="delete-event" data-id="${e.id}">Excluir</button>
        </li>
      `).join('');

    document.querySelectorAll('.delete-event').forEach(btn => {
        btn.addEventListener('click', async () => {
            const eventId = btn.dataset.id;
            if (confirm('Deseja deletar este evento?')) {
                await fetch(`http://127.0.0.1:5000/events/${eventId}`, { method: 'DELETE' });
                loadEvents();
            }
        });
    });
}

configBtn.addEventListener('click', () => {
    editSection.classList.toggle('hidden');
});

cancelBtn.addEventListener('click', () => {
    editSection.classList.add('hidden');
});

editForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(editForm);

    try {
        const res = await fetch(`${API_URL}/${petId}`, {
            method: 'PUT',
            body: formData
        });
        if (!res.ok) throw new Error('Erro ao atualizar pet.');

        alert('Pet atualizado com sucesso!');
        editSection.classList.add('hidden');
        loadPet();
    } catch (err) {
        alert(err.message);
    }
});

nomeEventoSelect.addEventListener('change', () => {
    if (nomeEventoSelect.value === "Outro") {
        nomeOutroInput.classList.remove('hidden');
    } else {
        nomeOutroInput.classList.add('hidden');
        nomeOutroInput.value = '';
    }
});

eventForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    let nome = nomeEventoSelect.value;
    if (nome === "Outro") {
        nome = nomeOutroInput.value.trim();
        if (!nome) {
            alert('Digite o nome do evento.');
            return;
        }
    }

    const data = eventForm.data.value;
    const descricao = eventForm.descricao.value;

    if (!data) {
        alert('Data do evento é obrigatória!');
        return;
    }

    let proximaDose = null;
    if (VACINA_INTERVALOS[nome]) {
        proximaDose = adicionarDias(data, VACINA_INTERVALOS[nome]);
    } else if (nome.toLowerCase() === "vermifugo") {
        proximaDose = adicionarDias(data, VERMIFUGO_INTERVALO);
    }

    const formData = { nome, data, descricao, proximaDose };

    try {
        const res = await fetch(`${API_URL}/${petId}/events`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        if (!res.ok) throw new Error('Erro ao criar evento.');

        eventForm.reset();
        nomeOutroInput.classList.add('hidden');
        loadEvents();
    } catch (err) {
        alert(err.message);
    }
});

loadPet();
loadEvents();