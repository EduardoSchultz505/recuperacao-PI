const API_URL = "http://127.0.0.1:5000/pets";

async function loadPets() {
  const res = await fetch(API_URL);
  const pets = await res.json();
  const ul = document.getElementById("pet-list");

  ul.innerHTML = pets.map(p => `
    <li>
      <img src="${p.foto ? `http://127.0.0.1:5000/uploads/${p.foto}` : 'https://via.placeholder.com/60?text=Sem+Foto'}" alt="${p.nome}" onclick="window.location.href='pet_view.html?id=${p.id}'" style="cursor:pointer;">
      <span onclick="window.location.href='pet_view.html?id=${p.id}'" style="cursor:pointer;">${p.nome}</span>
      <button class="delete-btn" onclick="deletePet(event, ${p.id})" title="Deletar Pet">🗑️</button>
    </li>
  `).join('');
}

async function deletePet(event, id) {
  event.stopPropagation(); // evita que o click do botão dispare o onclick do li
  if (confirm("Deseja deletar este pet?")) {
    try {
      const res = await fetch(`${API_URL}/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Erro ao deletar o pet.");
      alert("Pet deletado com sucesso!");
      loadPets();  // Recarrega a lista
    } catch (err) {
      alert(err.message);
    }
  }
}


document.getElementById('add-pet-btn').onclick = () => {
  window.location.href = 'add_pet.html';
};
